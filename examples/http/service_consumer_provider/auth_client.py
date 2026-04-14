"""
HTTP client used by `user-service` to call `auth-service`.

This module is intentionally free of any Pact dependency, it is production code.
The Pact dependency only appears in
[`test_consumer_auth`][examples.http.service_consumer_provider.test_consumer_auth],
which exercises this client against a Pact mock server to define the contract
between [`user_service`][examples.http.service_consumer_provider.user_service]
(consumer) and `auth-service` (provider).

This also demonstrates the consumer-driven philosophy: the client only requests
and parses the fields it actually needs (`valid`), even though `auth-service`
may return additional information in its response.
"""

from __future__ import annotations

import requests


class AuthClient:
    """
    HTTP client for credential validation against `auth-service`.

    This client is used by
    [`user_service`][examples.http.service_consumer_provider.user_service] to
    verify user credentials before creating accounts. It satisfies the
    [`CredentialsVerifier`][examples.http.service_consumer_provider.user_service.CredentialsVerifier]
    protocol and is the real implementation that would run in production.

    The matching Pact consumer tests live in
    [`test_consumer_auth`][examples.http.service_consumer_provider.test_consumer_auth].
    """

    def __init__(self, base_url: str) -> None:
        """
        Initialise the auth client.

        Args:
            base_url:
                Base URL of `auth-service`, e.g. `http://auth-service`. Trailing
                slashes are stripped automatically.
        """
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()

    def validate_credentials(self, username: str, password: str) -> bool:
        """
        Validate credentials against `auth-service`.

        Sends a `POST /auth/validate` request with the supplied credentials and
        returns whether `auth-service` considers them valid. This is the only
        field the client reads from the response: an example of how
        consumer-driven contracts focus on what the consumer *actually uses*.

        Args:
            username:
                Username to validate.

            password:
                Password to validate.

        Returns:
            `True` when credentials are valid; otherwise `False`.

        Raises:
            requests.HTTPError:
                If `auth-service` responds with a non-2xx status.
        """
        response = self._session.post(
            f"{self._base_url}/auth/validate",
            json={"username": username, "password": password},
        )
        response.raise_for_status()
        body = response.json()
        return bool(body.get("valid", False))
