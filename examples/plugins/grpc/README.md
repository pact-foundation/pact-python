# Example: gRPC Contract Testing with the Protobuf Plugin

This example demonstrates contract testing for a true [gRPC](https://grpc.io/)
service using the [Pact protobuf
plugin](https://github.com/pactflow/pact-protobuf-plugin). Unlike the
[`protobuf`](../protobuf/) example, which exchanges Protocol Buffer messages over
plain HTTP, this example tests the `AddressBookService` gRPC service end-to-end
over the gRPC transport (HTTP/2).

It is designed to be pedagogical, highlighting how Pact's plugin system extends
contract testing beyond HTTP to alternative transports such as gRPC.

## Overview

-   [**Proto definitions**][examples.plugins.proto]: The shared `person.proto`
    service definition and its generated stubs, reused from the
    [`protobuf`](../protobuf/) example.
-   [**Consumer Tests**][examples.plugins.grpc.test_consumer]: Contract
    definition and consumer testing against a mock gRPC server.
-   [**Provider Tests**][examples.plugins.grpc.test_provider]: Provider
    verification of a real gRPC server against the contract.

Use the above links to view additional documentation within.

## What This Example Demonstrates

### Consumer Side

-   Describing a gRPC interaction to the protobuf plugin using a JSON document
    that references the `.proto` file, the fully-qualified service method, and
    the expected request and response messages.
-   Standing up a mock gRPC server with `pact.serve(transport="grpc")`.
-   Calling the mock server with a generated gRPC client stub.
-   Writing the contract using the mock server (via `srv.write_file()`) so that
    the gRPC transport is recorded in the pact.

### Provider Side

-   Implementing the `AddressBookService` gRPC service using the shared
    `person.proto` definition.
-   Running the gRPC server in a background thread for verification.
-   Verifying the provider with the Pact Verifier over the `grpc` transport.
-   Provider state setup and teardown for isolated, repeatable verification.

## How gRPC Differs from the Protobuf Example

The [`protobuf`](../protobuf/) example sends protobuf-serialized messages as the
body of regular HTTP requests and responses. This example tests a real gRPC
service, where the protobuf plugin understands the service definition and:

-   Stands up a mock gRPC server for the consumer test, responding to RPC calls
    with the expected response message.
-   Replays the consumer's recorded RPC calls against a real provider gRPC
    server during verification.

The interaction is described to the plugin using the `application/grpc` content
type and a JSON document of the form:

```python
{
    "pact:proto": "/path/to/person.proto",
    "pact:proto-service": "AddressBookService/GetPerson",
    "pact:content-type": "application/grpc",
    "request": {"person_id": "matching(number, 1)"},
    "response": {"person": {"name": "matching(type, 'Alice')", ...}},
}
```

The `matching(...)` expressions instruct Pact to verify the structure and types
of the messages rather than their exact values, which is the recommended
approach for contract testing.

## Prerequisites

-   Python 3.10 or higher
-   A dependency manager ([uv](https://docs.astral.sh/uv/) recommended,
    [pip](https://pip.pypa.io/en/stable/) also works)
-   The [Pact protobuf
    plugin](https://github.com/pactflow/pact-protobuf-plugin), which provides
    both protobuf content handling and the gRPC transport. Pact downloads the
    plugin automatically the first time it is needed, so no manual step is
    usually required. To pre-install it (e.g. for offline use), use the [Pact
    plugin CLI](https://github.com/pact-foundation/pact-plugins/tree/main/cli):

    ```console
    pact-plugin-cli install protobuf
    ```

## Running the Example

Run the tests from this directory, exactly like the other examples. Although the
tests reuse the shared proto definitions from the top-level `examples` package,
the example's `pyproject.toml` makes the repository root importable so they run
standalone.

### Using uv (Recommended)

We recommend using [uv](https://docs.astral.sh/uv/) to manage the virtual
environment and dependencies. The following command will automatically set up
the virtual environment, install dependencies, and execute the tests:

```console
uv run --group test pytest
```

### Using pip

If using the [`venv`][venv] module, the required steps are:

1.  Create and activate a virtual environment:

    ```console
    python -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    .venv\Scripts\activate     # On Windows
    ```

2.  Install dependencies:

    ```console
    pip install -U pip  # Pip 25.1 is required
    pip install --group test -e .
    ```

3.  Run tests:

    ```console
    pytest
    ```

## Related Documentation

-   [Pact Documentation](https://docs.pact.io/)
-   [Pact Protobuf/gRPC Plugin](https://github.com/pactflow/pact-protobuf-plugin)
-   [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
-   [Protocol Buffers Documentation](https://protobuf.dev/)
-   [pytest Documentation](https://docs.pytest.org/)
