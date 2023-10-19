"""
FastAPI provider example.

This modules defines a simple
[provider](https://docs.pact.io/getting_started/terminology#service-provider)
which will be tested with Pact in the [provider
test](../tests/test_01_provider_fastapi.py). As Pact is a consumer-driven
framework, the consumer defines the contract which the provider must then
satisfy.

The provider is the application which receives requests from another service
(the consumer) and returns a response. In this example, we have a simple
endpoint which returns a user's information from a (fake) database.

Note that the code in this module is agnostic of Pact. The `pact-python`
dependency only appears in the tests. This is because the consumer is not
concerned with Pact, only the tests are.
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

"""
As this is a simple example, we'll use a simple dict to represent a database.
This would be replaced with a real database in a real application.

When testing the provider in a real application, the calls to the database would
be mocked out to avoid the need for a real database. An example of this can be
found in the [test suite](../tests/test_01_provider_fastapi.py).
"""
FAKE_DB: Dict[int, Dict[str, Any]] = {}


@app.get("/users/{uid}")
async def get_user_by_id(uid: int) -> JSONResponse:
    """
    Fetch a user by their ID.

    Args:
        uid: The ID of the user to fetch

    Returns:
        The user data if found, HTTP 404 if not
    """
    user = FAKE_DB.get(uid)
    if not user:
        return JSONResponse(status_code=404, content={"error": "User not found"})
    return JSONResponse(status_code=200, content=user)
