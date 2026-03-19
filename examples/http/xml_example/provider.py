"""
FastAPI XML provider example.

This module defines a simple
[provider](https://docs.pact.io/getting_started/terminology#service-provider)
implemented with [`fastapi`](https://fastapi.tiangolo.com/) which will be tested
with Pact in the [provider test][examples.http.xml_example.test_provider].

The provider receives requests from the consumer and returns XML responses built
using the standard library [`xml.etree.ElementTree`][xml.etree.ElementTree]
module.

Note that the code in this module is agnostic of Pact (i.e., this would be your
production code). The `pact-python` dependency only appears in the tests.
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
    """

    id: int
    name: str


class UserDb:
    """
    A simple in-memory user database abstraction for demonstration purposes.
    """

    _db: ClassVar[dict[int, User]] = {}

    @classmethod
    def create(cls, user: User) -> None:
        """
        Add a new user to the database.
        """
        cls._db[user.id] = user

    @classmethod
    def delete(cls, user_id: int) -> None:
        """
        Delete a user from the database by their ID.

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
