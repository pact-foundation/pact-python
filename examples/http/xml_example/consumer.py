"""
Requests XML consumer example.

This module defines a simple
[consumer](https://docs.pact.io/getting_started/terminology#service-consumer)
using the synchronous [`requests`][requests] library which will be tested with
Pact in the [consumer test][examples.http.xml_example.test_consumer].

The consumer sends requests expecting XML responses and parses them using the
standard library [`xml.etree.ElementTree`][xml.etree.ElementTree] module.

Note that the code in this module is agnostic of Pact (i.e., this would be your
production code). The `pact-python` dependency only appears in the tests.
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

logger = logging.getLogger(__name__)


@dataclass()
class User:
    """
    Represents a user as seen by the consumer.
    """

    id: int
    name: str


class UserClient:
    """
    HTTP client for interacting with a user provider service via XML.
    """

    def __init__(self, hostname: str) -> None:
        """
        Initialise the user client.

        Args:
            hostname:
                The base URL of the provider (must include scheme, e.g.,
                `http://`).

        Raises:
            ValueError:
                If the hostname does not start with 'http://' or `https://`.
        """
        if not hostname.startswith(("http://", "https://")):
            msg = "Invalid base URI"
            raise ValueError(msg)
        self._hostname = hostname
        self._session = requests.Session()

    def __enter__(self) -> Self:
        """
        Begin the context for the client.
        """
        self._session.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit the context for the client.
        """
        self._session.__exit__(exc_type, exc_val, exc_tb)

    def get_user(self, user_id: int) -> User:
        """
        Fetch a user by ID from the provider, expecting an XML response.

        Args:
            user_id:
                The ID of the user to fetch.

        Returns:
            A `User` instance parsed from the XML response.

        Raises:
            requests.HTTPError:
                If the server returns a non-2xx response.
        """
        logger.debug("Fetching user %s", user_id)
        response = self._session.get(
            f"{self._hostname}/users/{user_id}",
            headers={"Accept": "application/xml"},
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)  # noqa: S314
        return User(
            id=int(root.findtext("id")),
            name=root.findtext("name"),
        )
