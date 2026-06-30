# Example: Protobuf Contract Testing with the Protobuf Plugin

This example demonstrates contract testing for [Protocol
Buffers](https://protobuf.dev/) (protobuf) messages exchanged over plain HTTP,
using the [Pact protobuf
plugin](https://github.com/pactflow/pact-protobuf-plugin). The consumer requests
a `Person` from an address book service and receives a protobuf-serialized
response, which Pact verifies against the provider.

It is designed to be pedagogical, highlighting how Pact's plugin system extends
contract testing beyond text-based (e.g. JSON) payloads to binary content types
such as protobuf.

For a fully protobuf **and** gRPC example, where the same `person.proto`
definition drives a true gRPC service over the gRPC transport, see the
[`grpc`](../grpc/) example.

## Overview

-   [**Proto definitions**][examples.plugins.proto]: The shared `person.proto`
    message definitions and their generated stubs, also used by the
    [`grpc`](../grpc/) example.
-   [**Consumer Tests**][examples.plugins.protobuf.test_consumer]: Contract
    definition and consumer testing against a mock HTTP server.
-   [**Provider Tests**][examples.plugins.protobuf.test_provider]: Provider
    verification of a real FastAPI server against the contract.

Use the above links to view additional documentation within.

## What This Example Demonstrates

### Consumer Side

-   Describing the expected protobuf message and registering it as the binary
    body of an HTTP response.
-   Standing up a mock HTTP server with `pact.serve()`.
-   Calling the mock server and deserializing the protobuf response for
    validation.

### Provider Side

-   Implementing a FastAPI provider that responds with protobuf-serialized
    messages (`application/x-protobuf`).
-   Running the server in a background thread for verification.
-   Verifying the provider with the Pact Verifier.
-   Provider state setup for isolated, repeatable verification.

## How Protobuf-over-HTTP Works

Pact is traditionally focused on text-based payloads (primarily JSON). The
protobuf plugin extends this by teaching Pact how to encode, decode, and match
protobuf messages. In this example, the messages are carried as the binary body
of regular HTTP requests and responses, so the standard HTTP transport is used —
only the _content type_ is handled by the plugin.

This differs from the [`grpc`](../grpc/) example, which goes one step further:
there the protobuf plugin understands the `.proto` _service_ definition and
exercises a real gRPC service over the gRPC transport (HTTP/2), rather than
sending protobuf messages as opaque HTTP bodies.

## Prerequisites

-   Python 3.10 or higher
-   A dependency manager ([uv](https://docs.astral.sh/uv/) recommended,
    [pip](https://pip.pypa.io/en/stable/) also works)
-   The [Pact protobuf
    plugin](https://github.com/pactflow/pact-protobuf-plugin), which provides
    protobuf content handling. Pact downloads the plugin automatically the first
    time it is needed, so no manual step is usually required. To pre-install it
    (e.g. for offline use), use the [Pact plugin
    CLI](https://github.com/pact-foundation/pact-plugins/tree/main/cli):

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
-   [Protocol Buffers Documentation](https://protobuf.dev/)
-   [FastAPI Documentation](https://fastapi.tiangolo.com/)
-   [pytest Documentation](https://docs.pytest.org/)
