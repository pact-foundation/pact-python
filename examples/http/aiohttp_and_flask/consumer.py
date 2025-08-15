"""
Aiohttp consumer example.

This modules defines a simple
[consumer](https://docs.pact.io/getting_started/terminology#service-consumer)
using the asynchronous [`aiohttp`][aiohttp] library which will be tested with
Pact in the [consumer test][examples.http.aiohttp_and_flask.test_consumer]. As
Pact is a consumer-driven framework, the consumer defines the interactions which
the provider must then satisfy.

The consumer is the application which makes requests to another service (the
provider) and receives a response to process. In this example, we have a simple
`User` class and the consumer fetches a user's information from a HTTP endpoint.

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

import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

import aiohttp

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

logger = logging.getLogger(__name__)


@dataclass()
class User:
    """
    Represents a user as seen by the consumer.

    This class is intentionally minimal, including only the fields the consumer
    actually uses. It may differ from the [provider's user
    model][examples.http.aiohttp_and_flask.provider.User], which could have
    additional fields. This demonstrates the consumer-driven nature of contract
    testing: the consumer defines what it needs, not what the provider exposes.
    """

    id: int
    name: str
    created_on: datetime

    def __post_init__(self) -> None:
        """
        Validate the user data.

        Ensures that the user has a non-empty name and a positive integer ID.

        Raises:
            ValueError:
                If the name is empty or the ID is not positive.
        """
        if not self.name:
            msg = "User must have a name"
            raise ValueError(msg)

        if self.id <= 0:
            msg = "User ID must be a positive integer"
            raise ValueError(msg)

    def __repr__(self) -> str:
        """
        Return a string representation of the user.
        """
        return f"User(id={self.id!r}, name={self.name!r})"


class UserClient:
    """
    HTTP client for interacting with a user provider service.

    This class is a simple consumer that fetches user data from a provider over
    HTTP. It demonstrates how to structure consumer code for use in contract
    testing, keeping it independent of Pact or any contract testing framework.
    """

    def __init__(self, hostname: str, base_path: str | None = None) -> None:
        """
        Initialise the user client.

        Args:
            hostname:
                The base URL of the provider (must include scheme, e.g.,
                `http://`).

            base_path:
                The base path for the provider's API endpoints. Defaults to `/`.

        Raises:
            ValueError:
                If the hostname does not start with `http://` or 'https://'.
        """
        if not hostname.startswith(("http://", "https://")):
            msg = "Invalid base URI"
            raise ValueError(msg)
        self._hostname = hostname
        self._base_path = base_path or "/"
        if not self._base_path.endswith("/"):
            self._base_path += "/"

        self._session = aiohttp.ClientSession(
            base_url=self._hostname,
            timeout=aiohttp.ClientTimeout(total=5),
        )
        logger.debug(
            "Initialised UserClient with base URL: %s%s",
            self.base_url,
            self._base_path,
        )

    @property
    def hostname(self) -> str:
        """
        The hostname as a string.

        This includes the scheme.
        """
        return self._hostname

    @property
    def base_path(self) -> str:
        """
        The base path as a string.
        """
        return self._base_path

    @property
    def base_url(self) -> str:
        """
        The base URL as a string.
        """
        return f"{self._hostname}{self._base_path}"

    async def __aenter__(self) -> Self:
        """
        Begin an asynchronous context for the client.
        """
        await self._session.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit the asynchronous context for the client.

        Args:
            exc_type:
                The exception type, if any.

            exc_val:
                The exception value, if any.

            exc_tb:
                The traceback, if any.
        """
        await self._session.__aexit__(exc_type, exc_val, exc_tb)

    async def get_user(self, user_id: int) -> User:
        """
        Fetch a user by ID from the provider.

        This method demonstrates how a consumer fetches only the data it needs
        from a provider, regardless of what else the provider may return.

        Args:
            user_id:
                The ID of the user to fetch.

        Returns:
            A `User` instance representing the fetched user.

        Raises:
            aiohttp.ClientError:
                If the server returns a non-2xx response or the request fails.
        """
        logger.debug("Fetching user %s", user_id)
        async with self._session.get(f"{self.base_path}users/{user_id}") as response:
            response.raise_for_status()
            data: dict[str, Any] = await response.json()

            # Python < 3.11 don't support ISO 8601 offsets without a colon
            if sys.version_info < (3, 11) and data["created_on"][-4:].isdigit():
                data["created_on"] = (
                    data["created_on"][:-2] + ":" + data["created_on"][-2:]
                )
            return User(
                id=data["id"],
                name=data["name"],
                created_on=datetime.fromisoformat(data["created_on"]),
            )

    async def create_user(
        self,
        *,
        name: str,
    ) -> User:
        """
        Create a new user on the provider.

        Args:
            name:
                The name of the user to create.

        Returns:
            A `User` instance representing the newly created user.

        Raises:
            aiohttp.ClientError:
                If the server returns a non-2xx response or the request fails.
        """
        logger.debug("Creating user %s", name)
        async with (
            self._session.post(
                f"{self.base_path}users", json={"name": name}
            ) as response,
        ):
            response.raise_for_status()
            data = await response.json()
            # Python < 3.11 don't support ISO 8601 offsets without a colon
            if sys.version_info < (3, 11) and data["created_on"][-4:].isdigit():
                data["created_on"] = (
                    data["created_on"][:-2] + ":" + data["created_on"][-2:]
                )
            logger.debug("Created user %s", data["id"])
            return User(
                id=data["id"],
                name=data["name"],
                created_on=datetime.fromisoformat(data["created_on"]),
            )

    async def delete_user(self, uid: int | User) -> None:
        """
        Delete a user by ID from the provider.

        Args:
            uid:
                The user ID (int) or a `User` instance to delete.

        Raises:
            aiohttp.ClientError:
                If the server returns a non-2xx response or the request fails.
        """
        if isinstance(uid, User):
            uid = uid.id
        logger.debug("Deleting user %s", uid)

        async with self._session.delete(f"{self.base_path}users/{uid}") as response:
            response.raise_for_status()
