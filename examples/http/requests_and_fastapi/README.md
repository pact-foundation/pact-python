# Example: requests Client and FastAPI Provider with Pact Contract Testing

This example demonstrates contract testing between a synchronous [`requests`](https://docs.python-requests.org/en/latest/)-based client (consumer) and a [FastAPI](https://fastapi.tiangolo.com/) web server (provider). It is designed to be pedagogical, showing modern Python patterns, type hints, and best practices for contract-driven development.

## Overview

-   [**Consumer**][examples.http.requests_and_fastapi.consumer]: Synchronous HTTP client using requests
-   [**Provider**][examples.http.requests_and_fastapi.provider]: FastAPI web server
-   [**Consumer Tests**][examples.http.requests_and_fastapi.test_consumer]: Contract definition and consumer testing with Pact
-   [**Provider Tests**][examples.http.requests_and_fastapi.test_provider]: Provider verification against contracts

Use the above links to view additional documentation within.

## What This Example Demonstrates

### Consumer Side

-   Synchronous HTTP client implementation with requests
-   Consumer contract testing with Pact mock servers
-   Handling different HTTP response scenarios (success, not found, etc.)
-   Modern Python patterns and type hints

### Provider Side

-   FastAPI web server with RESTful endpoints
-   Provider verification against consumer contracts
-   Provider state setup for different test scenarios
-   Mock data management for testing

### Testing Patterns

-   Independent consumer and provider testing
-   Contract-driven development workflow
-   Error handling and edge case testing
-   Type safety with Python type hints

## Pedagogical Context

This example is intended for software engineers and engineering managers who want to understand:

-   How contract testing works in practice
-   Why consumer-driven contracts are valuable
-   How to structure Python code for clarity and testability
-   The benefits of using requests and FastAPI for simple, modern HTTP services

## Prerequisites

-   Python 3.10 or higher
-   A dependency manager ([uv](https://docs.astral.sh/uv/) recommended, [pip](https://pip.pypa.io/en/stable/) also works)

## Running the Example

### Using uv (Recommended)

We recommend using [uv](https://docs.astral.sh/uv/) to manage the virtual env and manage dependencies. The following command will automatically set up the virtual environment, install dependencies, and then execute the command within the virtual environment:

```console
uv run --group test pytest
```

### Using pip

If using the [`venv`][venv] module, the steps require are:

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
-   [requests Documentation](https://docs.python-requests.org/)
-   [FastAPI Documentation](https://fastapi.tiangolo.com/)
-   [pytest Documentation](https://docs.pytest.org/)
