"""
Test the FastAPI provider with Pact.

This module demonstrates how to write a provider test using Pact Python's
upcoming version 3. Pact, being a consumer-driven testing tool, requires that
the provider respond to the requests defined by the consumer. The consumer
defines the expected interactions with the provider, and the provider is
expected to respond with the expected responses.

This module tests the FastAPI provider defined in `src/fastapi.py` against the
mock consumer. The mock consumer is set up by Pact and will replay the requests
defined by the consumers. Pact will then validate that the provider responds
with the expected responses.

The provider will be expected to be in a given state in order to respond to
certain requests. For example, when fetching a user's information, the provider
will need to have a user with the given ID in the database. In order to avoid
side effects, the provider's database calls are mocked out using functionalities
from `unittest.mock`.

Note that Pact requires that the provider be running on an accessible URL. This
means that FastAPI's [`TestClient`][fastapi.testclient.TestClient] cannot be used
to test the provider. Instead, the provider is run in a separate thread using
Python's [`Thread`][threading.Thread] class.
"""

from __future__ import annotations

import contextlib
import time
from datetime import datetime, timezone
from threading import Thread
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest
import uvicorn
from yarl import URL

from examples.src.fastapi import User
from pact.v3 import Verifier

if TYPE_CHECKING:
    from collections.abc import Generator

PROVIDER_URL = URL("http://localhost:8000")


class Server(uvicorn.Server):
    """
    Custom server class to run the FastAPI server in a separate thread.

    Thanks to [this StackOverflow
    answer](https://stackoverflow.com/a/64521239/1573761) for this solution.
    """

    def install_signal_handlers(self) -> None:
        """
        Prevent the server from installing signal handlers.

        This is required to run the FastAPI server in a separate process. The
        default behaviour of `uvicorn.Server` is to install signal handlers which
        would interfere with the signal handlers of the main process.
        """

    @contextlib.contextmanager
    def run_in_thread(self) -> Generator[str, None, None]:
        """
        Run the FastAPI server in a separate thread.

        This method runs the FastAPI server in a separate thread and yields the
        URL of the server. The server is started in a separate thread to allow the
        tests to run in the main thread.
        """
        thread = Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(0.01)
            yield f"http://{self.config.host}:{self.config.port}"
        finally:
            self.should_exit = True
            thread.join()


@pytest.fixture(scope="session")
def server() -> Generator[str, None, None]:
    server = Server(uvicorn.Config("examples.src.fastapi:app", host="localhost"))
    with server.run_in_thread() as url:
        yield url


def test_provider(server: str) -> None:
    """
    Test the FastAPI provider with Pact.

    This function performs all of the provider testing. It runs as follows:

    1.  The FastAPI server is started in a separate process. A small wait time
        is added to allow the server to start up before the tests begin.
    2.  The Verifier is created and configured.

        1.  The `set_info` method tells Pact the names of provider to be tested.
            Pact will automatically discover all the consumers that have
            contracts with this provider.

            The `url` parameter is used to specify the base URL of the provider
            against which the tests will be run.
        2.  The `add_source` method adds the directory where the pact files are
            stored. In a more typical setup, this would in fact be a Pact Broker
            URL.
        3.  The `set_state` method defines the endpoint on the provider that
            will be called to set the provider into the correct state before the
            tests begin. At present, this is the only way to set the provider
            into the correct state; however, future version of Pact Python
            intend to provide a more Pythonic way to do this.

    3.  The `verify` method is called to run the tests. This will run all the
        tests defined in the pact files and verify that the provider responds
        correctly to each request. More specifically, for each interaction, it
        will perform the following steps:

        1.  The provider state(s) are by sending a POST request to the
            provider's `_pact/callback` endpoint.
        2.  Pact impersonates the consumer by sending a request to the provider.
        3.  The provider handles the request and sends a response back to Pact.
        4.  Pact validates the response against the expected response defined in
            the pact file.
        5.  If `teardown` is set to `True` for `set_state`, Pact will send a
            `teardown` action to the provider to reset the provider state(s).

    Pact will output the results of the tests to the console and verify that the
    provider is compliant with the contract. If the provider is not compliant,
    the tests will fail and the output will show which interactions failed and
    why.
    """
    verifier = (
        Verifier("v3_http_provider")
        .add_transport(url=server)
        .add_source("examples/pacts/v3_http_consumer-v3_http_provider.json")
        .state_handler(provider_state_handler, teardown=True)
    )
    verifier.verify()


def provider_state_handler(
    state: str,
    action: str,
    _parameters: dict[str, Any] | None,
) -> None:
    """
    Handler for the provider state callback.

    For Pact to be able to correctly test compliance with the contract, the
    internal state of the provider needs to be set up correctly. For example, if
    the consumer expects a user to exist in the database, the provider needs to
    have a user with the given ID in the database.

    Naïvely, this can be achieved by setting up the database with the correct
    data for the test, but this can be slow and error-prone, and requires
    standing up additional infrastructure. The alternative showcased here is to
    mock the relevant calls to the database so as to avoid any side effects. The
    `unittest.mock` library is used to achieve this as part of the `setup`
    action.

    The added benefit of using this approach is that the mock can subsequently
    be inspected to ensure that the correct calls were made to the database. For
    example, asserting that the correct user ID was retrieved from the database.
    These checks are performed as part of the `teardown` action. This action can
    also be used to reset the mock, or in the case were a real database is used,
    to clean up any side effects.

    Args:
        action:
            One of `setup` or `teardown`. Determines whether the provider state
            should be set up or torn down.

        state:
            The name of the state to set up or tear down.

    Returns:
        A dictionary containing the result of the action.
    """
    if action == "setup":
        {
            "user doesn't exists": mock_user_doesnt_exist,
            "user exists": mock_user_exists,
            "the specified user doesn't exist": mock_post_request_to_create_user,
            "user is present in DB": mock_delete_request_to_delete_user,
        }[state]()

    if action == "teardown":
        {
            "user doesn't exists": verify_user_doesnt_exist_mock,
            "user exists": verify_user_exists_mock,
            "the specified user doesn't exist": verify_mock_post_request_to_create_user,
            "user is present in DB": verify_mock_delete_request_to_delete_user,
        }[state]()


def mock_user_doesnt_exist() -> None:
    """
    Mock the database for the user doesn't exist state.
    """
    import examples.src.fastapi

    mock_db = MagicMock()
    mock_db.get.return_value = None
    examples.src.fastapi.FAKE_DB = mock_db


def mock_user_exists() -> None:
    """
    Mock the database for the user exists state.

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

    mock_db = MagicMock()
    mock_db.get.return_value = User(
        id=123,
        name="Verna Hampton",
        email="verna@example.com",
        created_on=datetime.now(tz=timezone.utc),
        ip_address="10.1.2.3",
        hobbies=["hiking", "swimming"],
        admin=False,
    )
    examples.src.fastapi.FAKE_DB = mock_db


def mock_post_request_to_create_user() -> None:
    """
    Mock the database for the post request to create a user.

    While the `FAKE_DB` is a dictionary in this example, one should imagine that
    this is a real database. In this instance, we are replacing the calls to the
    database with a local dictionary to avoid side effects; thereby eliminating
    the need to stand up a real database for the tests.

    The added benefit of using this approach is that the mock can subsequently
    be inspected to ensure that the correct calls were made to the database. For
    example, asserting that the correct user ID was retrieved from the database.
    These checks are performed as part of the `teardown` action. This action can
    also be used to reset the mock, or in the case were a real database is used,
    to clean up any side effects.
    """
    import examples.src.fastapi

    local_db: dict[int, User] = {}

    def local_setitem(key: int, value: User) -> None:
        local_db[key] = value

    def local_getitem(key: int) -> User:
        return local_db[key]

    mock_db = MagicMock()
    mock_db.__len__.return_value = 124
    mock_db.__setitem__.side_effect = local_setitem
    mock_db.__getitem__.side_effect = local_getitem
    examples.src.fastapi.FAKE_DB = mock_db


def mock_delete_request_to_delete_user() -> None:
    """
    Mock the database for the delete request to delete a user.

    As with the `mock_post_request_to_create_user` function, we are using a
    local dictionary to avoid side effects. This function replaces the calls to
    the database with a local dictionary to avoid side effects.
    """
    import examples.src.fastapi

    local_db = {
        123: User(
            id=123,
            name="Verna Hampton",
            email="verna@example.com",
            created_on=datetime.now(tz=timezone.utc),
            ip_address="10.1.2.3",
            hobbies=["hiking", "swimming"],
            admin=False,
        ),
        124: User(
            id=124,
            name="Jane Doe",
            email="jane@example.com",
            created_on=datetime.now(tz=timezone.utc),
            ip_address="10.1.2.5",
            hobbies=["running", "dancing"],
            admin=False,
        ),
    }

    def local_delitem(key: int) -> None:
        del local_db[key]

    def local_contains(key: int) -> bool:
        return key in local_db

    mock_db = MagicMock()
    mock_db.__delitem__.side_effect = local_delitem
    mock_db.__contains__.side_effect = local_contains
    examples.src.fastapi.FAKE_DB = mock_db


def verify_user_doesnt_exist_mock() -> None:
    """
    Verify the mock calls for the 'user doesn't exist' state.

    This function checks that the mock for `FAKE_DB.get` was called, verifies
    that it returned `None`, and ensures that it was called with an integer
    argument. It then resets the mock for future tests.
    """
    import examples.src.fastapi

    if TYPE_CHECKING:
        # During setup, the `FAKE_DB` is replaced with a MagicMock object.
        # We need to inform the type checker that this has happened.
        examples.src.fastapi.FAKE_DB = MagicMock()

    assert len(examples.src.fastapi.FAKE_DB.mock_calls) == 1

    examples.src.fastapi.FAKE_DB.get.assert_called_once()
    args, kwargs = examples.src.fastapi.FAKE_DB.get.call_args
    assert len(args) == 1
    assert isinstance(args[0], int)
    assert kwargs == {}

    examples.src.fastapi.FAKE_DB.reset_mock()


def verify_user_exists_mock() -> None:
    """
    Verify the mock calls for the 'user exists' state.

    This function checks that the mock for `FAKE_DB.get` was called, verifies
    that it returned the expected user data, and ensures that it was called with
    the integer argument `1`. It then resets the mock for future tests.
    """
    import examples.src.fastapi

    if TYPE_CHECKING:
        examples.src.fastapi.FAKE_DB = MagicMock()

    assert len(examples.src.fastapi.FAKE_DB.mock_calls) == 1

    examples.src.fastapi.FAKE_DB.get.assert_called_once()
    args, kwargs = examples.src.fastapi.FAKE_DB.get.call_args
    assert len(args) == 1
    assert isinstance(args[0], int)
    assert kwargs == {}

    examples.src.fastapi.FAKE_DB.reset_mock()


def verify_mock_post_request_to_create_user() -> None:
    import examples.src.fastapi

    if TYPE_CHECKING:
        examples.src.fastapi.FAKE_DB = MagicMock()

    assert len(examples.src.fastapi.FAKE_DB.mock_calls) == 3

    examples.src.fastapi.FAKE_DB.__getitem__.assert_called_once()
    args, kwargs = examples.src.fastapi.FAKE_DB.__getitem__.call_args
    assert len(args) == 1
    assert isinstance(args[0], int)
    assert kwargs == {}

    examples.src.fastapi.FAKE_DB.__len__.assert_called_once()
    args, kwargs = examples.src.fastapi.FAKE_DB.__len__.call_args
    assert len(args) == 0
    assert kwargs == {}

    examples.src.fastapi.FAKE_DB.reset_mock()


def verify_mock_delete_request_to_delete_user() -> None:
    import examples.src.fastapi

    if TYPE_CHECKING:
        examples.src.fastapi.FAKE_DB = MagicMock()

    assert len(examples.src.fastapi.FAKE_DB.mock_calls) == 2

    examples.src.fastapi.FAKE_DB.__delitem__.assert_called_once()
    args, kwargs = examples.src.fastapi.FAKE_DB.__delitem__.call_args
    assert len(args) == 1
    assert isinstance(args[0], int)
    assert kwargs == {}

    examples.src.fastapi.FAKE_DB.__contains__.assert_called_once()
    args, kwargs = examples.src.fastapi.FAKE_DB.__contains__.call_args
    assert len(args) == 1
    assert isinstance(args[0], int)
    assert kwargs == {}
