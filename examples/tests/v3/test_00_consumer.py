"""
HTTP consumer test using Pact Python v3.

This module demonstrates how to write a consumer test using Pact Python's
upcoming version 3. Pact, being a consumer-driven testing tool, requires that
the consumer define the expected interactions with the provider.

In this example, the consumer defined in `src/consumer.py` is tested against a
mock provider. The mock provider is set up by Pact and is used to ensure that
the consumer is making the expected requests to the provider. Once these
interactions are validated, the contracts can be published to a Pact Broker
where they can be re-run against the provider to ensure that the provider is
compliant with the contract.

A good source for understanding the consumer tests is the [Pact Consumer Test
section](https://docs.pact.io/5-minute-getting-started-guide#scope-of-a-consumer-pact-test)
of the Pact documentation.
"""

import json
from collections.abc import Generator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
import requests

from examples.src.consumer import UserConsumer
from pact.v3 import Pact, match


@pytest.fixture
def pact() -> Generator[Pact, None, None]:
    """
    Set up the Pact fixture.

    This fixture configures the Pact instance for the consumer test. It defines
    where the pact file will be written and the consumer and provider names.
    This fixture also sets the Pact specification to `V4` (the latest version).

    The use of `yield` allows this function to return the Pact instance to be
    used in the test cases, and then for this function to continue running after
    the test cases have completed. This is useful for writing the pact file
    after the test cases have run.

    Yields:
        The Pact instance for the consumer tests.
    """
    pact_dir = Path(Path(__file__).parent.parent.parent / "pacts")
    pact = Pact("v3_http_consumer", "v3_http_provider")
    yield pact.with_specification("V4")
    pact.write_file(pact_dir)


def test_get_existing_user(pact: Pact) -> None:
    """
    Retrieve an existing user's details.

    This test defines the expected interaction for a GET request to retrieve
    user information. It sets up the expected request and response from the
    provider and verifies that the response status code is 200.

    When setting up the expected response, the consumer should only define what
    it needs from the provider (as opposed to the full schema). Should the
    provider later decide to add or remove fields, Pact's consumer-driven
    approach will ensure that interaction is still valid.

    The use of the `given` method allows the consumer to define the state of the
    provider before the interaction. In this case, the provider is in a state
    where the user exists and can be retrieved. By contrast, the same HTTP
    request with a different `given` state is expected to return a 404 status
    code as shown in
    [`test_get_non_existent_user`](#test_get_non_existent_user).
    """
    expected: dict[str, Any] = {
        "id": 123,
        "name": "Verna Hampton",
        "created_on": match.datetime(
            # Python datetime objects are automatically formatted
            datetime.now(tz=timezone.utc),
            format="%Y-%m-%dT%H:%M:%S%z",
        ),
    }
    (
        pact.upon_receiving("a request for user information")
        .given("user exists")
        .with_request(method="GET", path="/users/123")
        .will_respond_with(200)
        .with_body(expected)
    )

    with pact.serve() as srv:
        client = UserConsumer(str(srv.url))
        user = client.get_user(123)
        assert user.id == 123
        assert user.name == "Verna Hampton"


def test_get_non_existent_user(pact: Pact) -> None:
    """
    Test the GET request for retrieving user information.

    This test defines the expected interaction for a GET request to retrieve
    user information when that user does not exist in the provider's database.
    It is the counterpart to the
    [`test_get_existing_user`](#test_get_existing_user) and showcases how the
    same request can have different responses based on the provider's state.

    It is up to the specific use case to determine whether negative scenarios
    should be tested, and to what extent. Certain common negative scenarios
    include testing for non-existent resources, unauthorized access attempts may
    be useful to ensure that the consumer handles these cases correctly; but it
    is generally infeasible to test all possible negative scenarios.
    """
    expected_response_code = 404
    (
        pact.upon_receiving("a request for user information")
        .given("user doesn't exists")
        .with_request(method="GET", path="/users/2")
        .will_respond_with(404)
    )

    with pact.serve() as srv:
        response = requests.get(f"{srv.url}/users/2", timeout=5)

        assert response.status_code == expected_response_code


def test_create_user(pact: Pact) -> None:
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
        "created_on": match.datetime(
            # Python datetime objects are automatically formatted
            datetime.now(tz=timezone.utc),
            format="%Y-%m-%dT%H:%M:%S%z",
        ),
    }

    (
        pact.upon_receiving("a request to create a new user")
        .given("the specified user doesn't exist")
        .with_request(method="POST", path="/users/")
        .with_body(json.dumps(body), content_type="application/json")
        .will_respond_with(status=200)
        .with_body(content_type="application/json", body=expected_response)
    )

    with pact.serve() as srv:
        client = UserConsumer(str(srv.url))
        user = client.create_user(name="Verna Hampton")
        assert user.id > 0
        assert user.name == "Verna Hampton"
        assert user.created_on


def test_delete_request_to_delete_user(pact: Pact) -> None:
    """
    Test the DELETE request for deleting a user.

    This test defines the expected interaction for a DELETE request to delete
    a user. It sets up the expected request and response from the provider,
    including the request body and headers, and verifies that the response
    status code is 200 and the response body matches the expected user data.
    """
    (
        pact.upon_receiving("a request for deleting user")
        .given("user is present in DB")
        .with_request(method="DELETE", path="/users/124")
        .will_respond_with(204)
    )

    with pact.serve() as srv:
        client = UserConsumer(str(srv.url))
        client.delete_user(124)
