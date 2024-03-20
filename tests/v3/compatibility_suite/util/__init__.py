"""
Utility functions to help with testing.

## Sharing PyTest BDD Steps

The PyTest BDD library does some 'magic' to make the given/when/then steps
available in the test context. This is done by inspecting the stack frame of the
calling function and injecting the step definition function as a fixture.

This is a problem when sharing steps between different test suites, as the stack
frame is different. Fortunately, PyTest BDD allows us to specify the stack level
to inspect, so we can use that to our advantage with the following pattern:

```python
def some_step(stacklevel: int = 1) -> None:
    @when(..., stacklevel=stacklevel + 1)
    def _():
        # Step definition goes here
```
"""

from __future__ import annotations

import base64
import contextlib
import hashlib
import logging
import typing
from collections.abc import Collection, Mapping
from datetime import date, datetime, time
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import flask
from flask import request
from multidict import MultiDict
from yarl import URL

if typing.TYPE_CHECKING:
    from pact.v3.pact import Pact

logger = logging.getLogger(__name__)
SUITE_ROOT = Path(__file__).parent.parent / "definition"
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
            return f"{data}"
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


def parse_markdown_table(content: str) -> list[dict[str, str]]:
    """
    Parse a Markdown table into a list of dictionaries.

    The table is expected to be in the following format:

    ```markdown
    | key1 | key2 | key3 |
    | val1 | val2 | val3 |
    ```

    Note that the first row is expected to be the column headers, and the
    remaining rows are the values. There is no header/body separation.
    """
    rows = [
        list(map(str.strip, row.split("|")))[1:-1]
        for row in content.split("\n")
        if row.strip()
    ]

    if len(rows) < 2:
        msg = f"Expected at least two rows in the table, got {len(rows)}"
        raise ValueError(msg)

    return [dict(zip(rows[0], row)) for row in rows[1:]]


def serialize(obj: Any) -> Any:  # noqa: ANN401, PLR0911
    """
    Convert an object to a dictionary.

    This function converts an object to a dictionary by calling `vars` on the
    object. This is useful for classes which are not otherwise serializable
    using `json.dumps`.

    A few special cases are handled:

    -   If the object is a `datetime` object, it is converted to an ISO 8601
        string.
    -   All forms of [`Mapping`][collections.abc.Mapping] are converted to
        dictionaries.
    -   All forms of [`Collection`][collections.abc.Collection] are converted to
        lists.

    All other types are converted to strings using the `repr` function.
    """
    if isinstance(obj, datetime | date | time):
        return obj.isoformat()

    # Basic types which are already serializable
    if isinstance(obj, str | int | float | bool | type(None)):
        return obj

    # Bytes
    if isinstance(obj, bytes):
        return {
            "__class__": obj.__class__.__name__,
            "data": base64.b64encode(obj).decode("utf-8"),
        }

    # Collections
    if isinstance(obj, Mapping):
        return {k: serialize(v) for k, v in obj.items()}

    if isinstance(obj, Collection):
        return [serialize(v) for v in obj]

    # Objects
    if hasattr(obj, "__dict__"):
        return {
            "__class__": obj.__class__.__name__,
            "__module__": obj.__class__.__module__,
            **{k: serialize(v) for k, v in obj.__dict__.items()},
        }

    return repr(obj)


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
        k, _sep, v = header.strip("'").partition(": ")
        kvs.append((k, v))
    return MultiDict(kvs)


def parse_matching_rules(matching_rules: str) -> str:
    """
    Parse the matching rules.

    The matching rules are in one of two formats:

    - An explicit JSON object, prefixed by `JSON: `.
    - A fixture file which contains the matching rules.
    """
    if matching_rules.startswith("JSON: "):
        return matching_rules[6:]

    with (FIXTURES_ROOT / matching_rules).open("r") as file:
        return file.read()


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

        def __repr__(self) -> str:
            """
            Debugging representation.
            """
            return "<Body: {}>".format(
                ", ".join(
                    str(k) + "=" + truncate(repr(v)) for k, v in vars(self).items()
                ),
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
        self.state: str | None = None
        self.method: str = kwargs.pop("method")
        self.path: str = kwargs.pop("path")
        self.response: int = int(kwargs.pop("response", 200))
        self.query: str | None = None
        self.headers: MultiDict[str] = MultiDict()
        self.body: InteractionDefinition.Body | None = None
        self.response_headers: MultiDict[str] = MultiDict()
        self.response_body: InteractionDefinition.Body | None = None
        self.matching_rules: str | None = None
        self.update(**kwargs)

    def update(self, **kwargs: str) -> None:  # noqa: C901, PLR0912
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
            self.headers = parse_headers(headers)

        if headers := (
            kwargs.pop("raw headers", None) or kwargs.pop("raw_headers", None)
        ):
            self.headers = parse_headers(headers)

        if body := kwargs.pop("body", None):
            # When updating the body, we _only_ update the body content, not
            # the content type.
            orig_content_type = self.body.mime_type if self.body else None
            self.body = InteractionDefinition.Body(body)
            self.body.mime_type = self.body.mime_type or orig_content_type

        if content_type := (
            kwargs.pop("content_type", None) or kwargs.pop("content type", None)
        ):
            if self.body is None:
                self.body = InteractionDefinition.Body("")
            self.body.mime_type = content_type

        if response := kwargs.pop("response", None) or kwargs.pop("status", None):
            self.response = int(response)

        if response_headers := (
            kwargs.pop("response_headers", None) or kwargs.pop("response headers", None)
        ):
            self.response_headers = parse_headers(response_headers)

        if response_content := (
            kwargs.pop("response_content", None) or kwargs.pop("response content", None)
        ):
            if self.response_body is None:
                self.response_body = InteractionDefinition.Body("")
            self.response_body.mime_type = response_content

        if response_body := (
            kwargs.pop("response_body", None) or kwargs.pop("response body", None)
        ):
            orig_content_type = (
                self.response_body.mime_type if self.response_body else None
            )
            self.response_body = InteractionDefinition.Body(response_body)
            self.response_body.mime_type = (
                self.response_body.mime_type or orig_content_type
            )

        if matching_rules := (
            kwargs.pop("matching_rules", None) or kwargs.pop("matching rules", None)
        ):
            self.matching_rules = parse_matching_rules(matching_rules)

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

    def add_to_pact(self, pact: Pact, name: str) -> None:  # noqa: C901, PLR0912
        """
        Add the interaction to the pact.

        This is a convenience method that allows the interaction definition to
        be added to the pact, defining the "upon receiving ... with ... will
        respond with ...".

        Args:
            pact:
                The pact being defined.

            name:
                Name for this interaction. Must be unique for the pact.
        """
        interaction = pact.upon_receiving(name)
        logging.info("with_request(%s, %s)", self.method, self.path)
        interaction.with_request(self.method, self.path)

        # We distinguish between "" and None here.
        if self.state is not None:
            logging.info("given(%s)", self.state)
            interaction.given(self.state)

        if self.query:
            query = URL.build(query_string=self.query).query
            logging.info("with_query_parameters(%s)", query.items())
            interaction.with_query_parameters(query.items())

        if self.headers:
            logging.info("with_headers(%s)", self.headers.items())
            interaction.with_headers(self.headers.items())

        if self.body:
            if self.body.string:
                logging.info(
                    "with_body(%s, %s)",
                    truncate(self.body.string),
                    self.body.mime_type,
                )
                interaction.with_body(
                    self.body.string,
                    self.body.mime_type,
                )
            elif self.body.bytes:
                logging.info(
                    "with_binary_file(%s, %s)",
                    truncate(self.body.bytes),
                    self.body.mime_type,
                )
                interaction.with_binary_body(
                    self.body.bytes,
                    self.body.mime_type,
                )
            else:
                msg = "Unexpected body definition"
                raise RuntimeError(msg)

        if self.matching_rules:
            logging.info("with_matching_rules(%s)", self.matching_rules)
            interaction.with_matching_rules(self.matching_rules)

        if self.response:
            logging.info("will_respond_with(%s)", self.response)
            interaction.will_respond_with(self.response)

        if self.response_body:
            if self.response_body.string:
                logging.info(
                    "with_body(%s, %s)",
                    truncate(self.response_body.string),
                    self.response_body.mime_type,
                )
                interaction.with_body(
                    self.response_body.string,
                    self.response_body.mime_type,
                )
            elif self.response_body.bytes:
                logging.info(
                    "with_binary_file(%s, %s)",
                    truncate(self.response_body.bytes),
                    self.response_body.mime_type,
                )
                interaction.with_binary_body(
                    self.response_body.bytes,
                    self.response_body.mime_type,
                )
            else:
                msg = "Unexpected body definition"
                raise RuntimeError(msg)

    def add_to_flask(self, app: flask.Flask) -> None:
        """
        Add an interaction to a Flask app.

        Args:
            app:
                The Flask app to add the interaction to.
        """

        async def route_fn() -> flask.Response:
            logger.info("Received request: %s %s", self.method, self.path)
            if self.query:
                query = URL.build(query_string=self.query).query
                # Perform a two-way check to ensure that the query parameters
                # are present in the request, and that the request contains no
                # unexpected query parameters.
                for k, v in query.items():
                    assert request.args[k] == v
                for k, v in request.args.items():
                    assert query[k] == v

            if self.headers:
                # Perform a one-way check to ensure that the expected headers
                # are present in the request, but don't check for any unexpected
                # headers.
                for k, v in self.headers.items():
                    assert k in request.headers
                    assert request.headers[k] == v

            if self.body:
                assert request.data == self.body.bytes

            return flask.Response(
                response=self.response_body.bytes or self.response_body.string or None
                if self.response_body
                else None,
                status=self.response,
                headers=self.response_headers,
                content_type=self.response_body.mime_type
                if self.response_body
                else None,
                direct_passthrough=True,
            )

        # The route function needs to have a unique name
        clean_name = self.path.replace("/", "_").replace("__", "_")
        route_fn.__name__ = f"{self.method.lower()}_{clean_name}"

        app.add_url_rule(
            self.path,
            view_func=route_fn,
            methods=[self.method],
        )
