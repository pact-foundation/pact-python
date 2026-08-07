"""
gRPC Plugin Example for Pact Python v3.

This module provides an example of how to use Pact plugins to perform contract
testing over a non-HTTP transport. Specifically, this example demonstrates the
use of the protobuf plugin to test true gRPC interactions, where messages are
exchanged using Protocol Buffers over the gRPC transport (HTTP/2).

For detailed information about Protocol Buffers, the generated files, and the
domain model used in this example, see the [`proto`][examples.plugins.proto]
module documentation. The same `person.proto` definition (and its generated
`person_pb2` and `person_pb2_grpc` modules) is shared with the
[`protobuf`][examples.plugins.protobuf] example.

## gRPC and Pact

The [`protobuf`][examples.plugins.protobuf] example demonstrates how to test
interactions where protobuf messages are sent as the body of regular HTTP
requests and responses. This example goes one step further and tests a real
gRPC service.

gRPC builds on top of Protocol Buffers and HTTP/2 to provide a high-performance
remote procedure call (RPC) framework. Rather than sending protobuf messages as
opaque HTTP bodies, gRPC defines services with strongly-typed methods, each with
a request and response message. The Pact protobuf plugin understands this and is
able to:

-   Stand up a mock gRPC server for the consumer test, responding to RPC calls
    with the expected response message.
-   Replay the consumer's RPC calls against a real provider gRPC server during
    the provider verification.

## This Example

This example demonstrates how to use the Pact protobuf plugin to test a gRPC
service defined by the `AddressBookService` in `person.proto`. It is assumed
that you have a basic understanding of Pact, Protocol Buffers, and gRPC.

The sample data used throughout this example is shared with the protobuf example
through the [`address_book`][examples.plugins.protobuf.address_book] helper.
"""

from __future__ import annotations

from pathlib import Path

import examples.plugins.proto

PROTO_DIR = Path(examples.plugins.proto.__file__).parent
"""
Directory containing the shared `person.proto` definition.

The protobuf plugin requires the path to the `.proto` file in order to
understand the gRPC service and message definitions. This is shared with the
[`protobuf`][examples.plugins.protobuf] example rather than being duplicated.
"""

PROTO_FILE = PROTO_DIR / "person.proto"
"""
Path to the shared `person.proto` definition.
"""
