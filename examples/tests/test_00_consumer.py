"""
Test the consumer with Pact.

This module tests the consumer defined in `src/consumer.py` against a mock
provider. The mock provider is set up by Pact, and is used to ensure that the
consumer is making the expected requests to the provider, and that the provider
is responding with the expected responses. Once these interactions are
validated, the contracts can be published to a Pact Broker. The contracts can
then be used to validate the provider's interactions.

A good resource for understanding the consumer tests is the [Pact Consumer
Test](https://docs.pact.io/5-minute-getting-started-guide#scope-of-a-consumer-pact-test)
section of the Pact documentation.
"""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

import pytest
import requests
from yarl import URL

from examples.src.consumer import User, UserConsumer
from pact import Consumer, Format, Like, Provider

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from pact.pact import Pact

logger = logging.getLogger(__name__)

MOCK_URL = URL("http://localhost:8080")


@pytest.fixture
def user_consumer() -> UserConsumer:
    """
    Returns an instance of the UserConsumer class.

    As we do not want to stand up all of the consumer's dependencies, we direct
    the consumer to use Pact's mock provider. This allows us to define what
    requests the consumer will make to the provider, and what responses the
    provider will return.

    The ability for the client to specify the expected response from the
    provider is critical to Pact's consumer-driven approach as it allows the
    consumer to declare the minimal response it requires from the provider (even
    if the provider is returning more data than the consumer needs).
    """
    return UserConsumer(str(MOCK_URL))


@pytest.fixture(scope="module")
def pact(broker: URL, pact_dir: Path) -> Generator[Pact, Any, None]:
    """
    Set up Pact.

    In order to test the consumer in isolation, Pact sets up a mock version of
    the provider. This mock provider will expect to receive defined requests
    and will respond with defined responses.

    The fixture here simply defines the Consumer and Provider, and sets up the
    mock provider. With each test, we define the expected request and response
    from the provider as follows:

    ```python
    pact.given("UserA exists and is not an admin") \
        .upon_receiving("A request for UserA") \
        .with_request("get", "/users/123") \
        .will_respond_with(200, body=Like(expected))
    ```
    """
    consumer = Consumer("UserConsumer")
    pact = consumer.has_pact_with(
        Provider("UserProvider"),
        pact_dir=pact_dir,
        publish_to_broker=True,
        # Mock service configuration
        host_name=MOCK_URL.host,
        port=MOCK_URL.port,
        # Broker configuration
        broker_base_url=str(broker),
        broker_username=broker.user,
        broker_password=broker.password,
    )

    pact.start_service()
    yield pact
    pact.stop_service()


def test_get_existing_user(pact: Pact, user_consumer: UserConsumer) -> None:
    """
    Test request for an existing user.

    This test defines the expected request and response from the provider. The
    provider will be expected to return a response with a status code of 200,
    """
    # When setting up the expected response, the consumer should only define
    # what it needs from the provider (as opposed to the full schema). Should
    # the provider later decide to add or remove fields, Pact's consumer-driven
    # approach will ensure that interaction is still valid.
    expected: dict[str, Any] = {
        "id": Format().integer,
        "name": "Verna Hampton",
        "created_on": Format().iso_8601_datetime(),
    }

    (
        pact.given("user 123 exists")
        .upon_receiving("a request for user 123")
        .with_request("get", "/users/123")
        .will_respond_with(200, body=Like(expected))
    )

    with pact:
        user = user_consumer.get_user(123)

        assert isinstance(user, User)
        assert user.name == "Verna Hampton"

        pact.verify()


def test_get_unknown_user(pact: Pact, user_consumer: UserConsumer) -> None:
    expected = {"detail": "User not found"}

    (
        pact.given("user 123 doesn't exist")
        .upon_receiving("a request for user 123")
        .with_request("get", "/users/123")
        .will_respond_with(404, body=Like(expected))
    )

    with pact:
        with pytest.raises(requests.HTTPError) as excinfo:
            user_consumer.get_user(123)
        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == HTTPStatus.NOT_FOUND
        pact.verify()


def test_create_user(pact: Pact, user_consumer: UserConsumer) -> None:
    """
    Test the POST request for creating a new user.

    This test defines the expected interaction for a POST request to create
    a new user. It sets up the expected request and response from the provider,
    including the request body and headers, and verifies that the response
    status code is 200 and the response body matches the expected user data.
    """
    body = {"name": "Verna Hampton"}
    expected_response: dict[str, Any] = {
        "id": 124,
        "name": "Verna Hampton",
        "created_on": Format().iso_8601_datetime(),
    }

    (
        pact.given("create user 124")
        .upon_receiving("A request to create a new user")
        .with_request(
            method="POST",
            path="/users/",
            body=body,
            headers={"Content-Type": "application/json"},
        )
        .will_respond_with(
            status=200,
            body=Like(expected_response),
        )
    )

    with pact:
        user = user_consumer.create_user(name="Verna Hampton")
        assert user.id > 0
        assert user.name == "Verna Hampton"
        assert user.created_on

        pact.verify()


def test_delete_request_to_delete_user(pact: Pact, user_consumer: UserConsumer) -> None:
    """
    Test the DELETE request for deleting a user.

    This test defines the expected interaction for a DELETE request to delete
    a user. It sets up the expected request and response from the provider,
    including the request body and headers, and verifies that the response
    status code is 200 and the response body matches the expected user data.
    """
    (
        pact.given("delete the user 124")
        .upon_receiving("a request for deleting user")
        .with_request(method="DELETE", path="/users/124")
        .will_respond_with(status=204)
    )

    with pact:
        user_consumer.delete_user(124)

        pact.verify()
