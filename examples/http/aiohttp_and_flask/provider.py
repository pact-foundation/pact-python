"""
Flask provider example.

This modules defines a simple
[provider](https://docs.pact.io/getting_started/terminology#service-provider)
implemented with [`flask`][flask] which will be tested with Pact in the
[provider test][examples.http.aiohttp_and_flask.test_provider]. As Pact is a
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
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, ClassVar, Literal

from flask import Flask, Response, abort, jsonify, request

if TYPE_CHECKING:
    import werkzeug.exceptions

logger = logging.getLogger(__name__)


@dataclass()
class User:
    """
    Represents a user in the provider system.

    This class is used to model user data as it might exist in a real
    application. In a provider context, the data model may contain more fields
    than are required by any single consumer. This example demonstrates how a
    provider can serve multiple consumers with different data needs, and how
    consumer-driven contract testing (such as with Pact) helps ensure
    compatibility as the provider evolves.
    """

    id: int
    name: str
    created_on: datetime
    email: str | None
    ip_address: str | None
    hobbies: list[str]
    admin: bool

    def __post_init__(self) -> None:
        """
        Validate the User data.

        Ensures that the user has a non-empty name and a positive integer ID.

        Raises:
          ValueError:
            If the name is empty or the ID is not positive.
        """
        if not self.name:
            msg = "User must have a name"
            raise ValueError(msg)

        if self.id < 0:
            msg = "User ID must be a positive integer"
            raise ValueError(msg)

    def __repr__(self) -> str:
        """
        Return a string representation of the user.

        Returns:
            The user's name and ID as a string.
        """
        return f"User(id={self.id!r}, name={self.name!r})"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the user's data to a dictionary.

        Returns:
            A dictionary containing the user's data, suitable for JSON
            serialization.
        """
        return {
            "id": self.id,
            "name": self.name,
            "created_on": self.created_on.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "email": self.email,
            "ip_address": self.ip_address,
            "hobbies": self.hobbies,
            "admin": self.admin,
        }


class UserDb:
    """
    A simple in-memory user database abstraction for demonstration purposes.

    This class simulates a user database using a class-level dictionary. In a
    real application, this would interface with a persistent database or
    external user service. For testing, calls to this class can be mocked to
    avoid the need for a real database. See the [test
    suite][examples.http.aiohttp_and_flask.test_provider] for an example.
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


app = Flask(__name__)


@app.errorhandler(404)
def not_found(error: werkzeug.exceptions.NotFound) -> tuple[Response, Literal[404]]:
    """
    Handle 404 Not Found errors.

    Args:
        error:
            The error that occurred.

    Returns:
        A JSON response with error details and HTTP 404 status code.
    """
    return jsonify({
        "title": "Not Found",
        "status": 404,
        "detail": error.description,
        "instance": request.path,
    }), 404


@app.errorhandler(400)
def bad_request(error: werkzeug.exceptions.BadRequest) -> tuple[Response, Literal[400]]:
    """
    Handle 400 Bad Request errors.

    Args:
        error:
            The error that occurred.

    Returns:
        A JSON response with error details and HTTP 400 status code.
    """
    return jsonify({
        "title": "Bad Request",
        "status": 400,
        "detail": error.description,
        "instance": request.path,
    }), 400


@app.route("/users/<int:uid>")
def get_user_by_id(uid: int) -> Response:
    """
    Retrieve a user by their ID.

    Args:
        uid:
            The ID of the user to fetch.

    Returns:
        A JSON response containing the user data if found.

    Raises:
        werkzeug.exceptions.NotFound:
            If the user does not exist in the database.
    """
    logger.debug("GET /users/%s", uid)
    user = UserDb.get(uid)
    if not user:
        abort(404, description="User not found")
    return jsonify(user.to_dict())


@app.route("/users/", methods=["POST"])
def create_user() -> tuple[Response, int]:
    """
    Create a new user in the system.

    The user ID is automatically assigned.

    Returns:
        A JSON response containing the created user data with HTTP 201 status
        code.

    Raises:
        werkzeug.exceptions.BadRequest:
            If the request body is not valid JSON or required fields are
            missing.
    """
    logger.debug("GET /users/")
    if request.json is None:
        abort(400, description="Invalid JSON data")

    user: dict[str, Any] = request.json
    new_user = User(
        id=UserDb.new_user_id(),
        name=user["name"],
        created_on=datetime.now(tz=timezone.utc),
        email=user.get("email"),
        ip_address=user.get("ip_address"),
        hobbies=user.get("hobbies", []),
        admin=user.get("admin", False),
    )
    UserDb.create(new_user)
    return jsonify(new_user.to_dict()), 201


@app.route("/users/<int:uid>", methods=["DELETE"])
def delete_user(uid: int) -> tuple[str | Response, int]:
    """
    Delete a user by their ID.

    If the user does not exist, a 404 error is returned.

    Args:
        uid:
            The ID of the user to delete.

    Returns:
        An empty response with HTTP 204 status code if successful.

    Raises:
        werkzeug.exceptions.NotFound:
            If the user does not exist in the database.
    """
    logger.debug("DELETE /users/%s", uid)
    if UserDb.get(uid) is None:
        abort(404, description="User not found")
    UserDb.delete(uid)
    return "", 204
