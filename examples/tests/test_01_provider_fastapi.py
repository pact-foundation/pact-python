"""
Test the FastAPI provider with Pact.

This module tests the FastAPI provider defined in `src/fastapi.py` against the
mock consumer. The mock consumer is set up by Pact and will replay the requests
defined by the consumers. Pact will then validate that the provider responds
with the expected responses.

The provider will be expected to be in a given state in order to respond to
certain requests. For example, when fetching a user's information, the provider
will need to have a user with the given ID in the database. In order to avoid
side effects, the provider's database calls are mocked out using functionalities
from `unittest.mock`.

In order to set the provider into the correct state, this test module defines an
additional endpoint on the provider, in this case `/_pact/provider_states`.
Calls to this endpoint mock the relevant database calls to set the provider into
the correct state.

A good resource for understanding the provider tests is the [Pact Provider
Test](https://docs.pact.io/5-minute-getting-started-guide#scope-of-a-provider-pact-test)
section of the Pact documentation.
"""

from __future__ import annotations

import time
from multiprocessing import Process
from typing import Any, Dict, Generator, Union
from unittest.mock import MagicMock

import pytest
import uvicorn
from pydantic import BaseModel
from yarl import URL

from examples.src.fastapi import app
from pact import Verifier

PROVIDER_URL = URL("http://localhost:8080")


class ProviderState(BaseModel):
    """Define the provider state."""

    consumer: str
    state: str


@app.post("/_pact/provider_states")
async def mock_pact_provider_states(
    state: ProviderState,
) -> Dict[str, Union[str, None]]:
    """
    Define the provider state.

    For Pact to be able to correctly tests compliance with the contract, the
    internal state of the provider needs to be set up correctly. Naively, this
    would be achieved by setting up the database with the correct data for the
    test, but this can be slow and error-prone. Instead this is best achieved by
    mocking the relevant calls to the database so as to avoid any side effects.

    For Pact to be able to correctly get the provider into the correct state,
    this function is used to define an additional endpoint on the provider. This
    endpoint is called by Pact before each test to ensure that the provider is
    in the correct state.
    """
    mapping = {
        "user 123 doesn't exist": mock_user_123_doesnt_exist,
        "user 123 exists": mock_user_123_exists,
    }
    return {"result": mapping[state.state]()}


def run_server() -> None:
    """
    Run the FastAPI server.

    This function is required to run the FastAPI server in a separate process. A
    lambda cannot be used as the target of a `multiprocessing.Process` as it
    cannot be pickled.
    """
    host = PROVIDER_URL.host if PROVIDER_URL.host else "localhost"
    port = PROVIDER_URL.port if PROVIDER_URL.port else 8080
    uvicorn.run(app, host=host, port=port)


@pytest.fixture(scope="module")
def verifier() -> Generator[Verifier, Any, None]:
    """Set up the Pact verifier."""
    proc = Process(target=run_server, daemon=True)
    verifier = Verifier(
        provider="UserProvider",
        provider_base_url=str(PROVIDER_URL),
    )
    proc.start()
    time.sleep(2)
    yield verifier
    proc.kill()


def mock_user_123_doesnt_exist() -> None:
    """Mock the database for the user 123 doesn't exist state."""
    import examples.src.fastapi

    examples.src.fastapi.FAKE_DB = MagicMock()
    examples.src.fastapi.FAKE_DB.get.return_value = None


def mock_user_123_exists() -> None:
    """
    Mock the database for the user 123 exists state.

    You may notice that the return value here differs from the consumer's
    expected response. This is because the consumer's expected response is
    guided by what the consumer uses.

    By using consumer-driven contracts and testing the provider against the
    consumer's contract, we can ensure that the provider is what the consumer
    needs. This allows the provider to safely evolve their API (by both adding
    and removing fields) without fear of breaking the interactions with the
    consumers.
    """
    import examples.src.fastapi

    examples.src.fastapi.FAKE_DB = MagicMock()
    examples.src.fastapi.FAKE_DB.get.return_value = {
        "id": 123,
        "name": "Verna Hampton",
        "created_on": "2016-12-15T20:16:01",
        "ip_address": "10.1.2.3",
        "hobbies": ["hiking", "swimming"],
        "admin": False,
    }


def test_against_broker(broker: URL, verifier: Verifier) -> None:
    """
    Test the provider against the broker.

    The broker will be used to retrieve the contract, and the provider will be
    tested against the contract.

    As Pact is a consumer-driven, the provider is tested against the contract
    defined by the consumer. The consumer defines the expected request to and
    response from the provider.

    For an example of the consumer's contract, see the consumer's tests.
    """
    code, _ = verifier.verify_with_broker(
        broker_url=str(broker),
        # Despite the auth being set in the broker URL, we still need to pass
        # the username and password to the verify_with_broker method.
        broker_username=broker.user,
        broker_password=broker.password,
        publish_version="0.0.0",
        publish_verification_results=True,
        provider_states_setup_url=str(PROVIDER_URL / "_pact" / "provider_states"),
    )

    assert code == 0
