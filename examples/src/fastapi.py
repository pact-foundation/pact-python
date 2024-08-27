"""
FastAPI provider example.

This modules defines a simple
[provider](https://docs.pact.io/getting_started/terminology#service-provider)
which will be tested with Pact in the [provider
test][examples.tests.test_01_provider_fastapi]. As Pact is a consumer-driven
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

import logging
from typing import Any, Dict

from pydantic import BaseModel

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()
logger = logging.getLogger(__name__)


class User(BaseModel):
    """
    User data class.

    This class is used to represent a user in the application. It is used to
    validate the incoming data and to dump the data to a dictionary.
    """

    id: int | None = None
    name: str
    email: str


"""
As this is a simple example, we'll use a simple dict to represent a database.
This would be replaced with a real database in a real application.

When testing the provider in a real application, the calls to the database would
be mocked out to avoid the need for a real database. An example of this can be
found in the [test suite][examples.tests.test_01_provider_fastapi].
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


@app.post("/users/")
async def create_new_user(user: User) -> JSONResponse:
    """
    Create a new user .

    Args:
        user: The user data to create

    Returns:
        The status code 200 and user data if successfully created, HTTP 404 if not
    """
    if user.id is not None:
        raise HTTPException(status_code=400, detail="ID should not be provided.")
    new_uid = len(FAKE_DB)
    FAKE_DB[new_uid] = user.model_dump()

    return JSONResponse(status_code=200, content=FAKE_DB[new_uid])


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):  # noqa: ANN201
    """
     Delete an existing user .

    Args:
        user_id: The ID of the user to delete

    Returns:
        The status code 204, HTTP 404 if not
    """
    if user_id not in FAKE_DB:
        raise HTTPException(status_code=404, detail="User not found")

    del FAKE_DB[user_id]
