"""
Consumer test using the gRPC transport with Pact Python v3.

This module demonstrates how to write a consumer test for a true gRPC service
using the Pact protobuf plugin with Pact Python's v3 API. Unlike the
[`protobuf`][examples.plugins.protobuf] example, which sends protobuf messages
over HTTP, this example tests the `AddressBookService` gRPC service end-to-end:
the protobuf plugin stands up a mock gRPC server, and the consumer interacts
with it using a generated gRPC client stub.

The shared `person.proto` definition (and its generated stubs) from the
[`proto`][examples.plugins.proto] module is reused here, ensuring the consumer
and provider agree on the same service contract.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import grpc
import pytest

from examples.plugins.grpc import PROTO_FILE
from examples.plugins.proto.person_pb2 import GetPersonRequest, Person
from examples.plugins.proto.person_pb2_grpc import AddressBookServiceStub
from pact import Pact

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def pact() -> Pact:
    """
    Set up the Pact fixture with the protobuf plugin.

    This fixture configures a Pact instance for consumer testing with the
    protobuf plugin enabled. In addition to handling Protocol Buffer
    serialization, the plugin provides support for the gRPC transport, allowing
    Pact to stand up a mock gRPC server for the consumer test.

    The fixture uses the V4 specification which provides full support for
    plugins and alternative transports.

    Returns:
        The configured Pact instance for gRPC consumer tests.
    """
    return (
        Pact("grpc_consumer", "grpc_provider")
        .with_specification("V4")
        .using_plugin("protobuf")
    )


def test_get_person_by_id(pact: Pact, pacts_path: Path) -> None:
    """
    Test retrieving a Person by ID over gRPC.

    This test defines the expected gRPC interaction for the
    `AddressBookService.GetPerson` method. The interaction is described to the
    protobuf plugin using a JSON document that references the shared
    `person.proto` file, the fully-qualified service method, and the expected
    request and response messages.

    The matching rules (e.g. `matching(type, ...)`) instruct Pact to verify the
    structure and types of the messages rather than their exact values, which
    is the recommended approach for contract testing.
    """
    interaction_contents = {
        "pact:proto": str(PROTO_FILE),
        "pact:proto-service": "AddressBookService/GetPerson",
        "pact:content-type": "application/grpc",
        "request": {
            "person_id": "matching(number, 1)",
        },
        "response": {
            "person": {
                "name": "matching(type, 'Alice')",
                "id": "matching(number, 1)",
                "email": "matching(type, 'alice@gmail.com')",
                "phones": [
                    {
                        "number": "matching(type, '123-456-7890')",
                        "type": "matching(equalTo, 'PHONE_TYPE_HOME')",
                    },
                    {
                        "number": "matching(type, '987-654-3210')",
                        "type": "matching(equalTo, 'PHONE_TYPE_MOBILE')",
                    },
                ],
            }
        },
    }

    (
        pact
        .upon_receiving("a gRPC request to get person by ID", "Sync")
        .given("person with the given ID exists", user_id=1)
        .with_plugin_contents(interaction_contents, "application/grpc")
    )

    # NOTE: We bind the mock server to an explicit IPv4 address. The protobuf
    # plugin's gRPC mock server does not accept a hostname (such as
    # `localhost`), so an IP address must be provided.
    with pact.serve(addr="127.0.0.1", transport="grpc") as srv:
        # NOTE: We use a raw gRPC channel and the generated stub here to
        # demonstrate the principles; however, in a real-world scenario, you
        # would be using the actual client code that interacts with the provider
        # service. This ensures that you are testing the consumer's behaviour.
        with grpc.insecure_channel(f"{srv.host}:{srv.port}") as channel:
            stub = AddressBookServiceStub(channel)
            response = stub.GetPerson(GetPersonRequest(person_id=1))

        person = response.person
        assert person.id == 1
        assert person.name == "Alice"
        assert person.email == "alice@gmail.com"
        assert len(person.phones) == 2
        assert person.phones[0].number == "123-456-7890"
        assert person.phones[0].type == Person.PhoneType.PHONE_TYPE_HOME
        assert person.phones[1].number == "987-654-3210"
        assert person.phones[1].type == Person.PhoneType.PHONE_TYPE_MOBILE

        # NOTE: The pact file is written using the mock server (rather than the
        # Pact handle) so that the gRPC transport is recorded in the contract.
        # This allows the provider verification to replay the interaction over
        # gRPC rather than the default HTTP transport.
        srv.write_file(pacts_path, overwrite=True)
