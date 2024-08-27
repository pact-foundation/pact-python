"""
This module provides test cases and example usage for the HTTP consumer in version 3.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator

import pytest
import requests

from pact.v3 import Pact


@pytest.fixture
def pact() -> Generator[Pact, None, None]:
    """
    Set up HTTP Pact Consumer.

    This fixtures sets up the HTTP Pact consumer and the pact it has with a
    provider. The consumer defines the expected http interactions it will receive from
    the provider, and the Python test suite verifies that the correct actions
    are taken.

    For each test case, the consumer defines the following:

    ```python

        pact_dir = Path(Path(__file__).parent.parent.parent / "pacts")
        pact = Pact("v3_http_consumer", "v3_http_provider")
        yield pact.with_specification("V3")
        pact.write_file(pact_dir)

    ```
    Returns a generator that yields the pact object and writes the pact file
    """
    pact_dir = Path(Path(__file__).parent.parent.parent / "pacts")
    pact = Pact("v3_http_consumer", "v3_http_provider")
    yield pact.with_specification("V3")
    pact.write_file(pact_dir)


# Example 1: GET request for existing user
def test_get_user(pact: Pact) -> None:
    """
    Test the GET request for retrieving user information.

    This test defines the expected interaction for a GET request to retrieve
    user information. It sets up the expected request and response from the
    provider and verifies that the response status code is 200.
    """
    # When setting up the expected response, the consumer should only define
    # what it needs from the provider (as opposed to the full schema). Should
    # the provider later decide to add or remove fields, Pact's consumer-driven
    # approach will ensure that interaction is still valid.

    expected_response_code = (
        200  # In this example, we only care about the response code
    )
    expected: Dict[str, Any] = {
        "id": 123,
        "name": "Verna Hampton",
        "created_on": datetime.now(tz=timezone.utc).isoformat(),
    }
    (
        pact.upon_receiving(
            "a request for user information"
        )  # Defining the interaction
        .given("user exists")  # Defining the provider state
        .with_request(method="GET", path="/users/123")
        .will_respond_with(200)
        .with_body(json.dumps(expected))
    )

    with pact.serve() as srv:
        response = requests.get(f"{srv.url}/users/123", timeout=5)

        assert response.status_code == expected_response_code
        assert expected["name"] == "Verna Hampton"


# Example 2: GET request for non-existing user
def test_get_non_existing_user(pact: Pact) -> None:
    """
    Test the GET request for retrieving user information.

    This test defines the expected interaction for a GET request to retrieve
    user information. It sets up the expected request and response from the
    provider and verifies that the response status code is 400.
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
