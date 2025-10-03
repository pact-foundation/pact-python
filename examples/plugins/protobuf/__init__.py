"""
Protocol Buffers Plugin Example for Pact Python v3.

This module provides an example of how to use Pact plugins to handle different
content types in contract testing. Specifically, this example demonstrates the
use of the protobuf plugin to test interactions involving Protocol Buffers
(protobuf) message serialization.

For detailed information about Protocol Buffers, the generated files, and the
domain model used in this example, see the [`proto`][examples.plugins.proto]
module documentation.

## Pact and the Plugin Ecosystem

Pact is traditionally focused on HTTP-based interactions with text-based
(primarily JSON) payloads. However, modern microservices architectures often use
various content types and transport mechanisms beyond simple text over HTTP. To
address this, Pact allows for extensibility through a plugin system that supports
different content types and protocols.

Pact plugins extend the core functionality of Pact to support different content
types, transport protocols, and matching strategies. The plugin system allows
Pact to:

-   Handle different content types (e.g., protobuf)
-   Support various transport mechanisms (e.g., gRPC)
-   Provide specialized matching rules for different data formats
-   Enable extensibility without modifying the core Pact library

## This Example

This example demonstrates how to use the Pact protobuf plugin to test
interactions involving protobuf messages sent over HTTP.  It is assumed that you
have a basic understanding of Pact and Protocol Buffers.
"""

from __future__ import annotations

from examples.plugins.proto.person_pb2 import AddressBook, Person


def address_book() -> AddressBook:
    """
    Create a sample address book.

    This function constructs an `AddressBook` instance containing three
    `Person` instances:

    -   Alice with ID 1
    -   Bob with ID 2
    -   Charlie with ID 3
    """
    alice = Person(
        name="Alice",
        id=1,
        email="alice@gmail.com",
        phones=[
            Person.PhoneNumber(
                number="123-456-7890", type=Person.PhoneType.PHONE_TYPE_HOME
            ),
            Person.PhoneNumber(
                number="987-654-3210", type=Person.PhoneType.PHONE_TYPE_MOBILE
            ),
        ],
    )
    bob = Person(
        name="Bob",
        id=2,
        email="bob@work.com",
        phones=[
            Person.PhoneNumber(
                number="555-555-5555", type=Person.PhoneType.PHONE_TYPE_WORK
            )
        ],
    )
    charlie = Person(
        name="Charlie",
        id=3,
        email="charlie@example.com",
        phones=[
            Person.PhoneNumber(
                number="111-222-3333", type=Person.PhoneType.PHONE_TYPE_UNSPECIFIED
            )
        ],
    )
    return AddressBook(people=[alice, bob, charlie])
