"""
Consumer test of example message handler  using the v3 API.

This test will create a pact between the message handler
and the message provider.
"""

from __future__ import annotations

import json
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
from pact.v3.pact import Pact

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
    will be called with one or two arguments - the value of `with_body` and
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
            .with_body(msg) \
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
def handler() -> Handler:
    """
    Fixture for the Handler.

    This fixture mocks the filesystem calls in the handler, so that we can
    verify that the handler is calling the filesystem correctly.
    """
    handler = Handler()
    handler.fs = MagicMock()
    handler.fs.write.return_value = None
    handler.fs.read.return_value = "Hello world!"
    return handler


@pytest.fixture()
def verifier(
    handler: Handler,
) -> Generator[Callable[[str | bytes | None, Dict[str, Any]], None], Any, None]:
    """
    Verifier function for the Pact.

    This function is passed to the `verify` method of the Pact object. It is
    responsible for taking in the messages (along with the context/metadata)
    and ensuring that the consumer is able to process the message correctly.

    In our case, we deserialize the message and pass it to the (pre-mocked)
    handler for processing. We then verify that the underlying filesystem
    calls were made as expected.
    """
    assert isinstance(handler.fs, MagicMock), "Handler filesystem not mocked"

    def _verifier(msg: str | bytes | None, context: Dict[str, Any]) -> None:
        assert msg is not None, "Message is None"
        data = json.loads(msg)
        log.info(
            "Processing message: ",
            extra={"input": msg, "processed_message": data, "context": context},
        )
        handler.process(data)

    yield _verifier

    assert handler.fs.mock_calls, "Handler did not call the filesystem"


def test_async_message_handler_write(
    pact: Pact,
    handler: Handler,
    verifier: Callable[[str | bytes | None, Dict[str, Any]], None],
) -> None:
    """
    Create a pact between the message handler and the message provider.
    """
    assert isinstance(handler.fs, MagicMock), "Handler filesystem not mocked"

    (
        pact.upon_receiving("a write request", "Async")
        .given("a request to write test.txt")
        .with_body(
            json.dumps({
                "action": "WRITE",
                "path": "my_file.txt",
                "contents": "Hello, world!",
            })
        )
    )
    pact.verify(verifier, "Async")

    handler.fs.write.assert_called_once_with("my_file.txt", "Hello, world!")


def test_async_message_handler_read(
    pact: Pact,
    handler: Handler,
    verifier: Callable[[str | bytes | None, Dict[str, Any]], None],
) -> None:
    """
    Create a pact between the message handler and the message provider.
    """
    assert isinstance(handler.fs, MagicMock), "Handler filesystem not mocked"

    (
        pact.upon_receiving("a read request", "Async")
        .given("a request to read test.txt")
        .with_body(
            json.dumps({
                "action": "READ",
                "path": "my_file.txt",
                "contents": "Hello, world!",
            })
        )
    )
    pact.verify(verifier, "Async")

    handler.fs.read.assert_called_once_with("my_file.txt")
