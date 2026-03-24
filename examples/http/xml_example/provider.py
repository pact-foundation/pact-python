"""
FastAPI XML provider example.

This module defines a simple
[provider](https://docs.pact.io/getting_started/terminology#service-provider)
implemented with [`fastapi`](https://fastapi.tiangolo.com/) which will be tested
with Pact in the [provider test][examples.http.xml_example.test_provider]. As
Pact is a consumer-driven framework, the consumer defines the contract which the
provider must then satisfy.

The provider receives requests from the consumer and returns XML responses built
using the standard library [`xml.etree.ElementTree`][xml.etree.ElementTree]
module. Serialisation is handled manually rather than via FastAPI's built-in
JSON serialisation, since FastAPI does not natively support XML response bodies.

This also showcases how Pact tests differ from merely testing adherence to an
OpenAPI specification. The Pact tests are concerned with the practical use of
the API from the consumer's perspective. The `User` model here could contain
additional fields in a real application; if the provider later adds or removes
fields, Pact's consumer-driven testing will verify that the consumer remains
compatible with those changes.

Note that the code in this module is agnostic of Pact (i.e., this would be your
production code). The `pact-python` dependency only appears in the tests. This
is because the provider is not concerned with Pact, only the tests are.
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import ClassVar

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import Response

logger = logging.getLogger(__name__)


@dataclass()
class User:
    """
    Represents a user in the provider system.

    This class uses a plain dataclass rather than Pydantic to keep the focus
    on the XML serialisation pattern. In a real FastAPI application you would
    typically use a Pydantic model to benefit from automatic validation and
    JSON serialisation; see the
    [`requests_and_fastapi`][examples.http.requests_and_fastapi.provider.User]
    example for that approach.

    The provider's model may contain more fields than any single consumer
    requires. This demonstrates how provider-side data can be richer than what
    appears in the consumer contract.
    """

    id: int
    name: str


class UserDb:
    """
    A simple in-memory user database abstraction for demonstration purposes.

    This class simulates a user database using a class-level dictionary. In a
    real application this would interface with a persistent database or external
    service. For testing, the state handlers in the [provider
    test][examples.http.xml_example.test_provider] populate and clean up this
    database directly, ensuring each contract interaction runs against a
    predictable state.
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
    def delete(cls, user_id: int) -> None:
        """
        Delete a user from the database by their ID.

        Args:
            user_id: The ID of the user to delete.

        Raises:
            KeyError: If the user does not exist.
        """
        if user_id not in cls._db:
            msg = f"User {user_id} does not exist."
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


app = FastAPI()


@app.get("/users/{uid}")
async def get_user_by_id(uid: int) -> Response:
    """
    Retrieve a user by their ID, returning an XML response.

    Args:
        uid:
            The user ID to retrieve.

    Raises:
        HTTPException: If the user is not found, a 404 error is raised.
    """
    logger.debug("GET /users/%s", uid)
    user = UserDb.get(uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    root = ET.Element("user")
    ET.SubElement(root, "id").text = str(user.id)
    ET.SubElement(root, "name").text = user.name
    return Response(
        content=ET.tostring(root, encoding="unicode"),
        media_type="application/xml",
    )
