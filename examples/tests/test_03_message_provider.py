"""
Test Message Pact provider.

Unlike the standard Pact, which is designed for HTTP interactions, the Message
Pact is designed for non-HTTP interactions. This example demonstrates how to use
the Message Pact to test whether a provider generates the correct messages.

In such examples, Pact simply checks the kind of messages produced. The consumer
need not send back a message, and any sideffects of the message must be verified
separately.

The below example verifies that the consumer makes the correct filesystem calls
when it receives a message to read or write a file. The calls themselves are
mocked out so as to avoid actually writing to the filesystem.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from flask import Flask
from pact import MessageProvider

if TYPE_CHECKING:
    from yarl import URL

app = Flask(__name__)
PACT_DIR = (Path(__file__).parent / "pacts").resolve()


def generate_write_message() -> dict[str, str]:
    return {
        "action": "WRITE",
        "path": "test.txt",
        "contents": "Hello world!",
    }


def generate_read_message() -> dict[str, str]:
    return {
        "action": "READ",
        "path": "test.txt",
    }


def test_verify(broker: URL) -> None:
    provider = MessageProvider(
        provider="MessageProvider",
        consumer="MessageConsumer",
        pact_dir=str(PACT_DIR),
        message_providers={
            "a request to write test.txt": generate_write_message,
            "a request to read test.txt": generate_read_message,
        },
    )

    with provider:
        provider.verify_with_broker(broker_url=str(broker))
