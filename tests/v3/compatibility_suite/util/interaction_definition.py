"""
Interaction definition.

This module defines the `InteractionDefinition` class, which is used to help
parse the interaction definitions from the compatibility suite, and interact
with the `Pact` and `Interaction` classes.
"""

from __future__ import annotations

import contextlib
import json
import logging
import typing
import warnings
from typing import Any, Literal
from xml.etree import ElementTree as ET

from multidict import MultiDict
from typing_extensions import Self
from yarl import URL

from pact.v3.interaction import HttpInteraction, Interaction
from tests.v3.compatibility_suite.util import (
    FIXTURES_ROOT,
    parse_headers,
    parse_matching_rules,
    truncate,
)

if typing.TYPE_CHECKING:
    from http.server import SimpleHTTPRequestHandler
    from pathlib import Path

    from pact.v3.interaction import Interaction
    from pact.v3.pact import Pact
    from pact.v3.types import Message

logger = logging.getLogger(__name__)


class InteractionBody:
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
            ", ".join(str(k) + "=" + truncate(repr(v)) for k, v in vars(self).items()),
        )

    def parse_fixture(self, fixture: Path) -> None:
        """
        Parse a fixture file.

        This is used to parse the fixture files that contain additional
        metadata about the body (such as the content type).
        """
        etree = ET.parse(fixture)  # noqa: S314
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

    def add_to_interaction(
        self,
        interaction: Interaction,
    ) -> None:
        """
        Add a body to the interaction.

        This is a helper method that adds the body to the interaction. This
        relies on Pact's intelligent understanding of whether it is dealing with
        a request or response (which is determined through the use of
        `will_respond_with`).

        Args:
            body:
                The body to add to the interaction.

            interaction:
                The interaction to add the body to.

        """
        if self.string:
            logger.info(
                "with_body(%r, %r)",
                truncate(self.string),
                self.mime_type,
            )
            interaction.with_body(
                self.string,
                self.mime_type,
            )
        elif self.bytes:
            logger.info(
                "with_binary_body(%r, %r)",
                truncate(self.bytes),
                self.mime_type,
            )
            interaction.with_binary_body(
                self.bytes,
                self.mime_type,
            )
        else:
            msg = "Unexpected body definition"
            raise RuntimeError(msg)

        if self.mime_type and isinstance(interaction, HttpInteraction):
            logger.info('set_header("Content-Type", %r)', self.mime_type)
            interaction.set_header("Content-Type", self.mime_type)


class InteractionState:
    """
    Provider state.
    """

    def __init__(
        self,
        name: str,
        parameters: str | dict[str, Any] | None = None,
    ) -> None:
        """
        Instantiate the provider state.
        """
        self.name = name
        self.parameters: dict[str, Any]
        if isinstance(parameters, str):
            self.parameters = json.loads(parameters)
        else:
            self.parameters = parameters or {}

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return "<State: {}>".format(
            ", ".join(str(k) + "=" + truncate(repr(v)) for k, v in vars(self).items()),
        )

    def as_dict(self) -> dict[str, str | dict[str, Any]]:
        """
        Convert the provider state to a dictionary.
        """
        return {"name": self.name, "parameters": self.parameters}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """
        Convert a dictionary to a provider state.
        """
        return cls(**data)


class InteractionDefinition:
    """
    Interaction definition.

    This is a dictionary that represents a single interaction. It is used to
    parse the HTTP interactions table into a more useful format.
    """

    def __init__(
        self,
        *,
        metadata: dict[str, Any] | None = None,
        **kwargs: str,
    ) -> None:
        """
        Initialise the interaction definition.

        As the interaction definitions are parsed from a Markdown table,
        values are expected to be strings and must be converted to the correct
        type.

        The _only_ exception to this is the `metadata` key, which expects
        a dictionary.
        """
        # A common pattern used in the tests is to have a table with the 'base'
        # definitions, and have tests modify these definitions as need be. As a
        # result, the `__init__` method is designed to set all the values to
        # defaults, and the `update` method is used to update the values.
        if type_ := kwargs.pop("type", "HTTP"):
            if type_ not in ("HTTP", "Sync", "Async"):
                msg = f"Invalid value for 'type': {type_}"
                raise ValueError(msg)
            self.type: Literal["HTTP", "Sync", "Async"] = type_  # type: ignore[assignment]

        # General properties shared by all interaction types
        self.id: int | None = None
        self.description: str | None = None
        self.states: list[InteractionState] = []
        self.metadata: dict[str, Any] | None = None
        self.pending: bool = False
        self.is_pending: bool = False
        self.test_name: str | None = None
        self.text_comments: list[str] = []
        self.comments: dict[str, str] = {}

        # Request properties
        self.method: str | None = None
        self.path: str | None = None
        self.response: int | None = None
        self.query: str | None = None
        self.headers: MultiDict[str] = MultiDict()
        self.body: InteractionBody | None = None
        self.matching_rules: str | None = None

        # Response properties
        self.response_headers: MultiDict[str] = MultiDict()
        self.response_body: InteractionBody | None = None
        self.response_matching_rules: str | None = None

        self.update(metadata=metadata, **kwargs)

    def update(self, *, metadata: dict[str, Any] | None = None, **kwargs: str) -> None:
        """
        Update the interaction definition.

        This is a convenience method that allows the interaction definition to
        be updated with new values.
        """
        kwargs = self._update_shared(metadata, **kwargs)
        kwargs = self._update_request(**kwargs)
        kwargs = self._update_response(**kwargs)

        if len(kwargs) > 0:
            msg = f"Unexpected arguments: {kwargs.keys()}"
            raise TypeError(msg)

    def _update_shared(
        self,
        metadata: dict[str, Any] | None = None,
        **kwargs: str,
    ) -> dict[str, str]:
        """
        Update the shared properties of the interaction.

        Note that the following properties are not supported and must be
        modified directly:

        -   `states`
        -   `text_comments`
        -   `comments`

        Args:
            metadata:
                Metadata for the interaction.

            kwargs:
                Remaining keyword arguments, which are:

                -   `No`: Interaction ID. Used purely for debugging purposes.
                -   `description`: Description of the interaction (used by
                    asynchronous messages)
                -   `pending`: Whether the interaction is pending.
                -   `test_name`: Test name for the interaction.

        Returns:
            The remaining keyword arguments.
        """
        if interaction_id := kwargs.pop("No", None):
            self.id = int(interaction_id)

        if description := kwargs.pop("description", None):
            self.description = description

        if "states" in kwargs:
            msg = "Unsupported. Modify the 'states' property directly."
            raise ValueError(msg)

        if metadata:
            self.metadata = metadata

        if "pending" in kwargs:
            self.pending = kwargs.pop("pending") == "true"

        if test_name := kwargs.pop("test_name", None):
            self.test_name = test_name

        if "text_comments" in kwargs:
            msg = "Unsupported. Modify the 'text_comments' property directly."
            raise ValueError(msg)

        if "comments" in kwargs:
            msg = "Unsupported. Modify the 'comments' property directly."
            raise ValueError(msg)

        return kwargs

    def _update_request(self, **kwargs: str) -> dict[str, str]:
        """
        Update the request properties of the interaction.

        Args:
            kwargs:
                Remaining keyword arguments, which are:

                -   `method`: Request method.
                -   `path`: Request path.
                -   `query`: Query parameters.
                -   `headers`: Request headers.
                -   `raw_headers`: Request headers.
                -   `body`: Request body.
                -   `content_type`: Request content type.
                -   `matching_rules`: Request matching rules.

        """
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
            self.body = InteractionBody(body)
            self.body.mime_type = self.body.mime_type or orig_content_type

        if content_type := (
            kwargs.pop("content_type", None) or kwargs.pop("content type", None)
        ):
            if self.body is None:
                self.body = InteractionBody("")
            self.body.mime_type = content_type

        if matching_rules := (
            kwargs.pop("matching_rules", None) or kwargs.pop("matching rules", None)
        ):
            self.matching_rules = parse_matching_rules(matching_rules)

        return kwargs

    def _update_response(self, **kwargs: str) -> dict[str, str]:
        """
        Update the response properties of the interaction.

        Args:
            kwargs:
                Remaining keyword arguments, which are:

                -  `response`: Response status code.
                -  `response_headers`: Response headers.
                -  `response_content`: Response content type.
                -  `response_body`: Response body.
                -  `response_matching_rules`: Response matching rules.

        Returns:
            The remaining keyword arguments.
        """
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
                self.response_body = InteractionBody("")
            self.response_body.mime_type = response_content

        if response_body := (
            kwargs.pop("response_body", None) or kwargs.pop("response body", None)
        ):
            orig_content_type = (
                self.response_body.mime_type if self.response_body else None
            )
            self.response_body = InteractionBody(response_body)
            self.response_body.mime_type = (
                self.response_body.mime_type or orig_content_type
            )

        if matching_rules := (
            kwargs.pop("response_matching_rules", None)
            or kwargs.pop("response matching rules", None)
        ):
            self.response_matching_rules = parse_matching_rules(matching_rules)

        return kwargs

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return "<Body: {}>".format(
            ", ".join(f"{k}={v!r}" for k, v in vars(self).items()),
        )

    def add_to_pact(  # noqa: C901, PLR0912, PLR0915
        self,
        pact: Pact,
        name: str,
    ) -> None:
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
        interaction = pact.upon_receiving(name, self.type)
        if isinstance(interaction, HttpInteraction):
            assert self.method, "Method must be defined"
            assert self.path, "Path must be defined"

            logger.info("with_request(%r, %r)", self.method, self.path)
            interaction.with_request(self.method, self.path)

        for state in self.states or []:
            if state.parameters:
                logger.info("given(%r, parameters=%r)", state.name, state.parameters)
                interaction.given(state.name, parameters=state.parameters)
            else:
                logger.info("given(%r)", state.name)
                interaction.given(state.name)

        if self.pending:
            logger.info("set_pending(True)")
            interaction.set_pending(pending=True)

        if self.text_comments:
            for comment in self.text_comments:
                logger.info("add_text_comment(%r)", comment)
                interaction.add_text_comment(comment)

        for key, value in self.comments.items():
            logger.info("set_comment(%r, %r)", key, value)
            interaction.set_comment(key, value)

        if self.test_name:
            logger.info("test_name(%r)", self.test_name)
            interaction.test_name(self.test_name)

        if self.query:
            assert isinstance(interaction, HttpInteraction), (
                "Query parameters require an HTTP interaction"
            )
            query = URL.build(query_string=self.query).query
            logger.info("with_query_parameters(%r)", query.items())
            interaction.with_query_parameters(query.items())

        if self.headers:
            assert isinstance(interaction, HttpInteraction), (
                "Headers require an HTTP interaction"
            )
            logger.info("with_headers(%r)", self.headers.items())
            interaction.with_headers(self.headers.items())

        if self.body:
            self.body.add_to_interaction(interaction)

        if self.matching_rules:
            logger.info("with_matching_rules(%r)", self.matching_rules)
            interaction.with_matching_rules(self.matching_rules)

        if self.response:
            assert isinstance(interaction, HttpInteraction), (
                "Response requires an HTTP interaction"
            )
            logger.info("will_respond_with(%r)", self.response)
            interaction.will_respond_with(self.response)

        if self.response_headers:
            assert isinstance(interaction, HttpInteraction), (
                "Response headers require an HTTP interaction"
            )
            logger.info("with_headers(%r)", self.response_headers)
            interaction.with_headers(self.response_headers.items(), "Response")

        if self.response_body:
            assert isinstance(interaction, HttpInteraction), (
                "Response body requires an HTTP interaction"
            )
            self.response_body.add_to_interaction(interaction)

        if self.response_matching_rules:
            logger.info("with_matching_rules(%r)", self.response_matching_rules)
            interaction.with_matching_rules(self.response_matching_rules)

        if self.metadata:
            for key, value in self.metadata.items():
                if isinstance(value, str):
                    interaction.with_metadata({key: value})
                else:
                    interaction.with_metadata({key: json.dumps(value)})

    def matches_request(self, request: SimpleHTTPRequestHandler) -> bool:
        """
        Check if a request matches the interaction.

        Args:
            request:
                The request to check.

        Returns:
            Whether the request matches the interaction.
        """
        if self.type == "HTTP":
            logger.debug(
                "Checking whether request '%s %s' matches '%s %s'",
                request.command,
                request.path,
                self.method,
                self.path,
            )
            return (
                request.command == self.method
                and request.path.split("?")[0] == self.path
            )
        return False

    def handle_request(self, request: SimpleHTTPRequestHandler) -> None:
        """
        Handle a HTTP request.

        Internally, we use Python's built-in [`http.server`][http.server] module
        to handle the request. For each request, Pythhon instantiates a new
        [`SimpleHTTPRequestHandler`][http.server.SimpleHTTPRequestHandler]
        object with the request details and provider the interface to respond.

        Args:
            request:
                The request to handle.
        """
        logger.debug("Handling request: %s %s", request.command, request.path)
        if self.type == "HTTP":
            self._handle_request_http(request)
        elif self.type in ("Sync", "Async"):
            msg = "Sync and Async interactions are handled by message relay."
            raise ValueError(msg)
        else:
            msg = f"Unknown interaction type: {self.type}"
            raise ValueError(msg)

    def _handle_request_http(self, request: SimpleHTTPRequestHandler) -> None:  # noqa: C901, PLR0912
        """
        Add a HTTP interaction to a Flask app.

        This function works by defining a new function to handle the request and
        produce the response. This function is then added to the Flask app as a
        route.

        Args:
            request:
                The request to handle.
        """
        assert isinstance(self.method, str), "Method must be a string"
        assert isinstance(self.path, str), "Path must be a string"

        logger.info(
            "Handling HTTP '%s %s' interaction",
            self.method,
            self.path,
        )

        # Check the request method
        if request.command != self.method:
            logger.error("Method mismatch: %s != %s", request.command, self.method)
            request.send_error(405, "Method Not Allowed")
            return

        # Check the request path
        if request.path.split("?")[0] != self.path:
            logger.error("Path mismatch: %s != %s", request.path, self.path)
            request.send_error(404, "Not Found")
            return

        # Check the query parameters
        #
        # We expect an exact match of the query parameters (unlike the headers)
        if self.query:
            logger.info("Checking request query parameters")
            expected_query = URL.build(query_string=self.query).query
            request_query = URL.build(
                query_string=request.path.split("?")[1] if "?" in request.path else ""
            ).query
            if (expected_keys := set(expected_query.keys())) != (
                request_keys := set(request_query.keys())
            ):
                logger.error(
                    "Query parameter mismatch: %s != %s",
                    request_keys,
                    expected_keys,
                )
                request.send_error(400, "Bad Request")
                return

            for k in expected_query:
                if (request_vals := request_query.getall(k)) != (
                    expected_vals := expected_query.getall(k)
                ):
                    logger.error(
                        "Query parameter mismatch: %s != %s",
                        request_vals,
                        expected_vals,
                    )
                    request.send_error(400, "Bad Request")
                    return

        # Check the headers
        #
        # We only check for the headers we expect from the interaction
        # definition. It is very likely that the request will contain additional
        # headers (e.g. `Host`, `User-Agent`, etc.) that we do not care about.
        if self.headers:
            logger.info("Checking request headers")
            for k, v in self.headers.items():
                if (rv := request.headers.get(k)) != v:
                    logger.error("Header mismatch: %s != %s", rv, v)
                    request.send_error(400, "Bad Request")
                    return

        # Check the body
        if self.body:
            content_length = int(request.headers.get("Content-Length", 0))
            request_body = request.rfile.read(content_length)
            if request_body != self.body.bytes:
                request.send_error(400, "Bad Request")
                return

        # Send the response
        if not self.response:
            warnings.warn(
                "No response defined, defaulting to 200",
                RuntimeWarning,
                stacklevel=2,
            )

        request.send_response(self.response or 200)
        for k, v in self.response_headers.items():
            request.send_header(k, v)
        if self.response_body and self.response_body.mime_type:
            request.send_header("Content-Type", self.response_body.mime_type)
        request.end_headers()
        if self.response_body and self.response_body.bytes:
            request.wfile.write(self.response_body.bytes)

    def message_producer(
        self,
        name: str,
        metadata: dict[str, Any] | None,
    ) -> Message:
        """
        Handle a message interaction.

        Args:
            name:
                The name of the message to produce.

            metadata:
                Metadata for the message.
        """
        logger.info("Handling message interaction")
        logger.info("  -> Body: %r", name)
        logger.info("  -> Metadata: %r", metadata)
        assert self.type in ("Sync", "Async"), "Message interactions only"

        assert name == self.description, "Description mismatch"

        contents = self.body.bytes if self.body else None
        return {
            "contents": contents or b"",
            "content_type": self.body.mime_type if self.body else None,
            "metadata": self.metadata,
        }
