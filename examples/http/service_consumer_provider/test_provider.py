"""
Provider verification for user-service against frontend-web contract.
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
    Test verifier used by provider state handlers.
    """

    def __init__(self, valid: bool) -> None:
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
    Run the FastAPI server used for provider verification.

    Returns:
        Base URL for user-service.
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


def set_auth_accepts(_parameters: dict[str, object] | None) -> None:
    """
    Provider state: auth-service accepts credentials.

    Args:
        _parameters:
            Optional Pact state parameters.
    """
    reset_state()
    set_auth_verifier(StubAuthVerifier(valid=True))


def set_auth_rejects(_parameters: dict[str, object] | None) -> None:
    """
    Provider state: auth-service rejects credentials.

    Args:
        _parameters:
            Optional Pact state parameters.
    """
    reset_state()
    set_auth_verifier(StubAuthVerifier(valid=False))


def test_provider(app_server: str, pacts_path: Path) -> None:
    """
    Verify user-service against frontend-web consumer contract.

    Args:
        app_server:
            Base URL of the running provider.

        pacts_path:
            Directory containing generated Pact files.
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
