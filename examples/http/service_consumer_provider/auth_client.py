"""
HTTP client used by user-service to call auth-service.
"""

from __future__ import annotations

import requests


class AuthClient:
    """
    Small HTTP client for auth-service contract interactions.
    """

    def __init__(self, base_url: str) -> None:
        """
        Initialise the auth client.

        Args:
            base_url:
                Base URL of auth-service.
        """
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()

    def validate_credentials(self, username: str, password: str) -> bool:
        """
        Validate credentials against auth-service.

        Args:
            username:
                Username to validate.

            password:
                Password to validate.

        Returns:
            True when credentials are valid; otherwise False.

        Raises:
            requests.HTTPError:
                If auth-service responds with a non-2xx status.
        """
        response = self._session.post(
            f"{self._base_url}/auth/validate",
            json={"username": username, "password": password},
        )
        response.raise_for_status()
        body = response.json()
        return bool(body.get("valid", False))
