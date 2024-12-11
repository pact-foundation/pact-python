"""
Producer test of example message.

This test will read a pact between the message handler and the message provider
and then validate the pact against the provider.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from examples.src.message_producer import FileSystemMessageProducer
from pact.v3 import Verifier
from pact.v3.types import Message

PACT_DIR = (Path(__file__).parent.parent.parent / "pacts").resolve()

RESPONSES: dict[str, dict[str, str]] = {
    "a request to write test.txt": {
        "function_name": "send_write_event",
    },
    "a request to read test.txt": {
        "function_name": "send_read_event",
    },
}


def message_producer(message: str, metadata: dict[str, Any] | None) -> Message:  # noqa: ARG001
    """
    Function to produce a message for the provider.

    This specific implementation is rather simple as it returns static content.
    In fact, a straight mapping of the message names to the expected responses
    could be given to the message handler directly. However, this function is
    provided to demonstrate the capability of the message handler to be very
    generic.

    Args:
        message:
            The message name.

        metadata:
            Any metadata associated with the message which can be used to
            determine the response.
    """
    producer = FileSystemMessageProducer()
    producer.queue = MagicMock()

    return Message(
        contents=json.dumps(RESPONSES[message]).encode("utf-8"),
        content_type="application/json",
        metadata=None,
    )


def test_producer() -> None:
    """
    Test the message producer.
    """
    verifier = Verifier("provider").message_handler(message_producer)
    verifier.verify()
