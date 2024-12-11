"""
Simple Consumer Implementation.

This modules defines a simple
[consumer](https://docs.pact.io/getting_started/terminology#service-consumer)
which will be tested with Pact in the [consumer
test][examples.tests.test_00_consumer]. As Pact is a consumer-driven framework,
the consumer defines the interactions which the provider must then satisfy.

The consumer is the application which makes requests to another service (the
provider) and receives a response to process. In this example, we have a simple
[`User`][examples.src.consumer.User] class and the consumer fetches a user's
information from a HTTP endpoint.

This also showcases how Pact tests differ from merely testing adherence to an
OpenAPI specification. The Pact tests are more concerned with the practical use
of the API, rather than the formally defined specification. So you will see
below that as far as this consumer is concerned, the only information needed
from the provider is the user's ID, name, and creation date. This is despite the
provider having additional fields in the response.

Note that the code in this module is agnostic of Pact (i.e., this would be your
production code). The `pact-python` dependency only appears in the tests. This
is because the consumer is not concerned with Pact, only the tests are.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests


@dataclass()
class User:
    """User data class."""

    id: int
    name: str
    created_on: datetime

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


class UserConsumer:
    """
    Example consumer.

    This class defines a simple consumer which will interact with a provider
    over HTTP to fetch a user's information, and then return an instance of the
    `User` class.
    """

    def __init__(self, base_uri: str) -> None:
        """
        Initialise the consumer.

        Args:
            base_uri: The uri of the provider
        """
        self.base_uri = base_uri

    def get_user(self, user_id: int) -> User:
        """
        Fetch a user by ID from the server.

        Args:
            user_id: The ID of the user to fetch.

        Returns:
            The user if found.

            In all other cases, an error dictionary is returned with the key
            `error` and the value as the error message.

        Raises:
            requests.HTTPError: If the server returns a non-200 response.
        """
        uri = f"{self.base_uri}/users/{user_id}"
        response = requests.get(uri, timeout=5)
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        # Python < 3.11 don't support ISO 8601 offsets without a colon
        if sys.version_info < (3, 11) and data["created_on"][-4:].isdigit():
            data["created_on"] = data["created_on"][:-2] + ":" + data["created_on"][-2:]
        return User(
            id=data["id"],
            name=data["name"],
            created_on=datetime.fromisoformat(data["created_on"]),
        )

    def create_user(
        self,
        *,
        name: str,
    ) -> User:
        """
        Create a new user on the server.

        Args:
            name: The name of the user to create.

        Returns:
            The user, if successfully created.

        Raises:
            requests.HTTPError: If the server returns a non-200 response.
        """
        uri = f"{self.base_uri}/users/"
        response = requests.post(uri, json={"name": name}, timeout=5)
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        # Python < 3.11 don't support ISO 8601 offsets without a colon
        if sys.version_info < (3, 11) and data["created_on"][-4:].isdigit():
            data["created_on"] = data["created_on"][:-2] + ":" + data["created_on"][-2:]
        return User(
            id=data["id"],
            name=data["name"],
            created_on=datetime.fromisoformat(data["created_on"]),
        )

    def delete_user(self, uid: int | User) -> None:
        """
        Delete a user by ID from the server.

        Args:
            uid: The user ID or user object to delete.

        Raises:
            requests.HTTPError: If the server returns a non-200 response.
        """
        if isinstance(uid, User):
            uid = uid.id

        uri = f"{self.base_uri}/users/{uid}"
        response = requests.delete(uri, timeout=5)
        response.raise_for_status()
