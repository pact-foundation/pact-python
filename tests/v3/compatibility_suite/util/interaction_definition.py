"""
Interaction definition.

This module defines the `InteractionDefinition` class, which is used to help
parse the interaction definitions from the compatibility suite, and interact
with the `Pact` and `Interaction` classes.
"""

from __future__ import annotations

import base64
import contextlib
import json
import logging
import sys
import typing
from typing import Any, Literal
from xml.etree import ElementTree

import flask
from flask import request
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
    from pathlib import Path

    from pact.v3.interaction import Interaction
    from pact.v3.pact import Pact
    from tests.v3.compatibility_suite.util.provider import Provider

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
            assert isinstance(
                interaction, HttpInteraction
            ), "Query parameters require an HTTP interaction"
            query = URL.build(query_string=self.query).query
            logger.info("with_query_parameters(%r)", query.items())
            interaction.with_query_parameters(query.items())

        if self.headers:
            assert isinstance(
                interaction, HttpInteraction
            ), "Headers require an HTTP interaction"
            logger.info("with_headers(%r)", self.headers.items())
            interaction.with_headers(self.headers.items())

        if self.body:
            self.body.add_to_interaction(interaction)

        if self.matching_rules:
            logger.info("with_matching_rules(%r)", self.matching_rules)
            interaction.with_matching_rules(self.matching_rules)

        if self.response:
            assert isinstance(
                interaction, HttpInteraction
            ), "Response requires an HTTP interaction"
            logger.info("will_respond_with(%r)", self.response)
            interaction.will_respond_with(self.response)

        if self.response_headers:
            assert isinstance(
                interaction, HttpInteraction
            ), "Response headers require an HTTP interaction"
            logger.info("with_headers(%r)", self.response_headers)
            interaction.with_headers(self.response_headers.items(), "Response")

        if self.response_body:
            assert isinstance(
                interaction, HttpInteraction
            ), "Response body requires an HTTP interaction"
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

    def add_to_provider(self, provider: Provider) -> None:
        """
        Add an interaction to a Flask app.

        Args:
            provider:
                The test provider to add the interaction to.
        """
        logger.debug("Adding %s interaction to Flask app", self.type)
        if self.type == "HTTP":
            self._add_http_to_provider(provider)
        elif self.type == "Sync":
            self._add_sync_to_provider(provider)
        elif self.type == "Async":
            self._add_async_to_provider(provider)
        else:
            msg = f"Unknown interaction type: {self.type}"
            raise ValueError(msg)

    def _add_http_to_provider(self, provider: Provider) -> None:
        """
        Add a HTTP interaction to a Flask app.

        Ths function works by defining a new function to handle the request and
        produce the response. This function is then added to the Flask app as a
        route.

        Args:
            provider:
                The test provider to add the interaction to.
        """
        assert isinstance(self.method, str), "Method must be a string"
        assert isinstance(self.path, str), "Path must be a string"

        logger.info(
            "Adding HTTP '%s %s' interaction to Flask app",
            self.method,
            self.path,
        )
        logger.debug("-> Query: %s", self.query)
        logger.debug("-> Headers: %s", self.headers)
        logger.debug("-> Body: %s", self.body)
        logger.debug("-> Response Status: %s", self.response)
        logger.debug("-> Response Headers: %s", self.response_headers)
        logger.debug("-> Response Body: %s", self.response_body)

        def route_fn() -> flask.Response:
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
                headers=dict(**self.response_headers),
                content_type=self.response_body.mime_type
                if self.response_body
                else None,
                direct_passthrough=True,
            )

        # The route function needs to have a unique name
        clean_name = self.path.replace("/", "_").replace("__", "_")
        route_fn.__name__ = f"{self.method.lower()}_{clean_name}"

        provider.app.add_url_rule(
            self.path,
            view_func=route_fn,
            methods=[self.method],
        )

    def _add_sync_to_provider(self, provider: Provider) -> None:
        """
        Add a synchronous message interaction to a Flask app.

        Args:
            provider:
                The test provider to add the interaction to.
        """
        raise NotImplementedError

    def _add_async_to_provider(self, provider: Provider) -> None:
        """
        Add a synchronous message interaction to a Flask app.

        Args:
            provider:
                The test provider to add the interaction to.
        """
        assert self.description, "Description must be set for async messages"
        provider.messages[self.description] = self

        # All messages are handled by the same route. So we just need to check
        # whether the route has been defined, and if not, define it.
        for rule in provider.app.url_map.iter_rules():
            if rule.rule == "/_pact/message":
                sys.stderr.write("Async message route already defined\n")
                return

        sys.stderr.write("Adding async message route\n")

        @provider.app.post("/_pact/message")
        def post_message() -> flask.Response:
            body: dict[str, Any] = json.loads(request.data)
            description: str = body["description"]

            if description not in provider.messages:
                return flask.Response(
                    response=json.dumps({
                        "error": f"Message {description} not found",
                    }),
                    status=404,
                    headers={"Content-Type": "application/json"},
                    content_type="application/json",
                )

            interaction: InteractionDefinition = provider.messages[description]
            return interaction.create_async_message_response()

    def create_async_message_response(self) -> flask.Response:
        """
        Convert the interaction to a Flask response.

        When an async message needs to be produced, Pact expects the response
        from the special `/_pact/message` endppoint to generate the expected
        message.

        Whilst this is a Response from Flask's perspective, the attributes
        returned
        """
        assert self.type == "Async", "Only async messages are supported"

        if self.metadata:
            self.headers["Pact-Message-Metadata"] = base64.b64encode(
                json.dumps(self.metadata).encode("utf-8")
            ).decode("utf-8")

        return flask.Response(
            response=self.body.bytes or self.body.string or None if self.body else None,
            headers=((k, v) for k, v in self.headers.items()),
            content_type=self.body.mime_type if self.body else None,
            direct_passthrough=True,
        )
