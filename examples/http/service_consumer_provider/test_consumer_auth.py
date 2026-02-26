"""
Consumer contract tests for user-service -> auth-service.
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
    Pact fixture for user-service as consumer.

    Args:
        pacts_path:
            Directory where Pact files are written.

    Yields:
        Pact configured for user-service -> auth-service.
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
def test_validate_credentials(pact: Pact, password: str, expected_valid: bool) -> None:
    """
    Verify user-service auth client contract.

    Args:
        pact:
            Pact fixture.

        password:
            Password sent to auth-service.

        expected_valid:
            Expected validation result.
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
