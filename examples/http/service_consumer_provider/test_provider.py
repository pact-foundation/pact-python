"""
Provider verification for `user-service` against the `frontend-web` contract.

This module runs the Pact verifier against the real
[`user_service`][examples.http.service_consumer_provider.user_service] FastAPI
application to confirm that it honours the contract defined by the consumer
tests in
[`test_consumer_frontend`][examples.http.service_consumer_provider.test_consumer_frontend].

## How provider verification works

Pact replays each interaction from the contract file against the running
`user-service`. Before each interaction it calls the appropriate *provider state
handler* to put the service in the right state. For example, the interaction `"A
request to create an account"` requires the state `"auth accepts credentials"`,
so Pact calls `set_auth_accepts` first, which installs a
[`StubAuthVerifier`][examples.http.service_consumer_provider.test_provider.StubAuthVerifier]
that always returns `True`.

This lets the entire `user-service` run for real while still being independent
of a live `auth-service`. The
[`CredentialsVerifier`][examples.http.service_consumer_provider.user_service.CredentialsVerifier]
protocol in `user_service.py` is the seam that makes this possible.

For more background, see the [Pact provider test
guide](https://docs.pact.io/5-minute-getting-started-guide#scope-of-a-provider-pact-test)
and the documentation for
[`Verifier.state_handler`][pact.verifier.Verifier.state_handler].
"""

from __future__ import annotations

import contextlib
import time
from threading import Thread
from typing import TYPE_CHECKING

import pytest
import requests
import uvicorn

import pact._util
from examples.http.service_consumer_provider.user_service import (
    app,
    reset_state,
    set_auth_verifier,
)
from pact import Verifier

if TYPE_CHECKING:
    from pathlib import Path


class StubAuthVerifier:
    """
    In-process stub for `auth-service`, used by provider state handlers.

    Rather than starting a real `auth-service` during provider verification, the
    tests replace the
    [`AuthClient`][examples.http.service_consumer_provider.auth_client.AuthClient]
    with this stub via
    [`set_auth_verifier`][examples.http.service_consumer_provider.user_service.set_auth_verifier].
    The stub satisfies the
    [`CredentialsVerifier`][examples.http.service_consumer_provider.user_service.CredentialsVerifier]
    protocol and returns a fixed result for every call, making provider states
    simple and deterministic.

    The real `AuthClient` behaviour is separately verified by the consumer tests
    in
    [`test_consumer_auth`][examples.http.service_consumer_provider.test_consumer_auth].
    """

    def __init__(self, *, valid: bool) -> None:
        """
        Create a stub verifier.

        Args:
            valid:
                Result to return for all validations.
        """
        self._valid = valid

    def validate_credentials(self, username: str, password: str) -> bool:
        """
        Validate credentials.

        Args:
            username:
                Ignored in this stub.

            password:
                Ignored in this stub.

        Returns:
            The configured validation result.
        """
        del username, password
        return self._valid


@pytest.fixture(scope="session")
def app_server() -> str:
    """
    Start the `user-service` FastAPI application for provider verification.

    Launches the application in a daemon thread so it is torn down when the test
    process exits. The fixture polls the `/docs` endpoint until the server is
    accepting connections (up to 5 seconds), which avoids race conditions when
    the verifier immediately begins replaying interactions.

    Returns:
        Base URL of the running `user-service`, e.g. `http://localhost:54321`.
    """
    hostname = "localhost"
    port = pact._util.find_free_port()  # noqa: SLF001
    Thread(
        target=uvicorn.run,
        args=(app,),
        kwargs={"host": hostname, "port": port},
        daemon=True,
    ).start()

    base_url = f"http://{hostname}:{port}"
    for _ in range(50):
        with contextlib.suppress(requests.RequestException):
            response = requests.get(f"{base_url}/docs", timeout=0.2)
            if response.status_code < 500:
                return base_url
        time.sleep(0.1)

    msg = f"user-service did not start at {base_url}"
    raise RuntimeError(msg)


def set_auth_accepts(parameters: dict[str, object] | None = None) -> None:
    """
    Provider state: `auth-service` accepts credentials.

    Configures `user-service` so that any credential validation attempt
    succeeds. This models the scenario where the upstream `auth-service`
    considers the supplied credentials valid, allowing account creation to
    proceed normally.

    Called by the Pact verifier before interactions that carry the provider
    state `"auth accepts credentials"`.

    Args:
        parameters:
            Optional Pact state parameters. Not used by this state.
    """
    del parameters
    reset_state()
    set_auth_verifier(StubAuthVerifier(valid=True))


def set_auth_rejects(parameters: dict[str, object] | None = None) -> None:
    """
    Provider state: `auth-service` rejects credentials.

    Configures `user-service` so that any credential validation attempt fails.
    This models the scenario where the upstream `auth-service` considers the
    supplied credentials invalid, causing `user-service` to return `401
    Unauthorized`.

    Called by the Pact verifier before interactions that carry the provider
    state `"auth rejects credentials"`.

    Args:
        parameters:
            Optional Pact state parameters. Not used by this state.
    """
    del parameters
    reset_state()
    set_auth_verifier(StubAuthVerifier(valid=False))


def test_provider(app_server: str, pacts_path: Path) -> None:
    """
    Verify `user-service` against the `frontend-web` consumer contract.

    This test uses the Pact verifier to replay each interaction from the
    contract generated by
    [`test_consumer_frontend`][examples.http.service_consumer_provider.test_consumer_frontend]
    against the running `user-service`. Before each interaction, the verifier
    calls the appropriate provider state handler to configure the service. After
    all interactions have been replayed, Pact reports any mismatches.

    Provider state handlers are the mechanism Pact uses to decouple verification
    from infrastructure: instead of wiring up a real `auth-service`, each state
    handler installs a `StubAuthVerifier` that returns a predetermined result.
    This makes verification fast, deterministic, and free of external
    dependencies.

    Note that `teardown=False` is set on the state handler because the handlers
    use `reset_state()` at the *start* of each setup call. Explicit teardown is
    unnecessary when the next setup always resets to a clean slate.

    Args:
        app_server:
            Base URL of the running `user-service` provider.

        pacts_path:
            Directory containing the Pact contract files to verify against.
    """
    verifier = (
        Verifier("user-service")
        .add_source(pacts_path)
        .add_transport(url=app_server)
        .state_handler(
            {
                "auth accepts credentials": set_auth_accepts,
                "auth rejects credentials": set_auth_rejects,
            },
            teardown=False,
        )
    )

    verifier.verify()
