"""
Consumer contract tests using Pact.

This module demonstrates how to test a consumer (see
[`consumer.py`][examples.http.requests_and_fastapi.consumer]) against a mock
provider using Pact. The mock provider is set up by Pact to validate that the
consumer makes the expected requests and can handle the provider's responses.
Once validated, the contract can be published to a Pact Broker for use in
provider verification.

For more information on consumer testing with Pact, see the [Pact Consumer
Test](https://docs.pact.io/5-minute-getting-started-guide#scope-of-a-consumer-pact-test)
section of the Pact documentation.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import pytest
import requests

from examples.http.requests_and_fastapi.consumer import UserClient
from pact import Pact, match

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

logger = logging.getLogger(__name__)


@pytest.fixture
def pact(pacts_path: Path) -> Generator[Pact, None, None]:
    """
    Set up a Pact mock provider for consumer tests.

    This fixture defines the consumer and provider, and sets up the mock
    provider using Pact. Each test can then define the expected request and
    response using the Pact DSL. This allows the consumer to be tested in
    isolation from the real provider, ensuring that the contract is correct
    before integration.

    Args:
        pacts_path:
            The path where the generated pact file will be written.

    Yields:
        A Pact object for use in tests.
    """
    pact = Pact("aiohttp-consumer", "flask-provider").with_specification("V4")
    yield pact
    pact.write_file(pacts_path)


def test_get_user(pact: Pact) -> None:
    """
    Test the GET request for a user.

    This test defines the expected interaction for a GET request for a user. It
    demonstrates how to use Pact to specify the expected request and response,
    and how to verify that the consumer code can handle the response correctly.
    """
    response: dict[str, object] = {
        "id": match.int(123),
        "name": match.str("Alice"),
        "created_on": match.datetime(),
    }
    (
        pact.upon_receiving("A user request")
        .given("the user exists", id=123, name="Alice")
        .with_request("GET", "/users/123")
        .will_respond_with(200)
        .with_body(response, content_type="application/json")
    )

    with (
        pact.serve() as srv,
        UserClient(str(srv.url)) as client,
    ):
        user = client.get_user(123)
        assert user.name == "Alice"


def test_get_unknown_user(pact: Pact) -> None:
    """
    Test the GET request for an unknown user.

    This test defines the expected interaction for a GET request for a user that
    does not exist. It verifies that the consumer handles error responses as
    expected.
    """
    response = {"detail": "User not found"}
    (
        pact.upon_receiving("A request for an unknown user")
        .given("the user doesn't exist", id=123)
        .with_request("GET", "/users/123")
        .will_respond_with(404)
        .with_body(response, content_type="application/json")
    )

    with (
        pact.serve() as srv,
        UserClient(str(srv.url)) as client,
        pytest.raises(requests.HTTPError),
    ):
        client.get_user(123)


def test_create_user(pact: Pact) -> None:
    """
    Test the POST request for creating a new user.

    This test defines the expected interaction for a POST request to create a
    new user. It demonstrates how to specify the request and response, and how
    to verify that the consumer can handle the provider's response. This also
    shows how Pact can support multiple requests and responses within a single
    test case.
    """
    payload: dict[str, Any] = {"name": "Bob"}
    response: dict[str, Any] = {
        "id": match.int(1000),
        "name": "Bob",
        "created_on": match.datetime(datetime.now(tz=timezone.utc)),
    }

    (
        pact.upon_receiving("A request to create a new user")
        .with_request("POST", "/users")
        .with_body(payload, content_type="application/json")
        .will_respond_with(201)
        .with_body(response, content_type="application/json")
    )

    with pact.serve() as srv, UserClient(str(srv.url)) as client:
        user = client.create_user(name="Bob")
        assert user.id == 1000


def test_delete_user(pact: Pact) -> None:
    """
    Test the DELETE request for deleting a user.

    This test defines the expected interaction for a DELETE request to delete a
    user. It demonstrates how to use Pact to specify the expected request and
    response, and how to verify that the consumer code can handle the response
    correctly.
    """
    (
        pact.upon_receiving("A user deletion request")
        .given("the user exists", id=124, name="Bob")
        .with_request("DELETE", "/users/124")
        .will_respond_with(204)
    )

    with pact.serve() as srv, UserClient(str(srv.url)) as client:
        client.delete_user(124)
