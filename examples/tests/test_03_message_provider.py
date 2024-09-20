"""
Test Message Pact provider.

Pact was originally designed for HTTP interactions involving a request and a
response. Message Pact is an addition to Pact that allows for testing of
non-HTTP interactions, such as message queues. This example demonstrates how to
use Message Pact to test whether a consumer can handle the messages it. Due to
the large number of possible transports, Message Pact does not provide a mock
provider and the tests only verifies the messages.

A note on terminology, the _consumer_ for Message Pact is the system that
receives the message, and the _provider_ is the system that sends the message.
Pact is still consumer-driven, and the consumer defines the expected messages it
will receive from the provider. When the provider is being verified, Pact
ensures that the provider sends the expected messages.

The below example verifies that the provider sends the expected messages. The
consumer need not send back a message, and any sideffects of the message must
be verified on the consumer side.

A good resource for understanding the message pact testing can be found [in the
Pact
documentation](https://docs.pact.io/getting_started/how_pact_works#non-http-testing-message-pact).
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
        provider.verify_with_broker(
            broker_url=str(broker),
            # Despite the auth being set in the broker URL, we still need to pass
            # the username and password to the verify_with_broker method.
            broker_username=broker.user,
            broker_password=broker.password,
            publish_version="0.0.0",
            publish_verification_results=True,
        )
