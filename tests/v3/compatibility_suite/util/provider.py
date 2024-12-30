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

import copy
import inspect
import json
import logging
import os
import re
import shutil
import subprocess
import warnings
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from threading import Thread
from typing import TYPE_CHECKING, Any, ClassVar, TypedDict
from unittest.mock import MagicMock

import pytest
import requests
from multidict import CIMultiDict
from pytest_bdd import given, parsers, then, when
from typing_extensions import Self
from yarl import URL

import pact.constants  # type: ignore[import-untyped]
from pact import __version__
from pact.v3._server import MessageProducer
from pact.v3._util import find_free_port
from pact.v3.pact import Pact
from tests.v3.compatibility_suite.util import (
    parse_headers,
    parse_horizontal_table,
)
from tests.v3.compatibility_suite.util.interaction_definition import (
    InteractionDefinition,
    InteractionState,
)

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path
    from types import TracebackType

    from pact.v3.types import Message
    from pact.v3.verifier import Verifier


logger = logging.getLogger(__name__)

VERIFIER_ERROR_MAP: dict[str, str] = {
    "Response status did not match": "StatusMismatch",
    "Headers had differences": "HeaderMismatch",
    "Body had differences": "BodyMismatch",
    "Metadata had differences": "MetadataMismatch",
}


def _next_version() -> Generator[str, None, None]:
    """
    Get the next version for the consumer.

    This is used to generate a new version for the consumer application to use
    when publishing the interactions to the Pact Broker.

    Returns:
        The next version.
    """
    version = 0
    while True:
        yield str(version)
        version += 1


version_iter = _next_version()


class Provider:
    """
    HTTP provider for the compatibility suite tests.

    As we are testing specific scenarios, this provider server is designed to
    be easily customized to return specific responses for specific requests.
    """

    interactions: ClassVar[list[InteractionDefinition]] = []

    def __init__(
        self,
        host: str = "localhost",
        port: int | None = None,
    ) -> None:
        """
        Initialize the provider.

        Args:
            host:
                The host for the provider.

            port:
                The port for the provider. If not provided, then a free port
                will be found.
        """
        self._host = host
        self._port = port or find_free_port()

        self._interactions: list[InteractionDefinition] = []
        self.requests: list[ProviderRequestDict] | None = None
        self._server: ProviderServer | None = None
        self._thread: Thread | None = None

    @property
    def host(self) -> str:
        """
        Server host.
        """
        return self._host

    @property
    def port(self) -> int:
        """
        Server port.
        """
        return self._port

    @property
    def url(self) -> URL:
        """
        Server URL.
        """
        return URL(f"http://{self.host}:{self.port}")

    def add_interaction(self, interaction: InteractionDefinition) -> None:
        """
        Add an interaction to the provider.

        Args:
            interaction:
                The interaction to add.
        """
        self._interactions.append(interaction)

    def __enter__(self) -> Self:
        """
        Start the provider.
        """
        logger.info(
            "Starting provider on %s with %s interaction(s)",
            self.url,
            len(self._interactions),
        )
        self._server = ProviderServer(
            (self.host, self.port),
            ProviderRequestHandler,
            interactions=self._interactions,
        )
        self._thread = Thread(
            target=self._server.serve_forever,
            name="Compatibility Suite Provider Server",
        )
        self._thread.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Exit the Provider context.
        """
        if not self._thread or not self._server:
            warnings.warn(
                "Exiting server context despite server not being started.",
                stacklevel=2,
            )
            return

        self.requests = self._server.requests
        self._server.shutdown()
        self._thread.join()


class ProviderServer(ThreadingHTTPServer):
    """
    Simple HTTP server for the provider.
    """

    def __init__(
        self,
        *args: Any,  # noqa: ANN401
        interactions: list[InteractionDefinition],
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize the server.

        Args:
            interactions:
                The interactions to use for the server.

            *args:
                Positional arguments to pass to the base `ThreadingHTTPServer`
                class.

            **kwargs:
                Keyword arguments to pass to the base `ThreadingHTTPServer`
                class.
        """
        self.interactions = interactions
        self.requests: list[ProviderRequestDict] = []
        super().__init__(*args, **kwargs)


class ProviderRequestDict(TypedDict):
    """
    Request dictionary for the provider server.
    """

    method: str | None
    path: str | None
    query: str | None
    headers: CIMultiDict[str] | None
    body: bytes | None


class ProviderRequestHandler(SimpleHTTPRequestHandler):
    """
    Request handler for the provider server.

    This class is responsible for handling the requests made to the provider
    server. It uses the standard library's
    [`SimpleHTTPRequestHandler`][http.server.SimpleHTTPRequestHandler].
    """

    if TYPE_CHECKING:
        server: ProviderServer

    def version_string(self) -> str:
        """
        Get the server version string.

        Returns:
            The server version string.
        """
        return f"Compatibility Suite Provider/{__version__}"

    def _record_request(self) -> None:
        """
        Record the request.

        Parses the request and records it in the server's request list.

        The `rfile` attribute, being a file-like object, can only be read once.
        This method reads the request body and then replaces the `rfile`
        attribute with a new `BytesIO` object containing the request body.
        """
        size = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(size)
        request: ProviderRequestDict = {
            "method": self.command,
            "path": self.path,
            "query": self.path.split("?", 1)[1] if "?" in self.path else None,
            "headers": CIMultiDict(self.headers.items()),
            "body": body,
        }
        self.server.requests.append(request)
        self.rfile = BytesIO(body)

    def do_POST(self) -> None:  # noqa: N802
        """
        Handle a POST request.
        """
        logger.info("Handling %s %s", self.command, self.path)
        self._record_request()

        for interaction in self.server.interactions:
            if interaction.matches_request(self):
                interaction.handle_request(self)
                return

        logger.warning(
            "No matching interaction found for %s %s",
            self.command,
            self.path,
        )
        self.send_error(404, "Not Found")

    def do_GET(self) -> None:  # noqa: N802
        """
        Handle a GET request.
        """
        logger.info("Handling %s %s", self.command, self.path)
        self._record_request()

        for interaction in self.server.interactions:
            if interaction.matches_request(self):
                interaction.handle_request(self)
                return

        logger.warning(
            "No matching interaction found for %s %s",
            self.command,
            self.path,
        )
        self.send_error(404, "Not Found")


class PactBroker:
    """
    Interface to the Pact Broker.
    """

    def __init__(
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

        cmd.extend(["--consumer-app-version", version or next(version_iter)])

        subprocess.run(  # noqa: S603
            cmd,
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
        target_fixture="provider",
        stacklevel=stacklevel + 1,
    )
    def _(
        interaction_definitions: dict[int, InteractionDefinition],
        interactions: list[int],
    ) -> Generator[Provider, None, None]:
        """
        Start a provider that returns the responses from the given interactions.
        """
        logger.info("Starting provider for interactions %s", interactions)

        provider = Provider()
        for i in interactions:
            logger.info("Interaction %d: %s", i, interaction_definitions[i])
            provider.add_interaction(interaction_definitions[i])

        with provider:
            yield provider


def a_provider_is_started_that_returns_the_responses_from_interactions_with_changes(
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a provider is started that returns the responses?"
            r' from interactions? "?(?P<ids>[0-9, ]+)"?'
            r" with the following changes:",
            re.DOTALL,
        ),
        converters={"ids": lambda x: [int(i) for i in x.split(",") if i]},
        target_fixture="provider",
        stacklevel=stacklevel + 1,
    )
    def _(
        interaction_definitions: dict[int, InteractionDefinition],
        ids: list[int],
        datatable: list[list[str]],
    ) -> Generator[Provider, None, None]:
        """
        Start a provider that returns the responses from the given interactions.
        """
        logger.info("Starting provider for modified interactions %s", ids)
        changes = parse_horizontal_table(datatable)

        assert len(changes) == 1, "Only one set of changes is supported"
        interactions: list[InteractionDefinition] = []
        for id_ in ids:
            interaction = copy.deepcopy(interaction_definitions[id_])
            interaction.update(**changes[0])  # type: ignore[arg-type]
            interactions.append(interaction)
            logger.info(
                "Updated interaction %d: %s",
                id_,
                interaction,
            )

        provider = Provider()
        for interaction in interactions:
            provider.add_interaction(interaction)
        with provider:
            yield provider


def a_provider_is_started_that_can_generate_the_message(
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a provider is started"
            r' that can generate the "(?P<name>[^"]+)" message'
            r' with "(?P<body>.+)"$'
        ),
        target_fixture="provider",
        stacklevel=stacklevel + 1,
    )
    def _(
        verifier: Verifier,
        name: str,
        body: str,
    ) -> None:
        logger.info("Starting provider for message %s", name)
        interaction = InteractionDefinition(
            type="Async",
            description=name,
            body=body.replace(r"\"", '"'),
        )
        # If there's no content type, then it is a `text/plain` message
        if interaction.body and not interaction.body.mime_type:
            interaction.body.mime_type = "text/plain"

        # The following is a hack to allow for multiple message interactions to
        # be defined. Typically, the end user would know all messages to be
        # produced; however, we don't have this luxury in this context.
        if isinstance(verifier._message_producer, MessageProducer):  # noqa: SLF001
            original_handler = verifier._message_producer._handler  # noqa: SLF001

            def handler(*args: Any, **kwargs: Any) -> Message:  # noqa: ANN401
                try:
                    return original_handler(*args, **kwargs)
                except AssertionError:
                    return interaction.message_producer(*args, **kwargs)

            verifier.message_handler(handler)

        else:
            verifier.message_handler(interaction.message_producer)


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
        logger.info(
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
                logger.info("Pact file: %s", line.rstrip())

        verifier.add_source(temp_dir / "pacts")


def a_pact_file_for_message_is_to_be_verified(
    version: str,
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r'a Pact file for "(?P<name>[^"]+)":"(?P<fixture>[^"]+)" is to be verified'
            r"(?P<pending>(, but is marked pending)?)",
        ),
        converters={"pending": lambda x: x != ""},
        stacklevel=stacklevel + 1,
    )
    def _(
        verifier: Verifier,
        temp_dir: Path,
        name: str,
        fixture: str,
        pending: bool,  # noqa: FBT001
    ) -> None:
        defn = InteractionDefinition(
            type="Async",
            description=name,
            body=fixture,
        )
        defn.pending = pending
        logger.info("Adding message interaction: %s", defn)

        pact = Pact("consumer", "provider")
        pact.with_specification(version)
        defn.add_to_pact(pact, name)
        (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
        pact.write_file(temp_dir / "pacts")

        with (temp_dir / "pacts" / "consumer-provider.json").open() as f:
            logger.info("Pact file contents: %s", f.read())

        verifier.add_source(temp_dir / "pacts")


def a_pact_file_for_interaction_is_to_be_verified_with_comments(
    version: str,
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a Pact file for interaction (?P<interaction>\d+) is to be verified"
            r" with the following comments:",
            re.DOTALL,
        ),
        converters={"interaction": int},
        stacklevel=stacklevel + 1,
    )
    def _(
        interaction_definitions: dict[int, InteractionDefinition],
        verifier: Verifier,
        interaction: int,
        datatable: list[list[str]],
        temp_dir: Path,
    ) -> None:
        """
        Verify the Pact file for the given interaction.
        """
        logger.info(
            "Adding interaction %d to be verified: %s",
            interaction,
            interaction_definitions[interaction],
        )
        comments = parse_horizontal_table(datatable)
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
                logger.info("Pact file: %s", line.rstrip())

        verifier.add_source(temp_dir / "pacts")


def a_pact_file_for_message_is_to_be_verified_with_comments(
    version: str,
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r'a Pact file for "(?P<name>[^"]+)":"(?P<fixture>[^"]+)" is to be verified'
            r" with the following comments:",
            re.DOTALL,
        ),
        stacklevel=stacklevel + 1,
    )
    def _(
        verifier: Verifier,
        temp_dir: Path,
        name: str,
        fixture: str,
        datatable: list[list[str]],
    ) -> None:
        logger.info("Adding message interaction %s with comments", name)
        defn = InteractionDefinition(
            type="Async",
            description=name,
            body=fixture,
        )
        comments = parse_horizontal_table(datatable)
        for comment in comments:
            if comment["type"] == "text":
                defn.text_comments.append(comment["comment"])
            elif comment["type"] == "testname":
                defn.test_name = comment["comment"]
            else:
                defn.comments[comment["type"]] = comment["comment"]
        logger.info("Updated interaction: %s", defn)

        pact = Pact("consumer", "provider")
        pact.with_specification(version)
        defn.add_to_pact(pact, name)
        (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
        pact.write_file(temp_dir / "pacts")

        with (temp_dir / "pacts" / "consumer-provider.json").open() as f:
            logger.info("Pact file contents: %s", f.read())

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
        logger.info(
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
        pact_broker.publish(pacts_dir)
        verifier.broker_source(pact_broker.url)
        yield pact_broker


def publishing_of_verification_results_is_enabled(stacklevel: int = 1) -> None:
    @given("publishing of verification results is enabled", stacklevel=stacklevel + 1)
    def _(verifier: Verifier) -> None:
        """
        Enable publishing of verification results.
        """
        logger.info("Publishing verification results")

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
        target_fixture="provider_callback",
        converters={"failure": lambda x: x != ""},
        stacklevel=stacklevel + 1,
    )
    def _(
        verifier: Verifier,
        failure: bool,  # noqa: FBT001
    ) -> MagicMock:
        """
        Configure a provider state callback.
        """
        logger.info("Configuring provider state callback")

        def _callback(
            _name: str,
            _action: str,
            _params: dict[str, str] | None,
        ) -> None:
            pass

        provider_callback = MagicMock(return_value=None, spec=_callback)
        provider_callback.__signature__ = inspect.signature(_callback)
        if failure:
            provider_callback.side_effect = RuntimeError("Provider state change failed")

        verifier.state_handler(
            provider_callback,
            teardown=True,
        )
        return provider_callback


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
        logger.info(
            "Adding interaction %d to be verified with provider state %s",
            interaction,
            state,
        )

        defn = interaction_definitions[interaction]
        defn.states = [InteractionState(state)]

        pact = Pact("consumer", "provider")
        pact.with_specification(version)
        defn.add_to_pact(pact, f"interaction {interaction}")
        (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
        pact.write_file(temp_dir / "pacts")

        verifier.add_source(temp_dir / "pacts")

        with (temp_dir / "provider_states").open("w") as f:
            logger.info("Writing provider state to %s", temp_dir / "provider_states")
            json.dump([s.as_dict() for s in defn.states], f)


def a_pact_file_for_interaction_is_to_be_verified_with_a_provider_states_defined(
    version: str,
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a Pact file for interaction (?P<interaction>\d+) is to be verified"
            r" with the following provider states defined:",
            re.DOTALL,
        ),
        converters={"interaction": int},
        stacklevel=stacklevel + 1,
    )
    def _(
        interaction_definitions: dict[int, InteractionDefinition],
        verifier: Verifier,
        interaction: int,
        datatable: list[list[str]],
        temp_dir: Path,
    ) -> None:
        """
        Verify the Pact file for the given interaction with provider states defined.
        """
        states = parse_horizontal_table(datatable)
        logger.info(
            "Adding interaction %d to be verified with provider states %s",
            interaction,
            states,
        )

        defn = interaction_definitions[interaction]
        defn.states = [
            InteractionState(s["State Name"], s.get("Parameters", None)) for s in states
        ]

        pact = Pact("consumer", "provider")
        pact.with_specification(version)
        defn.add_to_pact(pact, f"interaction {interaction}")
        (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
        pact.write_file(temp_dir / "pacts")

        verifier.add_source(temp_dir / "pacts")

        with (temp_dir / "provider_states").open("w") as f:
            logger.info("Writing provider state to %s", temp_dir / "provider_states")
            json.dump([s.as_dict() for s in defn.states], f)


def a_request_filter_is_configured_to_make_the_following_changes(
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.parse("a request filter is configured to make the following changes:"),
        stacklevel=stacklevel + 1,
    )
    def _(
        datatable: list[list[str]],
        verifier: Verifier,
    ) -> None:
        """
        Configure a request filter to make the given changes.
        """
        logger.info("Configuring request filter")

        changes = parse_horizontal_table(datatable)
        if "headers" in changes[0]:
            verifier.add_custom_headers(parse_headers(changes[0]["headers"]).items())
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
        provider: Provider | None,
    ) -> tuple[Verifier, Exception | None]:
        """
        Run the verification.
        """
        logger.info("Running verification on %r", verifier)

        if provider:
            verifier.add_transport(url=provider.url)

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
        logger.info("Checking verification result")
        logger.info("Verifier result: %s", verifier_result)

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
        logger.info("Checking that verification results contain error %s", error)

        verifier = verifier_result[0]
        logger.info("Verification results: %s", json.dumps(verifier.results, indent=2))

        mismatch_type = VERIFIER_ERROR_MAP.get(error)
        if not mismatch_type:
            if error == "State change request failed":
                assert "One or more of the setup state change handlers has failed" in [
                    error["mismatch"]["message"] for error in verifier.results["errors"]
                ]
                return
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
        logger.info("Checking that verification result was not published back")

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
        logger.info(
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
        logger.info(
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
        logger.info("Checking provider state callback was called before verification")


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
        provider_callback: MagicMock,
        action: str,
        state: str,
    ) -> None:
        """
        Check that the provider state callback received a setup call.
        """
        logger.info("Checking provider state callback received a %s call", action)
        logger.debug("Calls: %s", provider_callback.call_args_list)
        provider_callback.assert_called()
        for calls in provider_callback.call_args_list:
            if calls.args[0] == state and calls.args[1] == action:
                return

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
            r" and the following parameters:",
            re.DOTALL,
        ),
        stacklevel=stacklevel + 1,
    )
    def _(
        provider_callback: MagicMock,
        action: str,
        state: str,
        datatable: list[list[str]],
    ) -> None:
        """
        Check that the provider state callback received a setup call.
        """
        logger.info("Checking provider state callback received a %s call", action)
        parameters = parse_horizontal_table(datatable)
        params: dict[str, Any] = parameters[0]
        # Values are JSON values, so parse them
        for key, value in params.items():
            params[key] = json.loads(value)

        provider_callback.assert_called()
        for calls in provider_callback.call_args_list:
            if calls.args[0] == state and calls.args[1] == action:
                assert calls.args[2] == params
                return
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
                logger.info("Checking callback data: %s", data)
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
        logger.info("Checking for warning about missing provider state callback")
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
        provider: Provider,
        header: dict[str, str],
        # verifier_result: tuple[Verifier, Exception | None],
        # temp_dir: Path,
    ) -> None:
        """
        Check that the request to the provider contained the given header.
        """
        logger.info("Checking for header %r in provider requests", header)
        provider.__exit__(None, None, None)
        assert provider.requests
        assert len(provider.requests) == 1
        request = provider.requests[0]
        assert request["headers"]

        for key, value in header.items():
            assert key in request["headers"]
            assert request["headers"][key] == value


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
        logger.info("Checking for pending error")
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
        logger.info("Checking for comment %r in verifier output", comment)
        logger.info("Verifier output: %s", verifier.output(strip_ansi=True))
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
        logger.info("Checking for test name %r in verifier output", test_name)
        logger.info("Verifier output: %s", verifier.output(strip_ansi=True))
        assert err is None
        assert test_name in verifier.output(strip_ansi=True)
