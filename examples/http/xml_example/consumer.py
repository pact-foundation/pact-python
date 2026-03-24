"""
Requests XML consumer example.

This module defines a simple
[consumer](https://docs.pact.io/getting_started/terminology#service-consumer)
using the synchronous [`requests`][requests] library which will be tested with
Pact in the [consumer test][examples.http.xml_example.test_consumer]. As Pact
is a consumer-driven framework, the consumer defines the interactions which the
provider must then satisfy.

The consumer sends requests expecting XML responses and parses them using the
standard library [`xml.etree.ElementTree`][xml.etree.ElementTree] module.

This also showcases how Pact tests differ from merely testing adherence to an
OpenAPI specification. The Pact tests are more concerned with the practical use
of the API, rather than the formally defined specification. So you will see
below that the `User` class includes only the fields this consumer actually
needs, `id` and `name`, even though the provider could return additional fields
in its XML payload.

Note that the code in this module is agnostic of Pact (i.e., this would be your
production code). The `pact-python` dependency only appears in the tests. This
is because the consumer is not concerned with Pact, only the tests are.
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

    This class is intentionally minimal, including only the fields the consumer
    actually uses. It may differ from the [provider's user
    model][examples.http.xml_example.provider.User], which could expose
    additional fields. This demonstrates the consumer-driven nature of contract
    testing: the consumer defines what it needs, not what the provider exposes.
    """

    id: int
    name: str

    def __post_init__(self) -> None:
        """
        Validate the user data after initialisation.

        Raises:
            ValueError: If the name is empty or the ID is not a positive integer.
        """
        if not self.name:
            msg = "User must have a name"
            raise ValueError(msg)
        if self.id <= 0:
            msg = "User ID must be a positive integer"
            raise ValueError(msg)


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
        # S314: xml.etree.ElementTree is safe here because the XML comes from
        # a trusted provider over a controlled HTTP connection, not from
        # arbitrary user input.
        root = ET.fromstring(response.text)  # noqa: S314
        id_text = root.findtext("id")
        name_text = root.findtext("name")
        if id_text is None or name_text is None:
            msg = "Provider response missing required XML element 'id' or 'name'"
            raise ValueError(msg)
        return User(
            id=int(id_text),
            name=name_text,
        )
