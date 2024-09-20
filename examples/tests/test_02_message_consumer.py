"""
Test Message Pact consumer.

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

In this example, Pact simply ensures that the consumer is capable of processing
the message. The consumer need not send back a message, and any sideffects of
the message must be verified separately (such as through `assert` statements or
as part of the usual unit testing suite).

> :warning: There is currently a bug whereby the `given` and
`expects_to_receive` have swapped meanings compared to the reference
implementation. This will be addressed in a future release.

A good resource for understanding the message pact testing can be found [in the
Pact
documentation](https://docs.pact.io/getting_started/how_pact_works#non-http-testing-message-pact).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from examples.src.message import Handler
from pact import MessageConsumer, MessagePact, Provider

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from yarl import URL

log = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def pact(broker: URL, pact_dir: Path) -> Generator[MessagePact, Any, None]:
    """
    Set up Message Pact Consumer.

    This fixtures sets up the Message Pact consumer and the pact it has with a
    provider. The consumer defines the expected messages it will receive from
    the provider, and the Python test suite verifies that the correct actions
    are taken.

    For each interaction, the consumer defines the following:

    ```python
    (
        pact.given("a request to write test.txt")
        .expects_to_receive("empty filesystem")
        .with_content(msg)
        .with_metadata({"Content-Type": "application/json"})
    )

    NOTE: There is currently a bug whereby the `given` and `expects_to_receive`
    have swapped meanings. This will be addressed in a future release.
    ```
    """
    consumer = MessageConsumer("MessageConsumer")
    pact = consumer.has_pact_with(
        Provider("MessageProvider"),
        pact_dir=pact_dir,
        publish_to_broker=True,
        # Broker configuration
        broker_base_url=str(broker),
        broker_username=broker.user,
        broker_password=broker.password,
    )
    with pact:
        yield pact


@pytest.fixture
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


def test_write_file(pact: MessagePact, handler: Handler) -> None:
    """
    Test write file.

    This test will be run against the mock provider. The mock provider will
    expect to receive a request to write a file, and will respond with a 200
    status code.
    """
    msg = {"action": "WRITE", "path": "test.txt", "contents": "Hello world!"}
    (
        pact.given("a request to write test.txt")
        .expects_to_receive("empty filesystem")
        .with_content(msg)
        .with_metadata({"Content-Type": "application/json"})
    )

    result = handler.process(msg)
    handler.fs.write.assert_called_once_with(  # type: ignore[attr-defined]
        "test.txt",
        "Hello world!",
    )
    assert result is None


def test_read_file(pact: MessagePact, handler: Handler) -> None:
    msg = {"action": "READ", "path": "test.txt"}
    (
        pact.given("a request to read test.txt")
        .expects_to_receive("test.txt exists")
        .with_content(msg)
        .with_metadata({"Content-Type": "application/json"})
    )

    result = handler.process(msg)
    handler.fs.read.assert_called_once_with("test.txt")  # type: ignore[attr-defined]
    assert result == "Hello world!"
