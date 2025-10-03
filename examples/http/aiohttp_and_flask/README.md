# aiohttp and Flask Example

This example demonstrates contract testing between an asynchronous [`aiohttp`](https://docs.aiohttp.org/en/stable/)-based client (consumer) and a [Flask](https://flask.palletsprojects.com/en/stable/) web server (provider). It showcases modern Python patterns including async/await, type hints, and standalone dependency management.

## Overview

-   [**Consumer**][examples.http.aiohttp_and_flask.consumer]: An async HTTP client using aiohttp
-   [**Provider**][examples.http.aiohttp_and_flask.provider]: A Flask web server
-   [**Consumer Tests**][examples.http.aiohttp_and_flask.test_consumer]: Contract definition and consumer testing
-   [**Provider Tests**][examples.http.aiohttp_and_flask.test_provider]: Provider verification against contracts

Use the above links to view additional documentation within.

## What This Example Demonstrates

### Consumer Side

-   Async HTTP client implementation with aiohttp
-   Consumer contract testing with Pact mock servers
-   Handling different HTTP response scenarios (success, not found, etc.)
-   Modern Python async patterns

### Provider Side

-   Flask web server with RESTful endpoints
-   Provider verification against consumer contracts
-   Provider state setup for different test scenarios
-   Mock data management for testing

### Testing Patterns

-   Independent consumer and provider testing
-   Contract-driven development workflow
-   Error handling and edge case testing
-   Type safety with Python type hints

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

1.  Create the virtual environment and then activate it:

    ```console
    python -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    .venv\Scripts\activate     # On Windows
    ```

2.  Install the required dependencies in the virtual environment:

    ```console
    pip install -U pip  # Pip 25.1 is required
    pip install --group test -e .
    ```

3.  Run pytest:

    ```console
    pytest
    ```

## Related Documentation

-   [Pact Documentation](https://docs.pact.io/)
-   [aiohttp Documentation](https://docs.aiohttp.org/)
-   [Flask Documentation](https://flask.palletsprojects.com/)
-   [pytest Documentation](https://docs.pytest.org/)
