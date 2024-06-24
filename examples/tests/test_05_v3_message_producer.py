"""
Producer test of example message.

This test will read a pact between the message handler
and the message provider and then validate the pact
against the provider.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple
from unittest.mock import MagicMock

from examples.src.message_producer import FileSystemMessageProducer
from examples.tests.provider_server import start_provider_context
from pact.v3 import Verifier

PACT_DIR = (Path(__file__).parent.parent / "pacts").resolve()

responses = {
    "a request to write test.txt": {
        "function_name": "send_write_event",
    },
    "a request to read test.txt": {
        "function_name": "send_read_event",
    },
}

CURRENT_STATE = None


def message_producer_function() -> Tuple[str, str]:
    producer = FileSystemMessageProducer()
    producer.queue = MagicMock()
    function_name = responses.get(CURRENT_STATE, {}).get("function_name")
    producer_function = getattr(producer, function_name)
    if producer_function.__name__ == "send_write_event":
        producer_function("foo.txt", "Hello, world!")
    elif producer_function.__name__ == "send_read_event":
        producer_function("foo.txt")
    return producer.queue.send.call_args[0][0], "application/json"


def state_provider_function(state_name: str) -> None:
    global CURRENT_STATE  # noqa: PLW0603
    CURRENT_STATE = state_name


def test_producer() -> None:
    """
    Test the message producer.
    """
    with start_provider_context(
        handler_module=__name__,
        handler_function="message_producer_function",
        state_provider_module=__name__,
        state_provider_function="state_provider_function",
    ) as provider_url:
        verifier = (
            Verifier()
            .set_state(
                provider_url / "set_provider_state",
                teardown=True,
            )
            .set_info("provider", url=f"{provider_url}/produce_message")
            .filter_consumers("v3_message_consumer")
            .add_source(PACT_DIR / "v3_message_consumer-v3_message_provider.json")
        )
        verifier.verify()
