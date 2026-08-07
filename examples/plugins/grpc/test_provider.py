"""
Provider test using the gRPC transport with Pact Python v3.

This module demonstrates how to write a provider test for a true gRPC service
using the Pact protobuf plugin with Pact Python's v3 API. Unlike the
[`protobuf`][examples.plugins.protobuf] example, which verifies protobuf
messages exchanged over HTTP, this example stands up a real gRPC server
implementing the `AddressBookService` and verifies it against the consumer's
contract over the gRPC transport.

The provider test runs the actual gRPC server and uses the Pact Verifier to
replay the consumer's recorded RPC calls against it, verifying that the provider
responds with the expected protobuf messages.

This example shows how to:

-   Implement a gRPC service using the shared `person.proto` definition.
-   Run the gRPC server in a background thread for testing.
-   Use the Pact Verifier with the `grpc` transport and the protobuf plugin.
-   Handle provider states for setting up test data.
"""

from __future__ import annotations

from concurrent import futures
from typing import TYPE_CHECKING, Any, Literal

import grpc
import pytest

from examples.plugins.proto import person_pb2_grpc
from examples.plugins.proto.person_pb2 import (
    AddPersonResponse,
    AddressBook,
    GetPersonResponse,
    ListPeopleResponse,
)
from examples.plugins.protobuf import address_book
from pact import Verifier

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

# Global variable to hold our mock address book data
# In a real application, this would be a database or other data store
MOCK_ADDRESS_BOOK: AddressBook | None = None


class AddressBookService(person_pb2_grpc.AddressBookServiceServicer):
    """
    Concrete implementation of the `AddressBookService` gRPC service.

    This class implements the service methods defined in `person.proto`. It
    serves as the provider for the address book gRPC service, backed by the
    in-memory `MOCK_ADDRESS_BOOK` data store.

    This code would typically be in a separate module within your application,
    but for the sake of this example, it is included directly within the test
    module.
    """

    def GetPerson(  # noqa: N802 (gRPC method name)
        self,
        request: Any,  # noqa: ANN401
        context: grpc.ServicerContext,
    ) -> GetPersonResponse:
        """
        Get a person by ID.

        Args:
            request:
                The `GetPersonRequest` message containing the person ID.

            context:
                The gRPC servicer context.

        Returns:
            A `GetPersonResponse` containing the requested person.
        """
        if MOCK_ADDRESS_BOOK is not None:
            for person in MOCK_ADDRESS_BOOK.people:
                if person.id == request.person_id:
                    return GetPersonResponse(person=person)

        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Person not found")
        return GetPersonResponse()

    def ListPeople(  # noqa: N802 (gRPC method name)
        self,
        request: Any,  # noqa: ANN401, ARG002
        context: grpc.ServicerContext,  # noqa: ARG002
    ) -> ListPeopleResponse:
        """
        List all people in the address book.

        Args:
            request:
                The `ListPeopleRequest` message.

            context:
                The gRPC servicer context.

        Returns:
            A `ListPeopleResponse` containing all known people.
        """
        people = MOCK_ADDRESS_BOOK.people if MOCK_ADDRESS_BOOK else []
        return ListPeopleResponse(people=people)

    def AddPerson(  # noqa: N802 (gRPC method name)
        self,
        request: Any,  # noqa: ANN401
        context: grpc.ServicerContext,  # noqa: ARG002
    ) -> AddPersonResponse:
        """
        Add a new person to the address book.

        Args:
            request:
                The `AddPersonRequest` message containing the person to add.

            context:
                The gRPC servicer context.

        Returns:
            An `AddPersonResponse` containing the added person.
        """
        return AddPersonResponse(person=request.person)


@pytest.fixture(scope="session")
def grpc_server() -> Generator[int, None, None]:
    """
    Fixture to start the gRPC server for testing.

    The server is bound to an explicit IPv4 address, as the protobuf plugin's
    gRPC verifier does not accept a hostname.

    Yields:
        The port on which the gRPC server is listening.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    person_pb2_grpc.add_AddressBookServiceServicer_to_server(
        AddressBookService(),
        server,
    )
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    try:
        yield port
    finally:
        server.stop(grace=None)


def test_provider(grpc_server: int, pacts_path: Path) -> None:
    """
    Test the gRPC provider against the consumer contract.

    This test uses the Pact Verifier to replay the consumer's recorded gRPC
    interactions against the running provider service. The protobuf plugin is
    used to encode and decode the messages over the gRPC transport.

    The test:

    1.   Configures the Verifier with the `grpc` transport.
    2.   Points the verifier to the pact file generated by the consumer.
    3.   Sets up state handlers to prepare test data.
    4.   Verifies all interactions match the contract.
    """
    pact_file = pacts_path / "grpc_consumer-grpc_provider.json"

    # NOTE: The verifier requires a base (HTTP) transport in addition to the
    # gRPC transport. The first transport registered provides the provider's
    # base location, while the gRPC transport is used to replay the recorded
    # gRPC interactions (those whose `transport` is `grpc` in the pact file).
    verifier = (
        Verifier("grpc_provider", host="127.0.0.1")
        .add_transport(protocol="http", port=grpc_server, scheme="http")
        .add_transport(protocol="grpc", port=grpc_server)
        .add_source(pact_file)
        .state_handler(
            {
                "person with the given ID exists": state_person_exists,
            },
            teardown=True,
        )
    )

    verifier.verify()


def state_person_exists(
    action: Literal["setup", "teardown"],
    parameters: dict[str, Any] | None = None,
) -> None:
    """
    Handle provider state for when a person with the given ID exists.

    Args:
        action:
            Either "setup" or "teardown".

        parameters:
            Dictionary containing the user_id key.
    """
    global MOCK_ADDRESS_BOOK  # noqa: PLW0603

    if action == "setup":
        MOCK_ADDRESS_BOOK = address_book()
        if user_id := parameters.get("user_id") if parameters else None:
            assert any(person.id == user_id for person in MOCK_ADDRESS_BOOK.people), (
                f"Person with ID {user_id} does not exist in address book"
            )
        else:
            msg = "User ID not provided"
            raise AssertionError(msg)
    elif action == "teardown":
        MOCK_ADDRESS_BOOK = None
