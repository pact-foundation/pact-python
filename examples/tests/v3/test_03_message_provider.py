"""
Producer test of example message.

This test will read a pact between the message handler and the message provider
and then validate the pact against the provider.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from examples.src.message_producer import FileSystemMessageProducer
from examples.tests.v3.provider_server import start_provider
from pact.v3 import Verifier

PACT_DIR = (Path(__file__).parent.parent.parent / "pacts").resolve()

responses: dict[str, dict[str, str]] = {
    "a request to write test.txt": {
        "function_name": "send_write_event",
    },
    "a request to read test.txt": {
        "function_name": "send_read_event",
    },
}

CURRENT_STATE: str | None = None


def message_producer_function() -> tuple[str, str]:
    producer = FileSystemMessageProducer()
    producer.queue = MagicMock()

    assert CURRENT_STATE is not None, "State is not set"
    function_name = responses.get(CURRENT_STATE, {}).get("function_name")
    assert function_name is not None, "Function name could not be found"
    producer_function = getattr(producer, function_name)

    if producer_function.__name__ == "send_write_event":
        producer_function("provider_file_name.txt", "Hello, world!")
    elif producer_function.__name__ == "send_read_event":
        producer_function("provider_file_name.txt")

    return producer.queue.send.call_args[0][0], "application/json"


def state_provider_function(state_name: str) -> None:
    global CURRENT_STATE  # noqa: PLW0603
    CURRENT_STATE = state_name


def test_producer() -> None:
    """
    Test the message producer.
    """
    with start_provider(
        handler_module=__name__,
        handler_function="message_producer_function",
        state_provider_module=__name__,
        state_provider_function="state_provider_function",
    ) as provider_url:
        verifier = (
            Verifier("provider")
            .add_transport(url=f"{provider_url}/produce_message")
            .set_state(
                provider_url / "set_provider_state",
                teardown=True,
            )
            .filter_consumers("v3_message_consumer")
            .add_source(PACT_DIR / "v3_message_consumer-v3_message_provider.json")
        )
        verifier.verify()
