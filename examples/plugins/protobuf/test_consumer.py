"""
Consumer test using Protobuf plugin with Pact Python v3.

This module demonstrates how to write a consumer test using the Pact protobuf
plugin with Pact Python's v3 API. The protobuf plugin allows Pact to handle
Protocol Buffer messages as request and response payloads, enabling contract
testing for services that communicate using protobuf serialization.

This example builds on the address book domain model from the [protobuf.dev
tutorial](https://protobuf.dev/getting-started/pythontutorial/) and shows how to
test a consumer that retrieves Person data from a provider service using
protobuf-serialized messages over HTTP.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import requests

from examples.plugins.proto.person_pb2 import Person
from examples.plugins.protobuf import address_book
from pact import Pact

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


@pytest.fixture
def pact(pacts_path: Path) -> Generator[Pact, None, None]:
    """
    Set up the Pact fixture with protobuf plugin.

    This fixture configures a Pact instance for consumer testing with the
    protobuf plugin enabled. The protobuf plugin allows Pact to understand and
    handle Protocol Buffer message serialization for both request and response
    payloads.

    The fixture uses the V4 specification which provides full support for
    plugins and content type matching.

    Yields:
        The configured Pact instance for protobuf consumer tests.
    """
    pact = (
        Pact("protobuf_consumer", "protobuf_provider")
        .with_specification("V4")
        .using_plugin("protobuf")
    )
    yield pact
    pact.write_file(pacts_path)


def test_get_person_by_id(pact: Pact) -> None:
    """
    Test retrieving a Person by ID using protobuf serialization.

    This test defines the expected interaction for a GET request to retrieve a
    specific person from the address book. The response will be a protobuf-
    serialized Person message.

    The test demonstrates:

    -   Using the protobuf plugin to handle binary protobuf content
    -   Matching on protobuf message structure and content
    -   Deserializing the protobuf response for validation

    The provider state ensures that a person with ID 1 exists in the system,
    corresponding to Alice from our sample address book.
    """
    sample_address_book = address_book()
    alice = sample_address_book.people[0]
    expected_protobuf_data = alice.SerializeToString()

    (
        pact.upon_receiving("a request to get person by ID")
        .given("person with the given ID exists", user_id=1)
        .with_request("GET", "/person/1")
        .will_respond_with(200)
        .with_header("Content-Type", "application/x-protobuf")
        .with_binary_body(expected_protobuf_data, "application/x-protobuf")
    )

    with pact.serve() as srv:
        # NOTE: We use the `requests` library here to demonstrate the
        # principles; however, in a real-world scenario, you would be using the
        # actual client code that interacts with the provider service. This
        # ensures that you are testing the consumer's behaviour.
        response = requests.get(f"{srv.url}/person/1", timeout=5)

        # Verify response
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/x-protobuf"

        # Deserialize the protobuf response and then verify its content
        person = Person()
        person.ParseFromString(response.content)

        assert person.id == 1
        assert person.name == "Alice"
        assert person.email == "alice@gmail.com"
        assert len(person.phones) == 2

        assert person.phones[0].number == "123-456-7890"
        assert person.phones[0].type == Person.PhoneType.PHONE_TYPE_HOME
        assert person.phones[1].number == "987-654-3210"
        assert person.phones[1].type == Person.PhoneType.PHONE_TYPE_MOBILE


def test_get_nonexistent_person(pact: Pact) -> None:
    """
    Test retrieving a non-existent Person by ID.

    This test verifies the provider's behavior when requesting a person that
    doesn't exist in the address book. The provider should return a 404 status
    code with an appropriate error message as a JSON response.
    """
    (
        pact.upon_receiving("a request to get non-existent person")
        .given("person with the given ID does not exist", user_id=999)
        .with_request("GET", "/person/999")
        .will_respond_with(404)
        .with_header("Content-Type", "application/json")
        .with_body({"detail": "Person not found"})
    )

    with pact.serve() as srv:
        # NOTE: Again, we use the `requests` library to simulate the consumer's
        # request to the provider service. A real-world consumer would instead
        # use its own client and check that the appropriate error message is
        # raised and/or handled.
        response = requests.get(f"{srv.url}/person/999", timeout=5)

        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"
        assert response.json() == {"detail": "Person not found"}
