"""
Consumer contract tests for `frontend-web` → `user-service`.

This module defines the contract that `frontend-web` (acting as a *consumer*)
expects [`user_service`][examples.http.service_consumer_provider.user_service]
(the *provider*) to honour. When these tests run, Pact starts a mock server in
place of `user-service` and verifies that
[`FrontendClient`][examples.http.service_consumer_provider.frontend_client.FrontendClient]
makes exactly the requests specified here and can handle the responses.

The generated Pact file is used by the provider verification test in
[`test_provider`][examples.http.service_consumer_provider.test_provider], which
runs the real `user-service` and replays these interactions against it.

For background on consumer testing, see the [Pact consumer test
guide](https://docs.pact.io/5-minute-getting-started-guide#scope-of-a-consumer-pact-test).
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
    Pact fixture for `frontend-web` as consumer of `user-service`.

    Creates a V4 Pact between `frontend-web` (consumer) and `user-service`
    (provider). Each test in this module defines one or more expected
    interactions on the returned `Pact` object; Pact validates that
    `FrontendClient` sends exactly those requests and handles the responses
    correctly. After the test, the contract is written to *pacts_path* for
    provider verification.

    Args:
        pacts_path:
            Directory where the generated Pact file is written.

    Yields:
        Pact configured for `frontend-web` → `user-service`.
    """
    pact = Pact("frontend-web", "user-service").with_specification("V4")
    yield pact
    pact.write_file(pacts_path)


def test_create_account_success(pact: Pact) -> None:
    """
    Verify `FrontendClient` behaviour when credentials are valid.

    This test defines the happy-path interaction: `frontend-web` POSTs an
    account creation request with valid credentials, and `user-service` responds
    with `201 Created` and the new account details.

    Note the use of `match.int(1001)` for the `id` field. This tells Pact to
    verify that the field *type* is an integer, not that the value is exactly
    `1001`. This makes the contract resilient to auto-incremented IDs while
    still ensuring the consumer receives a numeric identifier it can work with.

    The provider state `"auth accepts credentials"` signals to the provider
    verification test (see
    [`test_provider`][examples.http.service_consumer_provider.test_provider])
    that it must configure a stub `auth-service` that accepts the supplied
    credentials.
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
    Verify `FrontendClient` behaviour when credentials are invalid.

    This test defines the failure-path interaction: `frontend-web` POSTs an
    account creation request with invalid credentials, and `user-service`
    responds with `401 Unauthorized`. The consumer is expected to propagate the
    error as a `requests.HTTPError`.

    Testing error paths in Pact contracts is important: it ensures the provider
    contract covers not just the happy path but also the error responses that
    consumers must handle gracefully.

    The provider state `"auth rejects credentials"` signals to the provider
    verification test that the stub `auth-service` must reject the supplied
    credentials.
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
