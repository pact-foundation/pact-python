"""
Provider utilities for compatibility suite tests.

This file has two main purposes.

The first functionality provided by this module is the ability to start a
provider application with a set of interactions. Since this is done in a
subprocess, any configuration must be passed in through files. The process is
started with

The second functionality provided by this module is to define some of the shared
steps for the compatibility suite tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))


import contextlib
import copy
import json
import logging
import os
import pickle
import re
import shutil
import signal
import socket
import subprocess
import time
import warnings
from contextvars import ContextVar
from datetime import datetime
from threading import Thread
from typing import TYPE_CHECKING, Any, NoReturn

import flask
import requests
from flask import request
from pytest_bdd import given, parsers, then, when
from yarl import URL

import pact.constants  # type: ignore[import-untyped]
from pact.v3.pact import Pact
from tests.v3.compatibility_suite.util import (
    InteractionDefinition,
    parse_headers,
    parse_markdown_table,
    serialize,
)

if TYPE_CHECKING:
    from collections.abc import Generator

    from pact.v3.verifier import Verifier

if sys.version_info < (3, 11):
    from datetime import timezone

    UTC = timezone.utc
else:
    from datetime import UTC


logger = logging.getLogger(__name__)

version_var = ContextVar("version_var", default="0")
"""
Shared context variable to store the version of the consumer application.

This is used to generate a new version for the consumer application to use when
publishing the interactions to the Pact Broker.
"""
reset_broker_var = ContextVar("reset_broker", default=True)
"""
This context variable is used to determine whether the Pact broker should be
cleaned up. It is used to ensure that the broker is only cleaned up once, even
if a step is run multiple times.

All scenarios which make use of the Pact broker should set this to `True` at the
start of the scenario.
"""


def next_version() -> str:
    """
    Get the next version for the consumer.

    This is used to generate a new version for the consumer application to use
    when publishing the interactions to the Pact Broker.

    Returns:
        The next version.
    """
    version = version_var.get()
    version_var.set(str(int(version) + 1))
    return version


def _find_free_port() -> int:
    """
    Find a free port.

    This is used to find a free port to host the API on when running locally. It
    is allocated, and then released immediately so that it can be used by the
    API.

    Returns:
        The port number.
    """
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


class Provider:
    """
    HTTP Provider.
    """

    def __init__(self, provider_dir: Path | str) -> None:
        """
        Instantiate a new provider.

        Args:
            provider_dir:
                The directory containing various files used to configure the
                provider. At a minimum, this directory must contain a file
                called `interactions.pkl`. This file must contain a list of
                [`InteractionDefinition`] objects.
        """
        self.provider_dir = Path(provider_dir)
        if not self.provider_dir.is_dir():
            msg = f"Directory {self.provider_dir} does not exist"
            raise ValueError(msg)

        self.app: flask.Flask = flask.Flask("provider")
        self._add_ping(self.app)
        self._add_callback(self.app)
        self._add_after_request(self.app)
        self._add_interactions(self.app)

    def _add_ping(self, app: flask.Flask) -> None:
        """
        Add a ping endpoint to the provider.

        This is used to check that the provider is running.
        """

        @app.get("/_test/ping")
        def ping() -> str:
            """Simple ping endpoint for testing."""
            return "pong"

    def _add_callback(self, app: flask.Flask) -> None:
        """
        Add a callback endpoint to the provider.

        This is used to receive any callbacks from Pact to configure any
        internal state (e.g., "given a user exists"). As far as the testing
        is concerned, this is just a simple endpoint that records the request
        and returns an empty response.

        If the provider directory contains a file called `fail_callback`, then
        the callback will return a 404 response.

        If the provider directory contains a file called `provider_state`, then
        the callback will check that the `state` query parameter matches the
        contents of the file.
        """

        @app.route("/_test/callback", methods=["GET", "POST"])
        def callback() -> tuple[str, int] | str:
            if (self.provider_dir / "fail_callback").exists():
                return "Provider state not found", 404

            provider_states_path = self.provider_dir / "provider_states"
            if provider_states_path.exists():
                with provider_states_path.open() as f:
                    states = [InteractionDefinition.State(**s) for s in json.load(f)]
                for state in states:
                    if request.args["state"] == state.name:
                        for k, v in state.parameters.items():
                            assert k in request.args
                            assert str(request.args[k]) == str(v)
                        break
                else:
                    msg = "State not found"
                    raise ValueError(msg)

            json_file = (
                self.provider_dir
                / f"callback.{datetime.now(tz=UTC).strftime('%H:%M:%S.%f')}.json"
            )
            with json_file.open("w") as f:
                json.dump(
                    {
                        "method": request.method,
                        "path": request.path,
                        "query_string": request.query_string.decode("utf-8"),
                        "query_params": serialize(request.args),
                        "headers_list": serialize(request.headers),
                        "headers_dict": serialize(dict(request.headers)),
                        "body": request.data.decode("utf-8"),
                        "form": serialize(request.form),
                    },
                    f,
                )

            return ""

    def _add_after_request(self, app: flask.Flask) -> None:
        """
        Add a handler to log requests and responses.

        This is used to log the requests and responses to the provider
        application (both to the logger as well as to files).
        """

        @app.after_request
        def log_request(response: flask.Response) -> flask.Response:
            sys.stderr.write(f"START REQUEST: {request.method} {request.path}\n")
            sys.stderr.write(f"Query string: {request.query_string.decode('utf-8')}\n")
            sys.stderr.write(f"Header: {serialize(request.headers)}\n")
            sys.stderr.write(f"Body: {request.data.decode('utf-8')}\n")
            sys.stderr.write(f"Form: {serialize(request.form)}\n")
            sys.stderr.write("END REQUEST\n")

            with (
                self.provider_dir
                / f"request.{datetime.now(tz=UTC).strftime('%H:%M:%S.%f')}.json"
            ).open("w") as f:
                json.dump(
                    {
                        "method": request.method,
                        "path": request.path,
                        "query_string": request.query_string.decode("utf-8"),
                        "query_params": serialize(request.args),
                        "headers_list": serialize(request.headers),
                        "headers_dict": serialize(dict(request.headers)),
                        "body": request.data.decode("utf-8"),
                        "form": serialize(request.form),
                    },
                    f,
                )
            return response

        @app.after_request
        def log_response(response: flask.Response) -> flask.Response:
            sys.stderr.write(f"START RESPONSE: {response.status_code}\n")
            sys.stderr.write(f"Headers: {serialize(response.headers)}\n")
            sys.stderr.write(
                f"Body: {response.get_data().decode('utf-8', errors='replace')}\n"
            )
            sys.stderr.write("END RESPONSE\n")

            with (
                self.provider_dir
                / f"response.{datetime.now(tz=UTC).strftime('%H:%M:%S.%f')}.json"
            ).open("w") as f:
                json.dump(
                    {
                        "status_code": response.status_code,
                        "headers_list": serialize(response.headers),
                        "headers_dict": serialize(dict(response.headers)),
                        "body": response.get_data().decode("utf-8", errors="replace"),
                    },
                    f,
                )
            return response

    def _add_interactions(self, app: flask.Flask) -> None:
        """
        Add the interactions to the provider.
        """
        with (self.provider_dir / "interactions.pkl").open("rb") as f:
            interactions: list[InteractionDefinition] = pickle.load(f)  # noqa: S301

        for interaction in interactions:
            interaction.add_to_flask(app)

    def run(self) -> None:
        """
        Start the provider.
        """
        url = URL(f"http://localhost:{_find_free_port()}")
        sys.stderr.write(f"Starting provider on {url}\n")
        for endpoint in self.app.url_map.iter_rules():
            sys.stderr.write(f"  * {endpoint}\n")

        self.app.run(
            host=url.host,
            port=url.port,
            debug=True,
        )


class PactBroker:
    """
    Interface to the Pact Broker.
    """

    def __init__(  # noqa: PLR0913
        self,
        broker_url: URL,
        *,
        username: str | None = None,
        password: str | None = None,
        provider: str = "provider",
        consumer: str = "consumer",
    ) -> None:
        """
        Instantiate a new Pact Broker interface.
        """
        self.url = broker_url
        self.username = broker_url.user or username
        self.password = broker_url.password or password
        self.provider = provider
        self.consumer = consumer

        self.broker_bin: str = (
            shutil.which("pact-broker") or pact.constants.BROKER_CLIENT_PATH
        )
        if not self.broker_bin:
            if "CI" in os.environ:
                self._install()
                bin_path = shutil.which("pact-broker")
                assert bin_path, "pact-broker not found"
                self.broker_bin = bin_path
            else:
                msg = "pact-broker not found"
                raise RuntimeError(msg)

    def _install(self) -> None:
        """
        Install the Pact Broker CLI tool.

        This function is intended to be run in CI environments, where the pact-broker
        CLI tool may not be installed already. This will download and extract
        the tool
        """
        msg = "pact-broker not found"
        raise NotImplementedError(msg)

    def reset(self) -> None:
        """
        Reset the Pact Broker.

        This function will reset the Pact Broker by deleting all pacts and
        verification results.
        """
        requests.delete(
            str(
                self.url
                / "integrations"
                / "provider"
                / self.provider
                / "consumer"
                / self.consumer
            ),
            timeout=2,
        )

    def publish(self, directory: Path | str, version: str | None = None) -> None:
        """
        Publish the interactions to the Pact Broker.

        Args:
            directory:
                The directory containing the pact files.

            version:
                The version of the consumer application.
        """
        cmd = [
            self.broker_bin,
            "publish",
            str(directory),
            "--broker-base-url",
            str(self.url.with_user(None).with_password(None)),
        ]
        if self.username:
            cmd.extend(["--broker-username", self.username])
        if self.password:
            cmd.extend(["--broker-password", self.password])

        cmd.extend(["--consumer-app-version", version or next_version()])

        subprocess.run(
            cmd,  # noqa: S603
            encoding="utf-8",
            check=True,
        )

    def interaction_id(self, num: int) -> str:
        """
        Find the interaction ID for the given interaction.

        This function is used to find the Pact Broker interaction ID for the given
        interaction. It does this by looking for the interaction with the
        description `f"interaction {num}"`.

        Args:
            num:
                The ID of the interaction.
        """
        response = requests.get(
            str(
                self.url
                / "pacts"
                / "provider"
                / self.provider
                / "consumer"
                / self.consumer
                / "latest"
            ),
            timeout=2,
        )
        response.raise_for_status()
        for interaction in response.json()["interactions"]:
            if interaction["description"] == f"interaction {num}":
                return interaction["_id"]
        msg = f"Interaction {num} not found"
        raise ValueError(msg)

    def verification_results(self, num: int) -> requests.Response:
        """
        Fetch the verification results for the given interaction.

        Args:
            num:
                The ID of the interaction.
        """
        interaction_id = self.interaction_id(num)
        response = requests.get(
            str(
                self.url
                / "pacts"
                / "provider"
                / self.provider
                / "consumer"
                / self.consumer
                / "latest"
                / "verification-results"
                / interaction_id
            ),
            timeout=2,
        )
        response.raise_for_status()
        return response

    def latest_verification_results(self) -> requests.Response | None:
        """
        Fetch the latest verification results for the provider.

        If there are no verification results, then this function will return
        `None`.
        """
        response = requests.get(
            str(
                self.url
                / "pacts"
                / "provider"
                / self.provider
                / "consumer"
                / self.consumer
                / "latest"
            ),
            timeout=2,
        )
        response.raise_for_status()
        links = response.json()["_links"]
        response = requests.get(
            links["pb:latest-verification-results"]["href"], timeout=2
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} <dir>")
        sys.exit(1)

    Provider(sys.argv[1]).run()


################################################################################
## Given
################################################################################


def a_provider_is_started_that_returns_the_responses_from_interactions(
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a provider is started that returns the responses? "
            r'from interactions? "?(?P<interactions>[0-9, ]+)"?',
        ),
        converters={"interactions": lambda x: [int(i) for i in x.split(",") if i]},
        target_fixture="provider_url",
        stacklevel=stacklevel + 1,
    )
    def _(
        interaction_definitions: dict[int, InteractionDefinition],
        interactions: list[int],
        temp_dir: Path,
    ) -> Generator[URL, None, None]:
        """
        Start a provider that returns the responses from the given interactions.
        """
        logger.debug("Starting provider for interactions %s", interactions)

        for i in interactions:
            logger.debug("Interaction %d: %s", i, interaction_definitions[i])

        with (temp_dir / "interactions.pkl").open("wb") as pkl_file:
            pickle.dump([interaction_definitions[i] for i in interactions], pkl_file)

        yield from start_provider(temp_dir)


def a_provider_is_started_that_returns_the_responses_from_interactions_with_changes(
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a provider is started that returns the responses?"
            r' from interactions? "?(?P<interactions>[0-9, ]+)"?'
            r" with the following changes:\n(?P<changes>.+)",
            re.DOTALL,
        ),
        converters={
            "interactions": lambda x: [int(i) for i in x.split(",") if i],
            "changes": parse_markdown_table,
        },
        target_fixture="provider_url",
        stacklevel=stacklevel + 1,
    )
    def _(
        interaction_definitions: dict[int, InteractionDefinition],
        interactions: list[int],
        changes: list[dict[str, str]],
        temp_dir: Path,
    ) -> Generator[URL, None, None]:
        """
        Start a provider that returns the responses from the given interactions.
        """
        logger.debug("Starting provider for modified interactions %s", interactions)

        assert len(changes) == 1, "Only one set of changes is supported"
        defns: list[InteractionDefinition] = []
        for interaction in interactions:
            defn = copy.deepcopy(interaction_definitions[interaction])
            defn.update(**changes[0])
            defns.append(defn)
            logger.debug(
                "Updated interaction %d: %s",
                interaction,
                defn,
            )

        with (temp_dir / "interactions.pkl").open("wb") as pkl_file:
            pickle.dump(defns, pkl_file)

        yield from start_provider(temp_dir)


def start_provider(provider_dir: str | Path) -> Generator[URL, None, None]:  # noqa: C901
    """Start the provider app with the given interactions."""
    process = subprocess.Popen(
        [  # noqa: S603
            sys.executable,
            Path(__file__),
            str(provider_dir),
        ],
        cwd=Path.cwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )

    pattern = re.compile(r" \* Running on (?P<url>[^ ]+)")
    while True:
        if process.poll() is not None:
            logger.error("Provider process exited with code %d", process.returncode)
            logger.error(
                "Provider stdout: %s", process.stdout.read() if process.stdout else ""
            )
            logger.error(
                "Provider stderr: %s", process.stderr.read() if process.stderr else ""
            )
            msg = f"Provider process exited with code {process.returncode}"
            raise RuntimeError(msg)
        if (
            process.stderr
            and (line := process.stderr.readline())
            and (match := pattern.match(line))
        ):
            break
        time.sleep(0.1)

    url = URL(match.group("url"))
    logger.debug("Provider started on %s", url)
    for _ in range(50):
        try:
            response = requests.get(str(url / "_test" / "ping"), timeout=1)
            assert response.text == "pong"
            break
        except (requests.RequestException, AssertionError):
            time.sleep(0.1)
            continue
    else:
        msg = "Failed to ping provider"
        raise RuntimeError(msg)

    def redirect() -> NoReturn:
        while True:
            if process.stdout:
                while line := process.stdout.readline():
                    logger.debug("Provider stdout: %s", line.strip())
            if process.stderr:
                while line := process.stderr.readline():
                    logger.debug("Provider stderr: %s", line.strip())

    thread = Thread(target=redirect, daemon=True)
    thread.start()

    yield url

    process.send_signal(signal.SIGINT)


def a_pact_file_for_interaction_is_to_be_verified(
    version: str,
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a Pact file for interaction (?P<interaction>\d+) is to be verified"
            r"(?P<pending>(, but is marked pending)?)",
        ),
        converters={"interaction": int, "pending": lambda x: x != ""},
        stacklevel=stacklevel + 1,
    )
    def _(
        interaction_definitions: dict[int, InteractionDefinition],
        verifier: Verifier,
        interaction: int,
        pending: bool,  # noqa: FBT001
        temp_dir: Path,
    ) -> None:
        """
        Verify the Pact file for the given interaction.
        """
        logger.debug(
            "Adding interaction %d to be verified: %s",
            interaction,
            interaction_definitions[interaction],
        )

        defn = interaction_definitions[interaction]
        defn.pending = pending

        pact = Pact("consumer", "provider")
        pact.with_specification(version)
        defn.add_to_pact(pact, f"interaction {interaction}")
        (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
        pact.write_file(temp_dir / "pacts")

        with (temp_dir / "pacts" / "consumer-provider.json").open(
            "r",
            encoding="utf-8",
        ) as f:
            for line in f:
                logger.debug("Pact file: %s", line.rstrip())

        verifier.add_source(temp_dir / "pacts")


def a_pact_file_for_interaction_is_to_be_verified_with_comments(
    version: str,
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a Pact file for interaction (?P<interaction>\d+) is to be verified"
            r" with the following comments:\n(?P<comments>.+)",
            re.DOTALL,
        ),
        converters={"interaction": int, "comments": parse_markdown_table},
        stacklevel=stacklevel + 1,
    )
    def _(
        interaction_definitions: dict[int, InteractionDefinition],
        verifier: Verifier,
        interaction: int,
        comments: list[dict[str, str]],
        temp_dir: Path,
    ) -> None:
        """
        Verify the Pact file for the given interaction.
        """
        logger.debug(
            "Adding interaction %d to be verified: %s",
            interaction,
            interaction_definitions[interaction],
        )

        defn = interaction_definitions[interaction]
        for comment in comments:
            if comment["type"] == "text":
                defn.text_comments.append(comment["comment"])
            elif comment["type"] == "testname":
                defn.test_name = comment["comment"]
            else:
                defn.comments[comment["type"]] = comment["comment"]
        logger.info("Updated interaction %d: %s", interaction, defn)

        pact = Pact("consumer", "provider")
        pact.with_specification(version)
        defn.add_to_pact(pact, f"interaction {interaction}")
        (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
        pact.write_file(temp_dir / "pacts")

        with (temp_dir / "pacts" / "consumer-provider.json").open(
            "r",
            encoding="utf-8",
        ) as f:
            for line in f:
                logger.debug("Pact file: %s", line.rstrip())

        verifier.add_source(temp_dir / "pacts")


def a_pact_file_for_interaction_is_to_be_verified_from_a_pact_broker(
    version: str,
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a Pact file for interaction (?P<interaction>\d+)"
            r" is to be verified from a Pact broker",
        ),
        converters={"interaction": int},
        target_fixture="pact_broker",
        stacklevel=stacklevel + 1,
    )
    def _(
        interaction_definitions: dict[int, InteractionDefinition],
        broker_url: URL,
        verifier: Verifier,
        interaction: int,
        temp_dir: Path,
    ) -> Generator[PactBroker, None, None]:
        """
        Verify the Pact file for the given interaction from a Pact broker.
        """
        logger.debug(
            "Adding interaction %d to be verified from a Pact broker", interaction
        )

        defn = interaction_definitions[interaction]

        pact = Pact("consumer", "provider")
        pact.with_specification(version)
        defn.add_to_pact(pact, f"interaction {interaction}")

        pacts_dir = temp_dir / "pacts"
        pacts_dir.mkdir(exist_ok=True, parents=True)
        pact.write_file(pacts_dir)

        pact_broker = PactBroker(broker_url)
        if reset_broker_var.get():
            logger.debug("Resetting Pact broker")
            pact_broker.reset()
            reset_broker_var.set(False)
        pact_broker.publish(pacts_dir)
        verifier.broker_source(pact_broker.url)
        yield pact_broker


def publishing_of_verification_results_is_enabled(stacklevel: int = 1) -> None:
    @given("publishing of verification results is enabled", stacklevel=stacklevel + 1)
    def _(verifier: Verifier) -> None:
        """
        Enable publishing of verification results.
        """
        logger.debug("Publishing verification results")

        verifier.set_publish_options(
            "0.0.0",
        )


def a_provider_state_callback_is_configured(
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a provider state callback is configured"
            r"(?P<failure>(, but will return a failure)?)",
        ),
        converters={"failure": lambda x: x != ""},
        stacklevel=stacklevel + 1,
    )
    def _(
        verifier: Verifier,
        provider_url: URL,
        temp_dir: Path,
        failure: bool,  # noqa: FBT001
    ) -> None:
        """
        Configure a provider state callback.
        """
        logger.debug("Configuring provider state callback")

        if failure:
            with (temp_dir / "fail_callback").open("w") as f:
                f.write("true")

        verifier.set_state(
            provider_url / "_test" / "callback",
            teardown=True,
        )


def a_pact_file_for_interaction_is_to_be_verified_with_a_provider_state_defined(
    version: str,
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a Pact file for interaction (?P<interaction>\d+) is to be verified"
            r' with a provider state "(?P<state>[^"]+)" defined',
        ),
        converters={"interaction": int},
        stacklevel=stacklevel + 1,
    )
    def _(
        interaction_definitions: dict[int, InteractionDefinition],
        verifier: Verifier,
        interaction: int,
        state: str,
        temp_dir: Path,
    ) -> None:
        """
        Verify the Pact file for the given interaction with a provider state defined.
        """
        logger.debug(
            "Adding interaction %d to be verified with provider state %s",
            interaction,
            state,
        )

        defn = interaction_definitions[interaction]
        defn.states = [InteractionDefinition.State(state)]

        pact = Pact("consumer", "provider")
        pact.with_specification(version)
        defn.add_to_pact(pact, f"interaction {interaction}")
        (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
        pact.write_file(temp_dir / "pacts")

        verifier.add_source(temp_dir / "pacts")

        with (temp_dir / "provider_states").open("w") as f:
            logger.debug("Writing provider state to %s", temp_dir / "provider_states")
            json.dump([s.as_dict() for s in defn.states], f)


def a_pact_file_for_interaction_is_to_be_verified_with_a_provider_states_defined(
    version: str,
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a Pact file for interaction (?P<interaction>\d+) is to be verified"
            r" with the following provider states defined:\n(?P<states>.+)",
            re.DOTALL,
        ),
        converters={"interaction": int, "states": parse_markdown_table},
        stacklevel=stacklevel + 1,
    )
    def _(
        interaction_definitions: dict[int, InteractionDefinition],
        verifier: Verifier,
        interaction: int,
        states: list[dict[str, Any]],
        temp_dir: Path,
    ) -> None:
        """
        Verify the Pact file for the given interaction with provider states defined.
        """
        logger.debug(
            "Adding interaction %d to be verified with provider states %s",
            interaction,
            states,
        )

        defn = interaction_definitions[interaction]
        defn.states = [
            InteractionDefinition.State(s["State Name"], s.get("Parameters", None))
            for s in states
        ]

        pact = Pact("consumer", "provider")
        pact.with_specification(version)
        defn.add_to_pact(pact, f"interaction {interaction}")
        (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
        pact.write_file(temp_dir / "pacts")

        verifier.add_source(temp_dir / "pacts")

        with (temp_dir / "provider_states").open("w") as f:
            logger.debug("Writing provider state to %s", temp_dir / "provider_states")
            json.dump([s.as_dict() for s in defn.states], f)


def a_request_filter_is_configured_to_make_the_following_changes(
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.parse(
            "a request filter is configured to make the following changes:\n{content}"
        ),
        converters={"content": parse_markdown_table},
        stacklevel=stacklevel + 1,
    )
    def _(
        content: list[dict[str, str]],
        verifier: Verifier,
    ) -> None:
        """
        Configure a request filter to make the given changes.
        """
        logger.debug("Configuring request filter")

        if "headers" in content[0]:
            verifier.add_custom_headers(parse_headers(content[0]["headers"]).items())
        else:
            msg = "Unsupported filter type"
            raise RuntimeError(msg)


################################################################################
## When
################################################################################


def the_verification_is_run(
    stacklevel: int = 1,
) -> None:
    @when(
        "the verification is run",
        target_fixture="verifier_result",
        stacklevel=stacklevel + 1,
    )
    def _(
        verifier: Verifier,
        provider_url: URL,
    ) -> tuple[Verifier, Exception | None]:
        """
        Run the verification.
        """
        logger.debug("Running verification on %r", verifier)

        verifier.set_info("provider", url=provider_url)
        try:
            verifier.verify()
        except Exception as e:  # noqa: BLE001
            return verifier, e
        return verifier, None


################################################################################
## Then
################################################################################


def the_verification_will_be_successful(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(r"the verification will(?P<negated>( NOT)?) be successful"),
        converters={"negated": lambda x: x == " NOT"},
        stacklevel=stacklevel + 1,
    )
    def _(
        verifier_result: tuple[Verifier, Exception | None],
        negated: bool,  # noqa: FBT001
    ) -> None:
        """
        Check that the verification was successful.
        """
        logger.debug("Checking verification result")
        logger.debug("Verifier result: %s", verifier_result)

        if negated:
            assert verifier_result[1] is not None
        else:
            assert verifier_result[1] is None


def the_verification_results_will_contain_a_error(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(r'the verification results will contain a "(?P<error>[^"]+)" error'),
        stacklevel=stacklevel + 1,
    )
    def _(verifier_result: tuple[Verifier, Exception | None], error: str) -> None:
        """
        Check that the verification results contain the given error.
        """
        logger.debug("Checking that verification results contain error %s", error)

        verifier = verifier_result[0]
        logger.debug("Verification results: %s", json.dumps(verifier.results, indent=2))

        if error == "Response status did not match":
            mismatch_type = "StatusMismatch"
        elif error == "Headers had differences":
            mismatch_type = "HeaderMismatch"
        elif error == "Body had differences":
            mismatch_type = "BodyMismatch"
        elif error == "State change request failed":
            assert "One or more of the setup state change handlers has failed" in [
                error["mismatch"]["message"] for error in verifier.results["errors"]
            ]
            return
        else:
            msg = f"Unknown error type: {error}"
            raise ValueError(msg)

        mismatch_types = [
            mismatch["type"]
            for error in verifier.results["errors"]
            for mismatch in error["mismatch"]["mismatches"]
        ]
        assert mismatch_type in mismatch_types
        if len(mismatch_types) > 1:
            warnings.warn(
                f"Multiple mismatch types found: {mismatch_types}", stacklevel=1
            )
            for verifier_error in verifier.results["errors"]:
                for mismatch in verifier_error["mismatch"]["mismatches"]:
                    warnings.warn(f"Mismatch: {mismatch}", stacklevel=1)


def a_verification_result_will_not_be_published_back(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(r"a verification result will NOT be published back"),
        stacklevel=stacklevel + 1,
    )
    def _(pact_broker: PactBroker) -> None:
        """
        Check that the verification result was published back to the Pact broker.
        """
        logger.debug("Checking that verification result was not published back")

        response = pact_broker.latest_verification_results()
        if response:
            with pytest.raises(requests.HTTPError, match="404 Client Error"):
                response.raise_for_status()


def a_successful_verification_result_will_be_published_back(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            "a successful verification result "
            "will be published back "
            r"for interaction \{(?P<interaction>\d+)\}",
        ),
        converters={"interaction": int},
        stacklevel=stacklevel + 1,
    )
    def _(
        pact_broker: PactBroker,
        interaction: int,
    ) -> None:
        """
        Check that the verification result was published back to the Pact broker.
        """
        logger.debug(
            "Checking that verification result was published back for interaction %d",
            interaction,
        )

        interaction_id = pact_broker.interaction_id(interaction)
        response = pact_broker.latest_verification_results()
        assert response is not None
        assert response.ok
        data: dict[str, Any] = response.json()
        assert data["success"]

        for test_result in data["testResults"]:
            if test_result["interactionId"] == interaction_id:
                assert test_result["success"]
                break
        else:
            msg = f"Interaction {interaction} not found in verification results"
            raise ValueError(msg)


def a_failed_verification_result_will_be_published_back(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            "a failed verification result "
            "will be published back "
            r"for the interaction \{(?P<interaction>\d+)\}",
        ),
        converters={"interaction": int},
        stacklevel=stacklevel + 1,
    )
    def _(
        pact_broker: PactBroker,
        interaction: int,
    ) -> None:
        """
        Check that the verification result was published back to the Pact broker.
        """
        logger.debug(
            "Checking that failed verification result"
            " was published back for interaction %d",
            interaction,
        )

        interaction_id = pact_broker.interaction_id(interaction)
        response = pact_broker.latest_verification_results()
        assert response is not None
        assert response.ok
        data: dict[str, Any] = response.json()
        assert not data["success"]

        for test_result in data["testResults"]:
            if test_result["interactionId"] == interaction_id:
                assert not test_result["success"]
                break
        else:
            msg = f"Interaction {interaction} not found in verification results"
            raise ValueError(msg)


def the_provider_state_callback_will_be_called_before_the_verification_is_run(
    stacklevel: int = 1,
) -> None:
    @then(
        "the provider state callback will be called before the verification is run",
        stacklevel=stacklevel + 1,
    )
    def _() -> None:
        """
        Check that the provider state callback was called before the verification.
        """
        logger.debug("Checking provider state callback was called before verification")


def the_provider_state_callback_will_receive_a_setup_call(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            r"the provider state callback"
            r" will receive a (?P<action>setup|teardown) call"
            r' (with )?"(?P<state>[^"]*)" as the provider state parameter',
        ),
        stacklevel=stacklevel + 1,
    )
    def _(
        temp_dir: Path,
        action: str,
        state: str,
    ) -> None:
        """
        Check that the provider state callback received a setup call.
        """
        logger.info("Checking provider state callback received a %s call", action)
        logger.info("Callback files: %s", list(temp_dir.glob("callback.*.json")))
        for file in temp_dir.glob("callback.*.json"):
            with file.open("r") as f:
                data: dict[str, Any] = json.load(f)
                logger.debug("Checking callback data: %s", data)
                if (
                    "action" in data["query_params"]
                    and data["query_params"]["action"] == action
                    and data["query_params"]["state"] == state
                ):
                    break
        else:
            msg = f"No {action} call found"
            raise AssertionError(msg)


def the_provider_state_callback_will_receive_a_setup_call_with_parameters(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            r"the provider state callback"
            r" will receive a (?P<action>setup|teardown) call"
            r' (with )?"(?P<state>[^"]*)"'
            r" and the following parameters:\n(?P<parameters>.+)",
            re.DOTALL,
        ),
        converters={"parameters": parse_markdown_table},
        stacklevel=stacklevel + 1,
    )
    def _(
        temp_dir: Path,
        action: str,
        state: str,
        parameters: list[dict[str, str]],
    ) -> None:
        """
        Check that the provider state callback received a setup call.
        """
        logger.info("Checking provider state callback received a %s call", action)
        logger.info("Callback files: %s", list(temp_dir.glob("callback.*.json")))
        params: dict[str, str] = parameters[0]
        # If we have a string that looks quoted, unquote it
        for key, value in params.items():
            if value.startswith('"') and value.endswith('"'):
                params[key] = value[1:-1]

        for file in temp_dir.glob("callback.*.json"):
            with file.open("r") as f:
                data: dict[str, Any] = json.load(f)
                logger.debug("Checking callback data: %s", data)
                if (
                    "action" in data["query_params"]
                    and data["query_params"]["action"] == action
                    and data["query_params"]["state"] == state
                ):
                    for key, value in params.items():
                        assert key in data["query_params"], f"Parameter {key} not found"
                        assert data["query_params"][key] == value
                    break
        else:
            msg = f"No {action} call found"
            raise AssertionError(msg)


def the_provider_state_callback_will_not_receive_a_setup_call(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            r"the provider state callback will "
            r"NOT receive a (?P<action>setup|teardown) call"
        ),
        stacklevel=stacklevel + 1,
    )
    def _(
        temp_dir: Path,
        action: str,
    ) -> None:
        """
        Check that the provider state callback did not receive a setup call.
        """
        for file in temp_dir.glob("callback.*.json"):
            with file.open("r") as f:
                data: dict[str, Any] = json.load(f)
                logger.debug("Checking callback data: %s", data)
                if (
                    "action" in data["query_params"]
                    and data["query_params"]["action"] == action
                ):
                    msg = f"Unexpected {action} call found"
                    raise AssertionError(msg)


def the_provider_state_callback_will_be_called_after_the_verification_is_run(
    stacklevel: int = 1,
) -> None:
    @then(
        "the provider state callback will be called after the verification is run",
        stacklevel=stacklevel + 1,
    )
    def _() -> None:
        """
        Check that the provider state callback was called after the verification.
        """


def a_warning_will_be_displayed_that_there_was_no_callback_configured(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            r"a warning will be displayed"
            r" that there was no provider state callback configured"
            r' for provider state "(?P<state>[^"]*)"',
        ),
        stacklevel=stacklevel + 1,
    )
    def _(
        state: str,
    ) -> None:
        """
        Check that a warning was displayed that there was no callback configured.
        """
        logger.debug("Checking for warning about missing provider state callback")
        assert state


def the_request_to_the_provider_will_contain_the_header(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            r'the request to the provider will contain the header "(?P<header>[^"]+)"',
        ),
        converters={"header": lambda x: parse_headers(f"'{x}'")},
        stacklevel=stacklevel + 1,
    )
    def _(
        verifier_result: tuple[Verifier, Exception | None],
        header: dict[str, str],
        temp_dir: Path,
    ) -> None:
        """
        Check that the request to the provider contained the given header.
        """
        verifier = verifier_result[0]
        logger.debug("verifier output: %s", verifier.output(strip_ansi=True))
        logger.debug("verifier results: %s", json.dumps(verifier.results, indent=2))
        for request_path in temp_dir.glob("request.*.json"):
            with request_path.open("r") as f:
                data: dict[str, Any] = json.load(f)
                if data["path"].startswith("/_test"):
                    continue
                logger.debug("Checking request data: %s", data)
                assert all([k, v] in data["headers_list"] for k, v in header.items())
                break
        else:
            msg = "No request found"
            raise AssertionError(msg)


def there_will_be_a_pending_error(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(r'there will be a pending "(?P<error>[^"]+)" error'),
        stacklevel=stacklevel + 1,
    )
    def _(
        error: str,
        verifier_result: tuple[Verifier, Exception | None],
    ) -> None:
        """
        There will be a pending error.
        """
        logger.debug("Checking for pending error")
        verifier, err = verifier_result

        if error == "Body had differences":
            mismatch = "BodyMismatch"
        else:
            msg = f"Unknown error type: {error}"
            raise ValueError(msg)

        assert err is None
        assert "pendingErrors" in verifier.results
        for verifier_error in verifier.results["pendingErrors"]:
            mismatches = [m["type"] for m in verifier_error["mismatch"]["mismatches"]]
            if mismatch in mismatches:
                if len(mismatches) > 1:
                    warnings.warn(
                        f"Multiple mismatch types found: {mismatches}",
                        stacklevel=2,
                    )
                break
        else:
            msg = "Pending error not found"
            raise AssertionError(msg)


def the_comment_will_have_been_printed_to_the_console(stacklevel: int = 1) -> None:
    @then(
        parsers.re(
            r'the comment "(?P<comment>[^"]+)" will have been printed to the console'
        ),
        stacklevel=stacklevel + 1,
    )
    def _(
        comment: str,
        verifier_result: tuple[Verifier, Exception | None],
    ) -> None:
        """
        Check that the given comment was printed to the console.
        """
        verifier, err = verifier_result
        logger.debug("Checking for comment %r in verifier output", comment)
        logger.debug("Verifier output: %s", verifier.output(strip_ansi=True))
        assert err is None
        assert comment in verifier.output(strip_ansi=True)


def the_name_of_the_test_will_be_displayed_as_the_original_test_name(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            r'the "(?P<test_name>[^"]+)" will displayed as the original test name'
        ),
        stacklevel=stacklevel + 1,
    )
    def _(
        test_name: str,
        verifier_result: tuple[Verifier, Exception | None],
    ) -> None:
        """
        Check that the given test name was displayed as the original test name.
        """
        verifier, err = verifier_result
        logger.debug("Checking for test name %r in verifier output", test_name)
        logger.debug("Verifier output: %s", verifier.output(strip_ansi=True))
        assert err is None
        assert test_name in verifier.output(strip_ansi=True)
