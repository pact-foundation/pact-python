"""
Handler for non-HTTP interactions.

This module implements a very basic handler to handle JSON payloads which might
be sent from Kafka, or some queueing system. Unlike a HTTP interaction, the
handler is solely responsible for processing the message, and does not
necessarily need to send a response.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Union


class Filesystem:
    """
    Filesystem interface.

    In practice, the handler would process messages and perform some actions on
    other systems, whether that be a database, a filesystem, or some other
    service. This capability would typically be offered by some library;
    however, when running tests, we typically wish to avoid actually interacting
    with this external service.

    In order to avoid side effects while testing, the test setup should mock out
    the calls to the external service.

    This class provides a simple dummy filesystem interface (which evidently
    would fail if actually used), and serves to demonstrate how to mock out
    external services when testing.
    """

    def __init__(self) -> None:
        """Initialize the filesystem connection."""

    def write(self, _file: str, _contents: str) -> None:
        """Write contents to a file."""
        raise NotImplementedError

    def read(self, file: str) -> str:
        """Read contents from a file."""
        raise NotImplementedError


class Handler:
    """
    Message queue handler.

    This class is responsible for handling messages from the queue.
    """

    def __init__(self) -> None:
        """
        Initialize the handler.

        This ensures the underlying filesystem is ready to be used.
        """
        self.fs = Filesystem()

    def process(self, event: Dict[str, Any]) -> Union[str, None]:
        """
        Process an event from the queue.

        The event is expected to be a dictionary with the following mandatory
        keys:

        - `action`: The action to be performed, either `READ` or `WRITE`.
        - `path`: The path to the file to be read or written.

        The event may also contain an optional `contents` key, which is the
        contents to be written to the file. If the `contents` key is not
        present, an empty file will be written.
        """
        self.validate_event(event)

        if event["action"] == "WRITE":
            self.fs.write(event["path"], event.get("contents", ""))
            return None
        if event["action"] == "READ":
            return self.fs.read(event["path"])

        msg = f"Invalid action: {event['action']!r}"
        raise ValueError(msg)

    @staticmethod
    def validate_event(event: Union[Dict[str, Any], Any]) -> None:  # noqa: ANN401
        """
        Validates the event received from the queue.

        The event is expected to be a dictionary with the following mandatory
        keys:

        - `action`: The action to be performed, either `READ` or `WRITe`.
        - `path`: The path to the file to be read or written.
        """
        if not isinstance(event, dict):
            msg = "Event must be a dictionary."
            raise TypeError(msg)
        if "action" not in event:
            msg = "Event must contain an 'action' key."
            raise ValueError(msg)
        if "path" not in event:
            msg = "Event must contain a 'path' key."
            raise ValueError(msg)
        if event["action"] not in ["READ", "WRITE"]:
            msg = "Event must contain a valid 'action' key."
            raise ValueError(msg)
        try:
            Path(event["path"])
        except TypeError as err:
            msg = "Event must contain a valid 'path' key."
            raise ValueError(msg) from err
