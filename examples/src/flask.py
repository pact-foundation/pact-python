"""
Flask provider example.

This modules defines a simple
[provider](https://docs.pact.io/getting_started/terminology#service-provider)
with Pact. As Pact is a consumer-driven framework, the consumer defines the
contract which the provider must then satisfy.

The provider is the application which receives requests from another service
(the consumer) and returns a response. In this example, we have a simple
endpoint which returns a user's information from a (fake) database.

Note that the code in this module is agnostic of Pact. The `pact-python`
dependency only appears in the tests. This is because the consumer is not
concerned with Pact, only the tests are.
"""

from __future__ import annotations

from typing import Any

from flask import Flask

app = Flask(__name__)

"""
As this is a simple example, we'll use a simple dict to represent a database.
This would be replaced with a real database in a real application.

When testing the provider in a real application, the calls to the database
would be mocked out to avoid the need for a real database. An example of this
can be found in the test suite.
"""
FAKE_DB: dict[int, dict[str, Any]] = {}


@app.route("/users/<uid>")
def get_user_by_id(uid: int) -> dict[str, Any] | tuple[dict[str, Any], int]:
    """
    Fetch a user by their ID.

    Args:
        uid: The ID of the user to fetch

    Returns:
        The user data if found, HTTP 404 if not
    """
    user = FAKE_DB.get(uid)
    if not user:
        return {"error": "User not found"}, 404
    return user
