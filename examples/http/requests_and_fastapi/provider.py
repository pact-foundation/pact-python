"""
FastAPI provider example.

This modules defines a simple
[provider](https://docs.pact.io/getting_started/terminology#service-provider)
implemented with [`fastapi`](https://fastapi.tiangolo.com/) which will be tested
with Pact in the [provider
test][examples.http.requests_and_fastapi.test_provider]. As Pact is a
consumer-driven framework, the consumer defines the contract which the provider
must then satisfy.

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
from typing import Any, ClassVar

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class User(BaseModel):
    """
    Represents a user in the provider system.

    This class models user data as it might exist in a real application. In a
    provider context, the data model may contain more fields than are required
    by any single consumer. This example demonstrates how a provider can serve
    multiple consumers with different data needs, and how consumer-driven
    contract testing (such as with Pact) helps ensure compatibility as the
    provider evolves.
    """

    id: int
    name: str
    created_on: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    email: str | None = None
    ip_address: str | None = None
    hobbies: list[str] = Field(default_factory=list)
    admin: bool = False

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: int) -> int:
        """
        Ensure the ID is a positive integer.
        """
        if value <= 0:
            msg = "ID must be a positive integer"
            raise ValueError(msg)
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """
        Ensure the name is not empty.
        """
        if not value:
            msg = "Name must not be empty"
            raise ValueError(msg)
        return value


class UserDb:
    """
    A simple in-memory user database abstraction for demonstration purposes.

    This class simulates a user database using a class-level dictionary. In a
    real application, this would interface with a persistent database or
    external user service. For testing, calls to this class can be mocked to
    avoid the need for a real database. See the [test
    suite][examples.http.requests_and_fastapi.test_provider] for an example.
    """

    _db: ClassVar[dict[int, User]] = {}

    @classmethod
    def create(cls, user: User) -> None:
        """
        Add a new user to the database.

        Args:
            user: The User instance to add.
        """
        cls._db[user.id] = user

    @classmethod
    def update(cls, user: User) -> None:
        """
        Update an existing user in the database.

        Args:
            user: The User instance with updated data.

        Raises:
            KeyError: If the user does not exist.
        """
        if user.id not in cls._db:
            msg = f"User with id {user.id} does not exist."
            raise KeyError(msg)
        cls._db[user.id] = user

    @classmethod
    def delete(cls, user_id: int) -> None:
        """
        Delete a user from the database by their ID.

        Args:
            user_id: The ID of the user to delete.

        Raises:
            KeyError: If the user does not exist.
        """
        if user_id not in cls._db:
            msg = f"User with id {user_id} does not exist."
            raise KeyError(msg)
        del cls._db[user_id]

    @classmethod
    def get(cls, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The User instance if found, else None.
        """
        return cls._db.get(user_id)

    @classmethod
    def new_user_id(cls) -> int:
        """
        Return a free user ID.
        """
        return max(cls._db.keys(), default=0) + 1


app = FastAPI()


@app.get("/users/{uid}")
async def get_user_by_id(uid: int) -> User:
    """
    Retrieve a user by their ID.

    Args:
        uid:
            The user ID to retrieve.

    Returns:
        A User instance representing the user with the given ID.

    Raises:
        HTTPException: If the user is not found, a 404 error is raised.
    """
    logger.debug("GET /users/%s", uid)
    user = UserDb.get(uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(data: dict[str, Any]) -> User:
    """
    Create a new user in the system.
    """
    logger.debug("POST /users/")

    if not data or "name" not in data:
        raise HTTPException(status_code=400, detail="Invalid JSON data")

    user = User(
        id=UserDb.new_user_id(),
        name=data["name"],
        created_on=datetime.now(tz=timezone.utc),
        email=data.get("email"),
        ip_address=data.get("ip_address"),
        hobbies=data.get("hobbies", []),
        admin=data.get("admin", False),
    )
    UserDb.create(user)
    return user


@app.delete("/users/{uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(uid: int):  # noqa: ANN201
    """
    Delete a user by their ID.

    Args:
        uid:
            The user ID to delete.

    Raises:
        HTTPException: If the user is not found, a 404 error is raised.
    """
    logger.debug("DELETE /users/%s", uid)
    if UserDb.get(uid) is None:
        raise HTTPException(status_code=404, detail="User not found")
    UserDb.delete(uid)
