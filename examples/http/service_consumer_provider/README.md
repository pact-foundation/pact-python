# Service as Consumer and Provider

This example demonstrates a common microservice pattern where one service plays both roles in contract testing:

- **Provider** to a frontend client (`frontend-web -> user-service`)
- **Consumer** of an upstream auth service (`user-service -> auth-service`)

## Overview

- [**Frontend Client**][examples.http.service_consumer_provider.frontend_client]: Consumer-facing client used by `frontend-web`
- [**Auth Client**][examples.http.service_consumer_provider.auth_client]: Upstream client used by `user-service`
- [**User Service**][examples.http.service_consumer_provider.user_service]: FastAPI app under test
- [**Frontend Consumer Tests**][examples.http.service_consumer_provider.test_consumer_frontend]: Defines frontend expectations of `user-service`
- [**Auth Consumer Tests**][examples.http.service_consumer_provider.test_consumer_auth]: Defines `user-service` expectations of `auth-service`
- [**Provider Verification**][examples.http.service_consumer_provider.test_provider]: Verifies `user-service` against the frontend pact

## What This Example Demonstrates

- One service owning two separate contracts in opposite directions
- Consumer tests for each dependency boundary
- Provider verification with state handlers that model upstream auth behaviour
- Contract scope focused on behaviour used by each consumer

## Running the Example

### Using uv (Recommended)

```console
uv run --group test pytest
```

### Using pip

1. Create and activate a virtual environment:

   ```console
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   .venv\Scripts\activate     # On Windows
   ```

2. Install dependencies:

   ```console
   pip install -U pip
   pip install --group test -e .
   ```

3. Run tests:

   ```console
   pytest
   ```

## Related Documentation

- [Pact Documentation](https://docs.pact.io/)
- [Provider States](https://docs.pact.io/getting_started/provider_states)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
