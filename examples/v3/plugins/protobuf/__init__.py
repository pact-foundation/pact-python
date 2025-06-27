"""
Protocol Buffers Plugin Example for Pact Python v3.

This module provides an example of how to use Pact plugins to handle different
content types in contract testing. Specifically, this example demonstrates the
use of the protobuf plugin to test interactions involving Protocol Buffers
(protobuf) message serialization, building on the [protobuf.dev Python
tutorial](https://protobuf.dev/getting-started/pythontutorial/).

## What are Protocol Buffers?

Protocol Buffers (protobuf) is a language-neutral, platform-neutral extensible
mechanism for serializing structured data developed by Google. It can be thought
of as similar to XML or JSON, but with pre-defined schemas and a binary format
that is more efficient for both storage and transmission.

The data structure is defined in a `.proto` file, which specifies the messages,
fields, and types. This is then compiled into source code in various programming
languages, allowing you to work with structured data in a type-safe manner. This
examples defines a simple address book and person schema within `person.proto`
and the `person.py` and `person.pyi` files have been generated from it using

```console
protoc --python_out=. --pyi_out=. person.proto
```

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

## The Protobuf Plugin Example

This example builds an address book application using the same domain model as
the [protobuf.dev
tutorial](https://protobuf.dev/getting-started/pythontutorial/).

It defines a simple address book schema using Protocol Buffers and demonstrates
how to use the Pact protobuf plugin to test interactions involving protobuf
messages. It is assumed that you have a basic understanding of Pact and Protocol
Buffers.
"""

from ..proto.person_pb2 import AddressBook, Person


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
