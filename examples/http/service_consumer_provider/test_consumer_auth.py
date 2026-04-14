"""
Consumer contract tests for `user-service` → `auth-service`.

This module defines the contract that
[`user_service`][examples.http.service_consumer_provider.user_service] (acting
as a *consumer*) expects `auth-service` (the *provider*) to honour. When these
tests run, Pact starts a mock server in place of `auth-service` and verifies
that
[`AuthClient`][examples.http.service_consumer_provider.auth_client.AuthClient]
makes exactly the requests specified here and can handle the responses.

The generated Pact file (written to the `pacts/` directory) would normally be
published to a Pact Broker so that the `auth-service` team can run provider
verification against it. In this self-contained example the file is consumed
locally by the provider verification tests.

For background on consumer testing, see the [Pact consumer test
guide](https://docs.pact.io/5-minute-getting-started-guide#scope-of-a-consumer-pact-test).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from examples.http.service_consumer_provider.auth_client import AuthClient
from pact import Pact

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


@pytest.fixture
def pact(pacts_path: Path) -> Generator[Pact, None, None]:
    """
    Pact fixture for `user-service` as consumer of `auth-service`.

    Creates a V4 Pact between `user-service` (consumer) and `auth-service`
    (provider). Each test in this module can define one or more expected
    interactions on the returned `Pact` object; the mock provider will validate
    that the consumer code sends exactly those requests and handles the
    responses correctly. After the test, the contract is written to *pacts_path*
    for use in provider verification.

    Args:
        pacts_path:
            Directory where the generated Pact file is written.

    Yields:
        Pact configured for `user-service` → `auth-service`.
    """
    pact = Pact("user-service", "auth-service").with_specification("V4")
    yield pact
    pact.write_file(pacts_path)


@pytest.mark.parametrize(
    ("password", "expected_valid"),
    [
        pytest.param("correct-horse-battery-staple", True, id="valid"),
        pytest.param("wrong-password", False, id="invalid"),
    ],
)
def test_validate_credentials(
    pact: Pact,
    password: str,
    *,
    expected_valid: bool,
) -> None:
    """
    Verify the `AuthClient` contract for both valid and invalid credentials.

    This parametrised test covers two interactions in a single contract:

    - **Valid credentials**: `auth-service` responds `{"valid": true}`, and
      [`AuthClient.validate_credentials`][examples.http.service_consumer_provider.auth_client.AuthClient.validate_credentials]
      returns `True`.
    - **Invalid credentials**: `auth-service` responds `{"valid": false}`, and
      `AuthClient.validate_credentials` returns `False`.

    Both cases map to the same endpoint (`POST /auth/validate`) but are modelled
    as separate Pact interactions with different provider states. This ensures
    that `auth-service` must support both outcomes, not just the happy path.

    Args:
        pact:
            Pact fixture for `user-service` → `auth-service`.

        password:
            Password sent to `auth-service`; determines which provider state
            (and therefore which mock response) is used.

        expected_valid:
            The validation result the consumer expects to receive and act on.
    """
    state = (
        "user credentials are valid"
        if expected_valid
        else "user credentials are invalid"
    )

    (
        pact
        .upon_receiving(f"Credential validation for {state}")
        .given(state)
        .with_request("POST", "/auth/validate")
        .with_body(
            {
                "username": "alice",
                "password": password,
            },
            content_type="application/json",
        )
        .will_respond_with(200)
        .with_body(
            {
                "valid": expected_valid,
                "subject": "alice",
            },
            content_type="application/json",
        )
    )

    with pact.serve() as srv:
        client = AuthClient(str(srv.url))
        assert client.validate_credentials("alice", password) is expected_valid
