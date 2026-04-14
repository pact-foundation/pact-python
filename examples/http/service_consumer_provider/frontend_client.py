"""
HTTP client representing `frontend-web` calling `user-service`.

This module is intentionally free of any Pact dependency; it is production code.
The Pact dependency only appears in
[`test_consumer_frontend`][examples.http.service_consumer_provider.test_consumer_frontend],
which exercises this client against a Pact mock server to define the contract
between `frontend-web` (consumer) and
[`user_service`][examples.http.service_consumer_provider.user_service]
(provider).

Notice that the
[`Account`][examples.http.service_consumer_provider.frontend_client.Account]
dataclass only captures the fields `frontend-web` cares about (`id`, `username`,
`status`). This is a deliberate illustration of how consumer-driven contracts
differ from testing an OpenAPI specification: the contract describes what *this
consumer* uses, not everything the provider exposes.
"""

from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass
class Account:
    """
    Minimal account model as seen by `frontend-web`.

    This class intentionally reflects only the fields the frontend consumer
    needs. It may differ from the internal representation in
    [`user_service`][examples.http.service_consumer_provider.user_service],
    which stores additional state. This asymmetry is expected and is a key
    feature of consumer-driven contract testing.
    """

    id: int
    username: str
    status: str


class FrontendClient:
    """
    HTTP client used by `frontend-web` to call `user-service`.

    This client is the consumer under test in
    [`test_consumer_frontend`][examples.http.service_consumer_provider.test_consumer_frontend].
    Keeping it free of Pact dependencies means it can be used as-is in
    production while the tests handle all contract verification.
    """

    def __init__(self, base_url: str) -> None:
        """
        Initialise the frontend client.

        Args:
            base_url:
                Base URL of `user-service`, e.g. `http://user-service`. Trailing
                slashes are stripped automatically.
        """
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()

    def create_account(self, username: str, password: str) -> Account:
        """
        Create an account through `user-service`.

        Sends a `POST /accounts` request and deserialises the response into an
        [`Account`][examples.http.service_consumer_provider.frontend_client.Account].
        Only the `id`, `username`, and `status` fields are read from the
        response, and any additional fields returned by the provider are
        ignored.

        Args:
            username:
                Desired username for the new account.

            password:
                Password forwarded to `user-service`, which validates it against
                `auth-service` before creating the account.

        Returns:
            Account data returned by `user-service`.

        Raises:
            requests.HTTPError:
                If `user-service` responds with a non-2xx status (e.g., `401`
                when credentials are rejected).
        """
        response = self._session.post(
            f"{self._base_url}/accounts",
            json={"username": username, "password": password},
        )
        response.raise_for_status()
        body = response.json()
        return Account(id=body["id"], username=body["username"], status=body["status"])
