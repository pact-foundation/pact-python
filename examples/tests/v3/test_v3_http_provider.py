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
"""

from __future__ import annotations

import time
from multiprocessing import Process
from typing import Callable, Dict, Union
from unittest.mock import MagicMock

import uvicorn
from yarl import URL

from examples.src.fastapi import app
from pact.v3 import Verifier

PROVIDER_URL = URL("http://localhost:8000")

ProviderStateResult = Union[MagicMock, str]


@app.post("/_pact/callback", response_model=None)
async def mock_pact_provider_states(
    action: str,
    state: str,
) -> Dict[str, ProviderStateResult]:
    """
    Define the provider state for Pact testing.

    This endpoint is used by Pact to set up or tear down the provider's state
    before running tests.
    It achieves this by calling predefined functions that mock or verify
    the state based on the provided action and state parameters.

    Parameters:
        action (str): The action to perform, either "setup" or "teardown".
        state (str): The specific state to set up or tear down.

    The function uses two mappings:
        `setup_mapping`: Maps state names to functions that set up the provider's state
                         by mocking relevant database calls or other side effects.

        `teardown_mapping`: Maps state names to functions that verify
                            the state has been correctly set up or cleaned up.

    Based on the `action` parameter, the function calls the corresponding function
    from either `setup_mapping` or `teardown_mapping` and returns the result of that
    function as a dictionary.

    Returns:
        Dict[str, ProviderStateResult]: A dictionary containing the result of the
                                       operation, with the result converted to a string.
    """
    setup_mapping: Dict[str, Callable[[], MagicMock]] = {
        "user doesn't exists": mock_user_doesnt_exist,
        "user exists": mock_user_exists,
    }

    teardown_mapping: Dict[str, Callable[[], str]] = {
        "user doesn't exists": verify_user_doesnt_exist_mock,
        "user exists": verify_user_exists_mock,
    }

    if action == "setup":
        result: ProviderStateResult = setup_mapping[state]()
    elif action == "teardown":
        result = teardown_mapping[state]()
    return {"result": str(result)}


def run_server() -> None:
    """
    Run the FastAPI server.

    This function is required to run the FastAPI server in a separate process. A
    lambda cannot be used as the target of a `multiprocessing.Process` as it
    cannot be pickled.
    """
    host = PROVIDER_URL.host if PROVIDER_URL.host else "localhost"
    port = PROVIDER_URL.port if PROVIDER_URL.port else 8000
    uvicorn.run(app, host=host, port=port)


def test_provider() -> None:
    """
    Test the provider to ensure compliance.
    """
    proc = Process(target=run_server, daemon=True)
    proc.start()
    time.sleep(2)
    verifier = Verifier().set_info("v3_http_provider", url=PROVIDER_URL)
    verifier.add_source("examples/pacts")
    verifier.set_state(
        PROVIDER_URL / "_pact" / "callback",
        teardown=True,
    )
    verifier.verify()

    proc.terminate()


def mock_user_doesnt_exist() -> MagicMock:
    """
    Mock the database for the user doesn't exist state.
    """
    import examples.src.fastapi

    mock_db = MagicMock()
    mock_db.get.return_value = None
    examples.src.fastapi.FAKE_DB = mock_db
    return mock_db


def mock_user_exists() -> MagicMock:
    """
    Mock the database for the user exists state.
    """
    import examples.src.fastapi

    mock_db = MagicMock()
    mock_db.get.return_value = {
        "id": 123,
        "name": "Verna Hampton",
        "created_on": "2024-08-29T04:53:07.337793+00:00",
        "ip_address": "10.1.2.3",
        "hobbies": ["hiking", "swimming"],
        "admin": False,
    }
    examples.src.fastapi.FAKE_DB = mock_db
    return mock_db


def verify_user_doesnt_exist_mock() -> str:
    """
    Verify the mock calls for the 'user doesn't exist' state.

    This function checks that the mock for `FAKE_DB.get` was called,
    verifies that it returned `None`,
    and ensures that it was called with an integer argument.
    It then resets the mock for future tests.

    Returns:
        str: A message indicating that the 'user doesn't exist' mock has been verified.
    """
    import examples.src.fastapi

    examples.src.fastapi.FAKE_DB.get.assert_called()

    assert (
        examples.src.fastapi.FAKE_DB.get.return_value is None
    ), "Expected get() to return None"

    args, _ = examples.src.fastapi.FAKE_DB.get.call_args
    assert isinstance(
        args[0], int
    ), f"Expected get() to be called with an integer, but got {type(args[0])}"

    examples.src.fastapi.FAKE_DB.reset_mock()

    return "Verified user doesn't exist mock"


def verify_user_exists_mock() -> str:
    """
    Verify the mock calls for the 'user exists' state.

    This function checks that the mock for `FAKE_DB.get` was called,
    verifies that it returned the expected user data,
    and ensures that it was called with the integer argument `1`.
    It then resets the mock for future tests.

    Returns:
        str: A message indicating that the 'user exists' mock has been verified.
    """
    import examples.src.fastapi

    examples.src.fastapi.FAKE_DB.get.assert_called()

    expected_return = {
        "id": 123,
        "name": "Verna Hampton",
        "created_on": "2024-08-29T04:53:07.337793+00:00",
        "ip_address": "10.1.2.3",
        "hobbies": ["hiking", "swimming"],
        "admin": False,
    }

    assert (
        examples.src.fastapi.FAKE_DB.get.return_value == expected_return
    ), "Unexpected return value from get()"

    args, _ = examples.src.fastapi.FAKE_DB.get.call_args
    assert isinstance(
        args[0], int
    ), f"Expected get() to be called with an integer, but got {type(args[0])}"
    assert args[0] == 123, f"Expected get(123), but got get({args[0]})"

    examples.src.fastapi.FAKE_DB.reset_mock()

    return "Verified user exists mock"
