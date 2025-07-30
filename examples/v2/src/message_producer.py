"""
Message producer for non-HTTP interactions.

This modules implements a very basic message producer which could
send to an eventing system, such as Kafka, or a message queue.

Note that the code in this module is agnostic of Pact (i.e., this would be your
production code). The `pact-python` dependency only appears in the tests. This
is because the consumer is not concerned with Pact, only the tests are.
"""

from __future__ import annotations

import enum
import json
from typing import Literal, NamedTuple


class FileSystemAction(enum.Enum):
    """
    Represents a file system action.
    """

    READ = "READ"
    WRITE = "WRITE"


class FileSystemEvent(NamedTuple):
    """
    Represents a file system event.
    """

    action: Literal[FileSystemAction.READ, FileSystemAction.WRITE]
    path: str
    contents: str | None


class MockMessageQueue:
    """
    A mock message queue.
    """

    def __init__(self) -> None:
        """
        Initialize the message queue.
        """
        self.messages: list[str] = []

    def send(self, message: str) -> None:
        """
        Send a message to the queue.

        Args:
            message: The message to send.
        """
        self.messages.append(message)


class FileSystemMessageProducer:
    """
    A message producer for file system events.
    """

    def __init__(self) -> None:
        """
        Initialize the message producer.
        """
        self.queue = MockMessageQueue()

    def send_to_queue(self, message: FileSystemEvent) -> None:
        """
        Send a message to a message queue.

        :param message: The message to send.
        """
        self.queue.send(
            json.dumps({
                "action": message.action.value,
                "path": message.path,
                "contents": message.contents,
            })
        )

    def send_write_event(self, filename: str, contents: str) -> None:
        """
        Send a write event to a message queue.

        Args:
            filename: The name of the file.
            contents: The contents of the file.
        """
        message = FileSystemEvent(
            action=FileSystemAction.WRITE,
            path=filename,
            contents=contents,
        )
        self.send_to_queue(message)

    def send_read_event(self, filename: str) -> None:
        """
        Send a read event to a message queue.

        :param filename: The name of the file.
        """
        message = FileSystemEvent(
            action=FileSystemAction.READ,
            path=filename,
            contents=None,
        )
        self.send_to_queue(message)
