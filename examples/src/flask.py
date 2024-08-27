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

Note that the code in this module is agnostic of Pact. The `pact-python`
dependency only appears in the tests. This is because the consumer is not
concerned with Pact, only the tests are.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Tuple, Union

from flask import Flask, Response, abort, jsonify, request

logger = logging.getLogger(__name__)

app = Flask(__name__)
"""
As this is a simple example, we'll use a simple dict to represent a database.
This would be replaced with a real database in a real application.

When testing the provider in a real application, the calls to the database would
be mocked out to avoid the need for a real database. An example of this can be
found in the [test suite][examples.tests.test_01_provider_flask].
"""
FAKE_DB: Dict[int, Dict[str, Any]] = {}


@app.route("/users/<uid>")
def get_user_by_id(uid: int) -> Union[Dict[str, Any], tuple[Dict[str, Any], int]]:
    """
    Fetch a user by their ID.

    Args:
        uid: The ID of the user to fetch

    Returns:
        The user data if found, HTTP 404 if not
    """
    user = FAKE_DB.get(int(uid))
    if not user:
        return {"error": "User not found"}, 404
    return user


@app.route("/users/", methods=["POST"])
def create_user() -> Tuple[Response, int]:
    if request.json is None:
        abort(400, description="Invalid JSON data")

    data: Dict[str, Any] = request.json
    new_uid: int = len(FAKE_DB)
    if new_uid in FAKE_DB:
        abort(400, description="User already exists")

    FAKE_DB[new_uid] = {"id": new_uid, "name": data["name"], "email": data["email"]}
    return jsonify(FAKE_DB[new_uid]), 200


@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id: int) -> Tuple[str, int]:
    if user_id not in FAKE_DB:
        abort(404, description="User not found")
    del FAKE_DB[user_id]
    return "", 204  # No Content status code
