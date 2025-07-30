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

This also showcases how Pact tests differ from merely testing adherence to an
OpenAPI specification. The Pact tests are more concerned with the practical use
of the API, rather than the formally defined specification. The User class
defined here has additional fields which are not used by the consumer. Should
the provider later decide to add or remove fields, Pact's consumer-driven
testing will provide feedback on whether the consumer is compatible with the
provider's changes.

Note that the code in this module is agnostic of Pact (i.e., this would be your
production code). The `pact-python` dependency only appears in the tests. This
is because the consumer is not concerned with Pact, only the tests are.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Annotated, Any, Optional

from pydantic import BaseModel, PlainSerializer

from fastapi import FastAPI, HTTPException

app = FastAPI()
logger = logging.getLogger(__name__)


class User(BaseModel):
    """User data class."""

    id: int
    name: str
    created_on: Annotated[
        datetime,
        PlainSerializer(
            lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
            return_type=str,
            when_used="json",
        ),
    ]
    email: Optional[str]
    ip_address: Optional[str]
    hobbies: list[str]
    admin: bool

    def __post_init__(self) -> None:
        """
        Validate the User data.

        This performs the following checks:

        - The name cannot be empty
        - The id must be a positive integer

        Raises:
            ValueError: If any of the above checks fail.
        """
        if not self.name:
            msg = "User must have a name"
            raise ValueError(msg)

        if self.id < 0:
            msg = "User ID must be a positive integer"
            raise ValueError(msg)

    def __repr__(self) -> str:
        """Return the user's name."""
        return f"User({self.id}:{self.name})"


"""
As this is a simple example, we'll use a simple dict to represent a database.
This would be replaced with a real database in a real application.

When testing the provider in a real application, the calls to the database would
be mocked out to avoid the need for a real database. An example of this can be
found in the [test suite][examples.tests.test_01_provider_fastapi].
"""
FAKE_DB: dict[int, User] = {}


@app.get("/users/{uid}")
async def get_user_by_id(uid: int) -> User:
    """
    Fetch a user by their ID.

    Args:
        uid: The ID of the user to fetch

    Returns:
        The user data if found, HTTP 404 if not
    """
    user = FAKE_DB.get(uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users/")
async def create_new_user(user: dict[str, Any]) -> User:
    """
    Create a new user .

    Args:
        user: The user data to create

    Returns:
        The status code 200 and user data if successfully created, HTTP 404 if not
    """
    if "id" in user:
        raise HTTPException(status_code=400, detail="ID should not be provided.")
    uid = len(FAKE_DB)
    FAKE_DB[uid] = User(
        id=uid,
        name=user["name"],
        created_on=datetime.now(tz=timezone.utc),
        email=user.get("email"),
        ip_address=user.get("ip_address"),
        hobbies=user.get("hobbies", []),
        admin=user.get("admin", False),
    )
    return FAKE_DB[uid]


@app.delete("/users/{uid}", status_code=204)
async def delete_user(uid: int):  # noqa: ANN201
    """
     Delete an existing user .

    Args:
        uid: The ID of the user to delete

    Returns:
        The status code 204, HTTP 404 if not
    """
    if uid not in FAKE_DB:
        raise HTTPException(status_code=404, detail="User not found")

    del FAKE_DB[uid]
