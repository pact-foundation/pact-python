"""
Consumer contract tests for frontend-web -> user-service.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import requests

from examples.http.service_consumer_provider.frontend_client import FrontendClient
from pact import Pact, match

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


@pytest.fixture
def pact(pacts_path: Path) -> Generator[Pact, None, None]:
    """
    Pact fixture for frontend-web as consumer.

    Args:
        pacts_path:
            Directory where Pact files are written.

    Yields:
        Pact configured for frontend-web -> user-service.
    """
    pact = Pact("frontend-web", "user-service").with_specification("V4")
    yield pact
    pact.write_file(pacts_path)


def test_create_account_success(pact: Pact) -> None:
    """
    Verify frontend behaviour when credentials are valid.

    Args:
        pact:
            Pact fixture.
    """
    (
        pact
        .upon_receiving("A request to create an account")
        .given("auth accepts credentials")
        .with_request("POST", "/accounts")
        .with_body(
            {
                "username": "alice",
                "password": "correct-horse-battery-staple",
            },
            content_type="application/json",
        )
        .will_respond_with(201)
        .with_body(
            {
                "id": match.int(1001),
                "username": "alice",
                "status": "created",
            },
            content_type="application/json",
        )
    )

    with pact.serve() as srv:
        client = FrontendClient(str(srv.url))
        account = client.create_account("alice", "correct-horse-battery-staple")
        assert account.id == 1001
        assert account.username == "alice"
        assert account.status == "created"


def test_create_account_invalid_credentials(pact: Pact) -> None:
    """
    Verify frontend behaviour when credentials are invalid.

    Args:
        pact:
            Pact fixture.
    """
    (
        pact
        .upon_receiving("A request with invalid credentials")
        .given("auth rejects credentials")
        .with_request("POST", "/accounts")
        .with_body(
            {
                "username": "alice",
                "password": "wrong-password",
            },
            content_type="application/json",
        )
        .will_respond_with(401)
        .with_body({"detail": "Invalid credentials"}, content_type="application/json")
    )

    with pact.serve() as srv:
        client = FrontendClient(str(srv.url))
        with pytest.raises(requests.HTTPError):
            client.create_account("alice", "wrong-password")
