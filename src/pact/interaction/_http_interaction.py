"""
HTTP interaction.
"""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Mapping
from typing import TYPE_CHECKING, Literal

import pact_ffi
from pact.interaction._base import Interaction
from pact.match import AbstractMatcher
from pact.match.matcher import IntegrationJSONEncoder

if TYPE_CHECKING:
    from collections.abc import Iterable

    from typing_extensions import Self


class HttpInteraction(Interaction):
    """
    A synchronous HTTP interaction.

    This class defines a synchronous HTTP interaction between a consumer and a
    provider. It defines a specific request that the consumer makes to the
    provider, and the response that the provider should return.

    This class provides a simple way to define the request and response for an
    HTTP interaction. As many elements are shared between the request and
    response, this class provides a common interface for both. The functions
    intelligently determine whether the element should be added to the request
    or the response based on whether
    [`will_respond_with`][pact.interaction.HttpInteraction.will_respond_with]
    has been called.

    For example, the following two interactions are equivalent:

    ```python
    (
        pact.upon_receiving("a request")
        .with_request("GET", "/")
        .with_header("X-Foo", "bar")
        .will_respond_with(200)
        .with_header("X-Hello", "world")
    )
    ```

    ```python
    (
        pact.upon_receiving("a request")
        .with_request("GET", "/")
        .will_respond_with(200)
        .with_header("X-Foo", "bar", part="Request")
        .with_header("X-Hello", "world", part="Response")
    )
    ```
    """

    def __init__(self, pact_handle: pact_ffi.PactHandle, description: str) -> None:
        """
        Initialise a new HTTP Interaction.

        This class should not be instantiated directly. Instead, an
        `HttpInteraction` should be created using the
        [`upon_receiving`][pact.Pact.upon_receiving] method of a
        [`Pact`][pact.Pact] instance.
        """
        super().__init__(description)
        self.__handle = pact_ffi.new_interaction(pact_handle, description)
        self.__interaction_part = pact_ffi.InteractionPart.REQUEST
        self._request_indices: dict[
            tuple[pact_ffi.InteractionPart, str],
            int,
        ] = defaultdict(int)
        self._parameter_indices: dict[str, int] = defaultdict(int)

    @property
    def _handle(self) -> pact_ffi.InteractionHandle:
        """
        Handle for the Interaction.

        This is used internally by the library to pass the Interaction to the
        underlying Pact library.
        """
        return self.__handle

    @property
    def _interaction_part(self) -> pact_ffi.InteractionPart:
        """
        Interaction part.

        Keeps track whether we are setting by default the request or the
        response in the HTTP interaction.
        """
        return self.__interaction_part

    def with_request(self, method: str, path: str | AbstractMatcher[object]) -> Self:
        """
        Set the request.

        This is the request that the consumer will make to the provider.

        Args:
            method:
                HTTP method for the request.

            path:
                Path for the request.
        """
        if isinstance(path, AbstractMatcher):
            path_str = json.dumps(path, cls=IntegrationJSONEncoder)
        else:
            path_str = path
        pact_ffi.with_request(self._handle, method, path_str)
        return self

    def with_header(
        self,
        name: str,
        value: str | dict[str, str] | AbstractMatcher[object],
        part: Literal["Request", "Response"] | None = None,
    ) -> Self:
        r"""
        Add a header to the request.

        If the same header has multiple values (see [RFC9110
        §5.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-5.2)), then
        the same header must be specified multiple times with _order being
        preserved_. For example

        ```python
        (
            pact.upon_receiving("a request")
            .with_header("X-Foo", "bar")
            .with_header("X-Foo", "baz")
        )
        ```

        will expect a request with the following headers:

        ```http
        X-Foo: bar
        X-Foo: baz
        # Or, equivalently:
        X-Foo: bar, baz
        ```

        Note that repeated headers are _case insensitive_ in accordance with
        [RFC 9110
        §5.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-5.1).

        Args:
            name:
                Name of the header.

            value:
                Value of the header.

            part:
                Whether the header should be added to the request or the
                response.

                If `None`, then the function intelligently determines whether
                the header should be added to the request or the response, based
                on whether the
                [`will_respond_with`][pact.interaction.HttpInteraction.will_respond_with]
                method has been called.
        """
        interaction_part = self._parse_interaction_part(part)
        name_lower = name.lower()
        index = self._request_indices[(interaction_part, name_lower)]
        self._request_indices[(interaction_part, name_lower)] += 1
        if not isinstance(value, str):
            value_str: str = json.dumps(value, cls=IntegrationJSONEncoder)
        else:
            value_str = value
        pact_ffi.with_header_v2(
            self._handle,
            interaction_part,
            name,
            index,
            value_str,
        )
        return self

    def with_headers(
        self,
        headers: dict[str, str] | Iterable[tuple[str, str]],
        part: Literal["Request", "Response"] | None = None,
    ) -> Self:
        """
        Add multiple headers to the request.

        While it is often convenient to use a dictionary to specify headers,
        this does not support repeated headers. If you need to specify repeated
        headers, consider one of the following:

        -   An alternative dictionary implementation which supports repeated
            keys such as [multidict](https://pypi.org/project/multidict/).

        -   Passing in an iterable of key-value tuples.

        -   Make multiple calls to this function or
            [`with_header`][pact.interaction.HttpInteraction.with_header].

        See
        [`with_header`][pact.interaction.HttpInteraction.with_header]
        for more information.

        Args:
            headers:
                Headers to add to the request.

            part:
                Whether the header should be added to the request or the
                response.

                If `None`, then the function intelligently determines whether
                the header should be added to the request or the response, based
                on whether the
                [`will_respond_with`][pact.interaction.HttpInteraction.will_respond_with]
                method has been called.
        """
        if isinstance(headers, dict):
            headers = headers.items()
        for name, value in headers:
            self.with_header(name, value, part)
        return self

    def set_header(
        self,
        name: str,
        value: str,
        part: Literal["Request", "Response"] | None = None,
    ) -> Self:
        r"""
        Add a header to the request.

        Unlike
        [`with_header`][pact.interaction.HttpInteraction.with_header], this
        function does no additional processing of the header value. This is
        useful for headers that contain a JSON object.

        Args:
            name:
                Name of the header.

            value:
                Value of the header.

            part:
                Whether the header should be added to the request or the
                response.

                If `None`, then the function intelligently determines whether
                the header should be added to the request or the response, based
                on whether the
                [`will_respond_with`][pact.interaction.HttpInteraction.will_respond_with]
                method has been called.
        """
        pact_ffi.set_header(
            self._handle,
            self._parse_interaction_part(part),
            name,
            value,
        )
        return self

    def set_headers(
        self,
        headers: dict[str, str] | Iterable[tuple[str, str]],
        part: Literal["Request", "Response"] | None = None,
    ) -> Self:
        """
        Add multiple headers to the request.

        While it is often convenient to use a dictionary to specify headers,
        this does not support repeated headers. If you need to specify repeated
        headers, consider one of the following:

        -   An alternative dictionary implementation which supports repeated
            keys such as [multidict](https://pypi.org/project/multidict/).

        -   Passing in an iterable of key-value tuples.

        -   Make multiple calls to this function or
            [`with_header`][pact.interaction.HttpInteraction.with_header].

        See [`set_header`][pact.interaction.HttpInteraction.set_header] for
        more information.

        Args:
            headers:
                Headers to add to the request.

            part:
                Whether the headers should be added to the request or the
                response.

                If `None`, then the function intelligently determines whether
                the headers should be added to the request or the response,
                based on whether the
                [`will_respond_with`][pact.interaction.HttpInteraction.will_respond_with]
                method has been called.
        """
        if isinstance(headers, dict):
            headers = headers.items()
        for name, value in headers:
            self.set_header(name, value, part)
        return self

    def with_query_parameter(
        self,
        name: str,
        value: object | AbstractMatcher[object],
    ) -> Self:
        r"""
        Add a query to the request.

        This is the query parameter that the consumer will send to the provider.

        If the same parameter can support multiple values, then the same
        parameter can be specified multiple times:

        ```python
        (
            pact.upon_receiving("a request")
            .with_query_parameter("name", "John")
            .with_query_parameter("name", "Mary")
        )
        ```

        Args:
            name:
                Name of the query parameter.

            value:
                Value of the query parameter.
        """
        index = self._parameter_indices[name]
        self._parameter_indices[name] += 1
        if not isinstance(value, str):
            value_str: str = json.dumps(value, cls=IntegrationJSONEncoder)
        else:
            value_str = value
        pact_ffi.with_query_parameter_v2(
            self._handle,
            name,
            index,
            value_str,
        )
        return self

    def with_query_parameters(
        self,
        parameters: Mapping[str, object | AbstractMatcher[object]]
        | Iterable[tuple[str, object | AbstractMatcher[object]]],
    ) -> Self:
        """
        Add multiple query parameters to the request.

        While it is often convenient to use a dictionary to specify query
        parameters, this does not support repeated keys. If you need to specify
        repeated keys, consider one of the following:

        -   An alternative dictionary implementation which supports repeated
            keys such as [multidict](https://pypi.org/project/multidict/).

        -   Passing in an iterable of key-value tuples.

        -   Make multiple calls to this function or
            [`with_query_parameter`][pact.interaction.HttpInteraction.with_query_parameter].

        See
        [`with_query_parameter`][pact.interaction.HttpInteraction.with_query_parameter]
        for more information.

        Args:
            parameters:
                Query parameters to add to the request.
        """
        if isinstance(parameters, Mapping):
            parameters = parameters.items()
        for name, value in parameters:
            self.with_query_parameter(name, value)
        return self

    def will_respond_with(self, status: int) -> Self:
        """
        Set the response status.

        Ideally, this function is called once all of the request information has
        been set. This allows functions such as
        [`with_header`][pact.interaction.HttpInteraction.with_header]
        to intelligently determine whether this is a request or response header.

        Alternatively, the `part` argument can be used to explicitly specify
        whether the header should be added to the request or the response.

        Args:
            status:
                Status for the response.
        """
        pact_ffi.response_status(self._handle, status)
        self.__interaction_part = pact_ffi.InteractionPart.RESPONSE
        return self
