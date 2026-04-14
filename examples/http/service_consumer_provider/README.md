# Service as Consumer and Provider

This example demonstrates a common microservice pattern where one service plays both roles in contract testing:

-   **Provider** to a frontend client (`frontend-web → user-service`)
-   **Consumer** of an upstream auth service (`user-service → auth-service`)

## Overview

-   [**Frontend Client**][examples.http.service_consumer_provider.frontend_client]: Consumer-facing client used by `frontend-web`
-   [**Auth Client**][examples.http.service_consumer_provider.auth_client]: Upstream client used by `user-service` to call `auth-service`
-   [**User Service**][examples.http.service_consumer_provider.user_service]: FastAPI app under test (the service in the middle)
-   [**Frontend Consumer Tests**][examples.http.service_consumer_provider.test_consumer_frontend]: Defines `frontend-web`'s expectations of `user-service`
-   [**Auth Consumer Tests**][examples.http.service_consumer_provider.test_consumer_auth]: Defines `user-service`'s expectations of `auth-service`
-   [**Provider Verification**][examples.http.service_consumer_provider.test_provider]: Verifies `user-service` against the frontend pact

Use the links above to view detailed documentation within each file.

## What This Example Demonstrates

-   One service owning two separate contracts in opposite directions
-   Consumer tests for each dependency boundary
-   Provider verification with state handlers that model upstream `auth-service` behaviour without needing it to run
-   A `Protocol`-based seam that allows the real FastAPI application to run during verification while the upstream dependency is replaced in-process

## Running the Example

```console
uv run --group test pytest
```

## Related Documentation

-   [Pact Documentation](https://docs.pact.io/)
-   [Provider States](https://docs.pact.io/getting_started/provider_states)
-   [FastAPI Documentation](https://fastapi.tiangolo.com/)
-   [pytest Documentation](https://docs.pytest.org/)
