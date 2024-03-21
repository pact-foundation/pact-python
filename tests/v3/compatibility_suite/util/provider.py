"""
Provider utilities for compatibility suite tests.

The main functionality provided by this module is the ability to start a
provider application with a set of interactions. Since this is done
in a subprocess, any configuration must be passed in through files.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))


import contextlib
import json
import logging
import os
import pickle
import shutil
import socket
import subprocess
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import flask
import requests
from flask import request
from yarl import URL

import pact.constants  # type: ignore[import-untyped]
from tests.v3.compatibility_suite.util import serialize

if TYPE_CHECKING:
    from tests.v3.compatibility_suite.util import InteractionDefinition

if sys.version_info < (3, 11):
    from datetime import timezone

    UTC = timezone.utc
else:
    from datetime import UTC


logger = logging.getLogger(__name__)

version_var = ContextVar("version_var", default="0")


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

            provider_state_path = self.provider_dir / "provider_state"
            if provider_state_path.exists():
                state = provider_state_path.read_text()
                assert request.args["state"] == state

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
