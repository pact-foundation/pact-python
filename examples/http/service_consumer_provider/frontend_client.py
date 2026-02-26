"""
HTTP client representing a frontend calling user-service.
"""

from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass
class Account:
    """
    Minimal account model used by the frontend.
    """

    id: int
    username: str
    status: str


class FrontendClient:
    """
    HTTP client used by frontend-web to call user-service.
    """

    def __init__(self, base_url: str) -> None:
        """
        Initialise the frontend client.

        Args:
            base_url:
                Base URL of user-service.
        """
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()

    def create_account(self, username: str, password: str) -> Account:
        """
        Create an account through user-service.

        Args:
            username:
                Desired username.

            password:
                Password used during credential validation.

        Returns:
            Account data returned by user-service.

        Raises:
            requests.HTTPError:
                If user-service responds with a non-2xx status.
        """
        response = self._session.post(
            f"{self._base_url}/accounts",
            json={"username": username, "password": password},
        )
        response.raise_for_status()
        body = response.json()
        return Account(id=body["id"], username=body["username"], status=body["status"])
