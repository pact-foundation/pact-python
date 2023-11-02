"""
Utility functions to help with testing.
"""

from __future__ import annotations

import contextlib
import hashlib
import logging
import typing
from pathlib import Path
from xml.etree import ElementTree

from multidict import MultiDict

logger = logging.getLogger(__name__)
SUITE_ROOT = Path(__file__).parent / "definition"
FIXTURES_ROOT = SUITE_ROOT / "fixtures"


def string_to_int(word: str) -> int:
    """
    Convert a word to an integer.

    The word can be a number, or a word representing a number.

    Args:
        word: The word to convert.

    Returns:
        The integer value of the word.

    Raises:
        ValueError: If the word cannot be converted to an integer.
    """
    try:
        return int(word)
    except ValueError:
        pass

    try:
        return {
            "first": 1,
            "second": 2,
            "third": 3,
            "fourth": 4,
            "fifth": 5,
            "sixth": 6,
            "seventh": 7,
            "eighth": 8,
            "ninth": 9,
            "1st": 1,
            "2nd": 2,
            "3rd": 3,
            "4th": 4,
            "5th": 5,
            "6th": 6,
            "7th": 7,
            "8th": 8,
            "9th": 9,
        }[word]
    except KeyError:
        pass

    msg = f"Unable to convert {word!r} to an integer"
    raise ValueError(msg)


def truncate(data: str | bytes) -> str:
    """
    Truncate a large string or bytes object.

    This is useful for printing large strings or bytes objects in tests.
    """
    if len(data) <= 32:
        if isinstance(data, str):
            return f"{data!r}"
        return data.decode("utf-8", "backslashreplace")

    length = len(data)
    if isinstance(data, str):
        checksum = hashlib.sha256(data.encode()).hexdigest()
        return (
            '"'
            + data[:6]
            + "⋯"
            + data[-6:]
            + '"'
            + f" ({length} bytes, sha256={checksum[:7]})"
        )

    checksum = hashlib.sha256(data).hexdigest()
    return (
        'b"'
        + data[:8].decode("utf-8", "backslashreplace")
        + "⋯"
        + data[-8:].decode("utf-8", "backslashreplace")
        + '"'
        + f" ({length} bytes, sha256={checksum[:7]})"
    )


class InteractionDefinition:
    """
    Interaction definition.

    This is a dictionary that represents a single interaction. It is used to
    parse the HTTP interactions table into a more useful format.
    """

    class Body:
        """
        Interaction body.

        The interaction body can be one of:

        - A file
        - An arbitrary string
        - A JSON document
        - An XML document
        """

        def __init__(self, data: str) -> None:
            """
            Instantiate the interaction body.
            """
            self.string: str | None = None
            self.bytes: bytes | None = None
            self.mime_type: str | None = None

            if data.startswith("file: ") and data.endswith("-body.xml"):
                self.parse_fixture(FIXTURES_ROOT / data[6:])
                return

            if data.startswith("file: "):
                self.parse_file(FIXTURES_ROOT / data[6:])
                return

            if data.startswith("JSON: "):
                self.string = data[6:]
                self.bytes = self.string.encode("utf-8")
                self.mime_type = "application/json"
                return

            if data.startswith("XML: "):
                self.string = data[5:]
                self.bytes = self.string.encode("utf-8")
                self.mime_type = "application/xml"
                return

            self.bytes = data.encode("utf-8")
            self.string = data
            self.mime_type = "text/plain"

        def __repr__(self) -> str:
            """
            Debugging representation.
            """
            return "<Body: {}>".format(
                ", ".join(truncate(f"{k}={v!r}") for k, v in vars(self).items()),
            )

        def parse_fixture(self, fixture: Path) -> None:
            """
            Parse a fixture file.

            This is used to parse the fixture files that contain additional
            metadata about the body (such as the content type).
            """
            etree = ElementTree.parse(fixture)  # noqa: S314
            root = etree.getroot()
            if not root or root.tag != "body":
                msg = "Invalid XML fixture document"
                raise ValueError(msg)

            contents = root.find("contents")
            content_type = root.find("contentType")
            if contents is None:
                msg = "Invalid XML fixture document: no contents"
                raise ValueError(msg)
            if content_type is None:
                msg = "Invalid XML fixture document: no contentType"
                raise ValueError(msg)
            self.string = typing.cast(str, contents.text)

            if eol := contents.attrib.get("eol", None):
                if eol == "CRLF":
                    self.string = self.string.replace("\r\n", "\n")
                    self.string = self.string.replace("\n", "\r\n")
                elif eol == "LF":
                    self.string = self.string.replace("\r\n", "\n")

            self.bytes = self.string.encode("utf-8")
            self.mime_type = content_type.text

        def parse_file(self, file: Path) -> None:
            """
            Load the contents of a file.

            The mime type is inferred from the file extension, and the contents
            are loaded as a byte array, and optionally as a string.
            """
            self.bytes = file.read_bytes()
            with contextlib.suppress(UnicodeDecodeError):
                self.string = file.read_text()

            if file.suffix == ".xml":
                self.mime_type = "application/xml"
            elif file.suffix == ".json":
                self.mime_type = "application/json"
            elif file.suffix == ".jpg":
                self.mime_type = "image/jpeg"
            elif file.suffix == ".pdf":
                self.mime_type = "application/pdf"
            else:
                msg = "Unknown file type"
                raise ValueError(msg)

    def __init__(self, **kwargs: str) -> None:
        """Initialise the interaction definition."""
        self.id: int | None = None
        self.method: str = kwargs.pop("method")
        self.path: str = kwargs.pop("path")
        self.response: int = int(kwargs.pop("response"))
        self.query: str | None = None
        self.headers: MultiDict[str] = MultiDict()
        self.body: InteractionDefinition.Body | None = None
        self.response_content: str | None = None
        self.response_body: InteractionDefinition.Body | None = None
        self.update(**kwargs)

    def update(self, **kwargs: str) -> None:  # noqa: C901
        """
        Update the interaction definition.

        This is a convenience method that allows the interaction definition to
        be updated with new values.
        """
        if interaction_id := kwargs.pop("No", None):
            self.id = int(interaction_id)
        if method := kwargs.pop("method", None):
            self.method = method
        if path := kwargs.pop("path", None):
            self.path = path
        if query := kwargs.pop("query", None):
            self.query = query
        if headers := kwargs.pop("headers", None):
            self.headers = InteractionDefinition.parse_headers(headers)
        if body := kwargs.pop("body", None):
            # When updating the body, we _only_ update the body content, not
            # the content type.
            orig_content_type = self.body.mime_type if self.body else None
            self.body = InteractionDefinition.Body(body)
            self.body.mime_type = orig_content_type or self.body.mime_type
        if content_type := (
            kwargs.pop("content_type", None) or kwargs.pop("content type", None)
        ):
            if self.body is None:
                self.body = InteractionDefinition.Body("")
            self.body.mime_type = content_type
        if response := kwargs.pop("response", None):
            self.response = int(response)
        if response_content := (
            kwargs.pop("response_content", None) or kwargs.pop("response content", None)
        ):
            self.response_content = response_content
        if response_body := (
            kwargs.pop("response_body", None) or kwargs.pop("response body", None)
        ):
            self.response_body = InteractionDefinition.Body(response_body)

        if len(kwargs) > 0:
            msg = f"Unexpected arguments: {kwargs.keys()}"
            raise TypeError(msg)

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return "<Body: {}>".format(
            ", ".join(f"{k}={v!r}" for k, v in vars(self).items()),
        )

    @staticmethod
    def parse_headers(headers: str) -> MultiDict[str]:
        """
        Parse the headers.

        The headers are in the format:

        ```text
        'X-A: 1', 'X-B: 2', 'X-A: 3'
        ```

        As headers can be repeated, the result is a MultiDict.
        """
        kvs: list[tuple[str, str]] = []
        for header in headers.split(", "):
            k, v = header.strip("'").split(": ")
            kvs.append((k, v))
        return MultiDict(kvs)
