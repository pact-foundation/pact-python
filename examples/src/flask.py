"""
Flask provider example.

This modules defines a simple
[provider](https://docs.pact.io/getting_started/terminology#service-provider)
which will be tested with Pact in the [provider
test][examples.tests.test_01_provider_flask]. As Pact is a consumer-driven
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
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from flask import Flask, Response, abort, jsonify, request

logger = logging.getLogger(__name__)
app = Flask(__name__)


@dataclass()
class User:
    """User data class."""

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

    def dict(self) -> dict[str, Any]:
        """
        Return the user's data as a dict.
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


"""
As this is a simple example, we'll use a simple dict to represent a database.
This would be replaced with a real database in a real application.

When testing the provider in a real application, the calls to the database would
be mocked out to avoid the need for a real database. An example of this can be
found in the [test suite][examples.tests.test_01_provider_flask].
"""
FAKE_DB: dict[int, User] = {}


@app.route("/users/<int:uid>")
def get_user_by_id(uid: int) -> Response | tuple[Response, int]:
    """
    Fetch a user by their ID.

    Args:
        uid: The ID of the user to fetch

    Returns:
        The user data if found, HTTP 404 if not
    """
    user = FAKE_DB.get(uid)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    return jsonify(user.dict())


@app.route("/users/", methods=["POST"])
def create_user() -> Response:
    if request.json is None:
        abort(400, description="Invalid JSON data")

    user: dict[str, Any] = request.json
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
    return jsonify(FAKE_DB[uid].dict())


@app.route("/users/<int:uid>", methods=["DELETE"])
def delete_user(uid: int) -> tuple[str | Response, int]:
    if uid not in FAKE_DB:
        return jsonify({"detail": "User not found"}), 404
    del FAKE_DB[uid]
    return "", 204
