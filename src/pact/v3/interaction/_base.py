"""
Pact between a consumer and a provider.

This module defines the classes that are used to define a Pact between a
consumer and a provider. It defines the interactions between the two parties,
and provides the functionality to verify that the interactions are satisfied.

For the roles of consumer and provider, see the documentation for the
`pact.v3.service` module.
"""

from __future__ import annotations

import abc
import json
from typing import TYPE_CHECKING, Any, Literal, overload

import pact.v3.ffi
from pact.v3.match.matcher import IntegrationJSONEncoder

if TYPE_CHECKING:
    from pathlib import Path

    from pact.v3.match import Matcher

    try:
        from typing import Self
    except ImportError:
        from typing_extensions import Self


class Interaction(abc.ABC):
    """
    Interaction between a consumer and a provider.

    This abstract class defines an interaction between a consumer and a
    provider. The concrete subclasses define the type of interaction, and
    include:

    -  [`HttpInteraction`][pact.v3.interaction.HttpInteraction]
    -  [`AsyncMessageInteraction`][pact.v3.interaction.AsyncMessageInteraction]
    -  [`SyncMessageInteraction`][pact.v3.interaction.SyncMessageInteraction]

    # Interaction Part

    For HTTP and synchronous message interactions, the interaction is split into
    two parts: the request and the response. The interaction part is used to
    specify which part of the interaction is being set. This is specified using
    the `part` argument of various methods (which defaults to an intelligent
    choice based on the order of the methods called).

    The asynchronous message interaction does not have parts, as the interaction
    contains a single message from the provider (a.ka. the producer of the
    message) to the consumer. An attempt to set a response part will raise an
    error.
    """

    def __init__(self, description: str) -> None:
        """
        Create a new Interaction.

        As this class is abstract, this function should not be called directly
        but should instead be called through one of the concrete subclasses.

        Args:
            description:
                Description of the interaction. This must be unique within the
                Pact.
        """
        self._description = description

    def __str__(self) -> str:
        """
        Nice representation of the Interaction.
        """
        return f"{self.__class__.__name__}({self._description})"

    def __repr__(self) -> str:
        """
        Debugging representation of the Interaction.
        """
        return f"{self.__class__.__name__}({self._handle!r})"

    @property
    @abc.abstractmethod
    def _handle(self) -> pact.v3.ffi.InteractionHandle:
        """
        Handle for the Interaction.

        This is used internally by the library to pass the Interaction to the
        underlying Pact library.
        """

    @property
    @abc.abstractmethod
    def _interaction_part(self) -> pact.v3.ffi.InteractionPart:
        """
        Interaction part.

        Where interactions have multiple parts, this property keeps track
        of which part is currently being set.
        """

    def _parse_interaction_part(
        self,
        part: Literal["Request", "Response", None],
    ) -> pact.v3.ffi.InteractionPart:
        """
        Convert the input into an InteractionPart.
        """
        if part == "Request":
            return pact.v3.ffi.InteractionPart.REQUEST
        if part == "Response":
            return pact.v3.ffi.InteractionPart.RESPONSE
        if part is None:
            return self._interaction_part
        msg = f"Invalid part: {part}"
        raise ValueError(msg)

    @overload
    def given(self, state: str) -> Self: ...

    @overload
    def given(self, state: str, *, name: str, value: str) -> Self: ...

    @overload
    def given(self, state: str, *, parameters: dict[str, Any] | str) -> Self: ...

    def given(
        self,
        state: str,
        *,
        name: str | None = None,
        value: str | None = None,
        parameters: dict[str, Any] | str | None = None,
    ) -> Self:
        """
        Set the provider state.

        This is the state that the provider should be in when the Interaction is
        executed. When the provider is being verified, the provider state is
        passed to the provider so that its internal state can be set to match
        the provider state.

        In its simplest form, the provider state is a string. For example, to
        match a provider state of `a user exists`, you would use:

        ```python
        pact.upon_receiving("a request").given("a user exists")
        ```

        It is also possible to specify a parameter that will be used to match
        the provider state. For example, to match a provider state of `a user
        exists` with a parameter `id` that has the value `123`, you would use:

        ```python
        (
            pact.upon_receiving("a request").given(
                "a user exists",
                name="id",
                value="123",
            )
        )
        ```

        Lastly, it is possible to specify multiple parameters that will be used
        to match the provider state. For example, to match a provider state of
        `a user exists` with a parameter `id` that has the value `123` and a
        parameter `name` that has the value `John`, you would use:

        ```python
        (
            pact.upon_receiving("a request").given(
                "a user exists",
                parameters={
                    "id": "123",
                    "name": "John",
                },
            )
        )
        ```

        This function can be called repeatedly to specify multiple provider
        states for the same Interaction. If the same `state` is specified with
        different parameters, then the parameters are merged together. The above
        example with multiple parameters can equivalently be specified as:

        ```python
        (
            pact.upon_receiving("a request")
            .given("a user exists", name="id", value="123")
            .given("a user exists", name="name", value="John")
        )
        ```

        Args:
            state:
                Provider state for the Interaction.

            name:
                Name of the parameter. This must be specified in conjunction
                with `value`.

            value:
                Value of the parameter. This must be specified in conjunction
                with `name`.

            parameters:
                Key-value pairs of parameters to use for the provider state.
                These must be encodable using [`json.dumps(...)`][json.dumps].
                Alternatively, a string contained the JSON object can be passed
                directly.

                If the string does not contain a valid JSON object, then the
                string is passed directly as follows:

                ```python
                (
                    pact.upon_receiving("a request").given(
                        "a user exists",
                        name="value",
                        value=parameters,
                    )
                )
                ```

        Raises:
            ValueError:
                If the combination of arguments is invalid or inconsistent.
        """
        if name is not None and value is not None and parameters is None:
            pact.v3.ffi.given_with_param(self._handle, state, name, value)
        elif name is None and value is None and parameters is not None:
            if isinstance(parameters, dict):
                pact.v3.ffi.given_with_params(
                    self._handle,
                    state,
                    json.dumps(parameters),
                )
            else:
                pact.v3.ffi.given_with_params(self._handle, state, parameters)
        elif name is None and value is None and parameters is None:
            pact.v3.ffi.given(self._handle, state)
        else:
            msg = "Invalid combination of arguments."
            raise ValueError(msg)
        return self

    def with_body(
        self,
        body: str | dict[str, Any] | Matcher[Any] | None = None,
        content_type: str | None = None,
        part: Literal["Request", "Response"] | None = None,
    ) -> Self:
        """
        Set the body of the request or response.

        Args:
            body:
                Body of the request. If this is `None`, then the body is
                empty.

            content_type:
                Content type of the body. This is ignored if the `Content-Type`
                header has already been set.

            part:
                Whether the body should be added to the request or the response.
                If `None`, then the function intelligently determines whether
                the body should be added to the request or the response.
        """
        if body and isinstance(body, str):
            body_str = body
        else:
            body_str = json.dumps(body, cls=IntegrationJSONEncoder)

        pact.v3.ffi.with_body(
            self._handle,
            self._parse_interaction_part(part),
            content_type,
            body_str,
        )
        return self

    def with_binary_body(
        self,
        body: bytes | None,
        content_type: str | None = None,
        part: Literal["Request", "Response"] | None = None,
    ) -> Self:
        """
        Adds a binary body to the request or response.

        Note that for HTTP interactions, this function will overwrite the body
        if it has been set using
        [`with_body(...)`][pact.v3.interaction.Interaction.with_body].

        Args:
            part:
                Whether the body should be added to the request or the response.
                If `None`, then the function intelligently determines whether
                the body should be added to the request or the response.

            content_type:
                Content type of the body. This is ignored if the `Content-Type`
                header has already been set.

            body:
                Body of the request.
        """
        pact.v3.ffi.with_binary_body(
            self._handle,
            self._parse_interaction_part(part),
            content_type,
            body,
        )
        return self

    def with_metadata(
        self,
        __metadata: dict[str, str] | None = None,
        __part: Literal["Request", "Response"] | None = None,
        /,
        **kwargs: str,
    ) -> Self:
        """
        Set metadata for the interaction.

        This function may either be called with a single dictionary of metadata,
        or with keyword arguments that are the key-value pairs of the metadata
        (or a combination therefore):

        ```python
        interaction.with_metadata({"key": "value", "key two": "value two"})
        interaction.with_metadata(foo="bar", baz="qux")
        ```

        The value of `None` will remove the metadata key from the interaction.
        This is distinct from using an empty string or a string containing the
        JSON `null` value, which will set the metadata key to an empty string or
        the JSON `null` value, respectively.

        !!! note

            There are two special keys which cannot be used as keyword
            arguments: `__metadata` and `__part`. Should there ever be a need
            to set metadata with one of these keys, they must be passed through
            as a dictionary:

            ```python
            interaction.with_metadata({"__metadata": "value", "__part": 1})
            ```

        Args:
            ___metadata:
                Dictionary of metadata keys and associated values.

            __part:
                Whether the metadata should be added to the request or the
                response. If `None`, then the function intelligently determines
                whether the body should be added to the request or the response.

            **kwargs:
                Additional metadata key-value pairs.

        Returns:
            The current instance of the interaction.
        """
        part = self._parse_interaction_part(__part)
        for k, v in (__metadata or {}).items():
            pact.v3.ffi.with_metadata(
                self._handle,
                k,
                v,
                part,
            )
        for k, v in kwargs.items():
            pact.v3.ffi.with_metadata(
                self._handle,
                k,
                v,
                part,
            )
        return self

    def with_multipart_file(
        self,
        part_name: str,
        path: Path | None,
        content_type: str | None = None,
        part: Literal["Request", "Response"] | None = None,
        boundary: str | None = None,
    ) -> Self:
        """
        Adds a binary file as the body of a multipart request or response.

        The content type of the body will be set to a MIME multipart message.
        """
        pact.v3.ffi.with_multipart_file_v2(
            self._handle,
            self._parse_interaction_part(part),
            content_type,
            path,
            part_name,
            boundary,
        )
        return self

    def set_key(self, key: str | None) -> Self:
        """
        Sets the key for the interaction.

        This is used by V4 interactions to set the key of the interaction, which
        can subsequently used to reference the interaction.
        """
        pact.v3.ffi.set_key(self._handle, key)
        return self

    def set_pending(self, *, pending: bool) -> Self:
        """
        Mark the interaction as pending.

        This is used by V4 interactions to mark the interaction as pending, in
        which case the provider is not expected to honour the interaction.
        """
        pact.v3.ffi.set_pending(self._handle, pending=pending)
        return self

    def set_comment(self, key: str, value: Any | None) -> Self:  # noqa: ANN401
        """
        Set a comment for the interaction.

        This is used by V4 interactions to set a comment for the interaction. A
        comment consists of a key-value pair, where the key is a string and the
        value is anything that can be encoded as JSON.

        Args:
            key:
                Key for the comment.

            value:
                Value for the comment. This must be encodable using
                [`json.dumps(...)`][json.dumps], or an existing JSON string. The
                value of `None` will remove the comment with the given key.

        # Warning

        This function will overwrite any existing comment with the same key. In
        particular, the `text` key is used by `add_text_comment`.
        """
        if isinstance(value, str) or value is None:
            pact.v3.ffi.set_comment(self._handle, key, value)
        else:
            pact.v3.ffi.set_comment(self._handle, key, json.dumps(value))
        return self

    def add_text_comment(self, comment: str) -> Self:
        """
        Add a text comment for the interaction.

        This is used by V4 interactions to set arbitrary text comments for the
        interaction.

        Args:
            comment:
                Text of the comment.

        # Warning

        Internally, the comments are appended to an array under the `text`
        comment key. Care should be taken to ensure that conflicts are not
        introduced by
        [`set_comment`][pact.v3.interaction.Interaction.set_comment].
        """
        pact.v3.ffi.add_text_comment(self._handle, comment)
        return self

    def test_name(
        self,
        name: str,
    ) -> Self:
        """
        Set the test name annotation for the interaction.

        This is used by V4 interactions to set the name of the test.

        Args:
            name:
                Name of the test.
        """
        pact.v3.ffi.interaction_test_name(self._handle, name)
        return self

    def with_plugin_contents(
        self,
        contents: dict[str, Any] | str,
        content_type: str,
        part: Literal["Request", "Response"] | None = None,
    ) -> Self:
        """
        Set the interaction content using a plugin.

        The value of `contents` is passed directly to the plugin as a JSON
        string. The plugin will document the format of the JSON content.

        Args:
            contents:
                Body of the request. If this is `None`, then the body is empty.

            content_type:
                Content type of the body. This is ignored if the `Content-Type`
                header has already been set.

            part:
                Whether the body should be added to the request or the response.
                If `None`, then the function intelligently determines whether
                the body should be added to the request or the response.
        """
        if isinstance(contents, dict):
            contents = json.dumps(contents)

        pact.v3.ffi.interaction_contents(
            self._handle,
            self._parse_interaction_part(part),
            content_type,
            contents,
        )
        return self

    def with_matching_rules(
        self,
        rules: dict[str, Any] | str,
        part: Literal["Request", "Response"] | None = None,
    ) -> Self:
        """
        Add matching rules to the interaction.

        Matching rules are used to specify how the request or response should be
        matched. This is useful for specifying that certain parts of the request
        or response are flexible, such as the date or time.

        Args:
            rules:
                Matching rules to add to the interaction. This must be
                encodable using [`json.dumps(...)`][json.dumps], or a string.

            part:
                Whether the matching rules should be added to the request or the
                response. If `None`, then the function intelligently determines
                whether the matching rules should be added to the request or the
                response.
        """
        if isinstance(rules, dict):
            rules = json.dumps(rules)

        pact.v3.ffi.with_matching_rules(
            self._handle,
            self._parse_interaction_part(part),
            rules,
        )
        return self

    def with_generators(
        self,
        generators: dict[str, Any] | str,
        part: Literal["Request", "Response"] | None = None,
    ) -> Self:
        """
        Add generators to the interaction.

        Generators are used to adjust how parts of the request or response are
        generated when the Pact is being tested. This can be useful for fields
        that vary each time the request is made, such as a timestamp.

        Args:
            generators:
                Generators to add to the interaction. This must be encodable using
                [`json.dumps(...)`][json.dumps], or a string.

            part:
                Whether the generators should be added to the request or the
                response. If `None`, then the function intelligently determines
                whether the generators should be added to the request or the
                response.
        """
        if isinstance(generators, dict):
            generators = json.dumps(generators)

        pact.v3.ffi.with_generators(
            self._handle,
            self._parse_interaction_part(part),
            generators,
        )
        return self
