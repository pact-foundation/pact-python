"""
Consumer test of example message handler  using the v3 API.

This test will create a pact between the message handler
and the message provider.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
)
from unittest.mock import MagicMock

import pytest
from examples.src.message import Handler

from pact.v3.pact import MessagePact as Pact

if TYPE_CHECKING:
    from collections.abc import Callable


log = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def pact() -> Generator[Pact, None, None]:
    """
    Set up Message Pact Consumer.

    This fixtures sets up the Message Pact consumer and the pact it has with a
    provider. The consumer defines the expected messages it will receive from
    the provider, and the Python test suite verifies that the correct actions
    are taken.

    The verify method takes a function as an argument. This function
    will be called with one or two arguments - the value of `with_content` and
    the contents of `with_metadata` if provided.

    If the function under test does not take those parameters, you can create
    a wrapper function to convert the pact parameters into the values
    expected by your function.


    For each interaction, the consumer defines the following:

    ```python
    (
        pact = Pact("consumer name", "provider name")
        processed_messages: list[MessagePact.MessagePactResult] = pact \
            .with_specification("V3")
            .upon_receiving("a request", "Async") \
            .given("a request to write test.txt") \
            .with_content(msg) \
            .with_metadata({"Content-Type": "application/json"})
            .verify(pact_handler)
    )

    ```
    """
    pact_dir = Path(Path(__file__).parent.parent / "pacts")
    pact = Pact("v3_message_consumer", "v3_message_provider")
    log.info("Creating Message Pact with V3 specification")
    yield pact.with_specification("V3")
    pact.write_file(pact_dir, overwrite=True)


@pytest.fixture()
def handler() -> tuple[Handler, Callable[[Dict[str, Any], Dict[str, Any]], str | None]]:
    handler = Handler()
    handler.fs = MagicMock()

    # need a function to accept the params
    # the pact will send in during verify
    # and call the actual function under test
    def pact_handler(msg: Dict[str, Any], context: Dict[str, Any]) -> str | None:
        log.info(
            "Processing message: ",
            extra={"processed_message": msg, "context": context},
        )
        return handler.process(msg)

    log.info("Handler created")
    return handler, pact_handler


def test_async_message_handler_write(
    pact: Pact,
    handler: tuple[
        Handler,
        Callable[
            [Dict[str, Any], Dict[str, Any]],
            str | None,
        ],
    ],
) -> None:
    """
    Create a pact between the message handler and the message provider.
    """
    actual_handler, pact_handler = handler
    actual_handler.fs.write.return_value = None
    async_message = {
        "action": "WRITE",
        "path": "my_file.txt",
        "contents": "Hello, world!",
    }
    processed_message = (
        pact.upon_receiving("a write request", "Async")
        .given("a request to write test.txt")
        .with_content(async_message)
        .verify(pact_handler)
    )
    actual_handler.fs.write.assert_called_once_with(  # type: ignore[attr-defined]
        async_message["path"],
        async_message["contents"],
    )
    assert processed_message is not None
    assert processed_message.response is None


def test_async_message_handler_read(
    pact: Pact,
    handler: tuple[
        Handler,
        Callable[
            [Dict[str, Any], Dict[str, Any]],
            str | None,
        ],
    ],
) -> None:
    """
    Create a pact between the message handler and the message provider.
    """
    actual_handler, pact_handler = handler
    async_message = {
        "action": "READ",
        "path": "my_file.txt",
        "contents": "Hello, world!",
    }
    actual_handler.fs.read.return_value = async_message["contents"]
    processed_message = (
        pact.upon_receiving("a read request", "Async")
        .given("a request to read test.txt")
        .with_content(async_message)
        .verify(pact_handler)
    )
    actual_handler.fs.read.assert_called_once_with(  # type: ignore[attr-defined]
        "my_file.txt",
    )
    assert processed_message is not None
    assert processed_message.response == async_message["contents"]
