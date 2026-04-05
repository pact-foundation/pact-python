"""
FastAPI service that acts as both a consumer and a provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from examples.http.service_consumer_provider.auth_client import AuthClient


class CredentialsVerifier(Protocol):
    """
    Behaviour required for credential verification.
    """

    def validate_credentials(self, username: str, password: str) -> bool:
        """
        Validate credentials.
        """


@dataclass
class UserAccount:
    """
    Stored account record.
    """

    id: int
    username: str


class InMemoryAccountStore:
    """
    Small in-memory store for example purposes.
    """

    def __init__(self) -> None:
        """
        Initialise the in-memory store.
        """
        self._next_id = 1
        self._accounts: dict[int, UserAccount] = {}

    def create(self, username: str) -> UserAccount:
        """
        Create and store a new account.

        Args:
            username:
                Username for the new account.

        Returns:
            The created account.
        """
        account = UserAccount(id=self._next_id, username=username)
        self._accounts[account.id] = account
        self._next_id += 1
        return account

    def reset(self) -> None:
        """
        Reset all stored accounts.
        """
        self._next_id = 1
        self._accounts.clear()


class CreateAccountRequest(BaseModel):
    """
    Request payload used by frontend-web.
    """

    username: str
    password: str


class CreateAccountResponse(BaseModel):
    """
    Response payload returned to frontend-web.
    """

    id: int
    username: str
    status: str = "created"


ACCOUNT_STORE = InMemoryAccountStore()


class _ServiceState:
    """
    Mutable state used by provider-state handlers in tests.
    """

    def __init__(self) -> None:
        """
        Initialise default collaborators.
        """
        self.auth_verifier: CredentialsVerifier = AuthClient("http://auth-service")


SERVICE_STATE = _ServiceState()

app = FastAPI()


def set_auth_verifier(verifier: CredentialsVerifier) -> None:
    """
    Replace the auth verifier implementation.

    Args:
        verifier:
            New verifier implementation.
    """
    SERVICE_STATE.auth_verifier = verifier


def reset_state() -> None:
    """
    Reset internal provider state.
    """
    ACCOUNT_STORE.reset()


@app.post("/accounts", status_code=status.HTTP_201_CREATED)
async def create_account(payload: CreateAccountRequest) -> CreateAccountResponse:
    """
    Create an account after validating credentials with auth-service.

    Args:
        payload:
            Account request payload.

    Returns:
        Created account response.

    Raises:
        HTTPException:
            If credentials are invalid.
    """
    if not SERVICE_STATE.auth_verifier.validate_credentials(
        payload.username,
        payload.password,
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    account = ACCOUNT_STORE.create(payload.username)
    return CreateAccountResponse(id=account.id, username=account.username)
