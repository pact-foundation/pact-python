"""
Pact between a consumer and a provider.

This module defines the classes that are used to define a Pact between a
consumer and a provider. It defines the interactions between the two parties,
and provides the functionality to verify that the interactions are satisfied.

For the roles of consumer and provider, see the documentation for the
`pact.v3.service` module.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Iterable, Literal

import pact.v3.ffi
from pact.v3.interaction import Interaction

if TYPE_CHECKING:
    try:
        from typing import Self
    except ImportError:
        from typing_extensions import Self


class HttpInteraction(Interaction):
    """
    A synchronous HTTP interaction.

    This class defines a synchronous HTTP interaction between a consumer and a
    provider. It defines a specific request that the consumer makes to the
    provider, and the response that the provider should return.
    """

    def __init__(self, pact_handle: pact.v3.ffi.PactHandle, description: str) -> None:
        """
        Initialise a new HTTP Interaction.

        This function should not be called directly. Instead, an Interaction
        should be created using the
        [`upon_receiving(...)`][pact.v3.Pact.upon_receiving] method of a
        [`Pact`][pact.v3.Pact] instance.
        """
        super().__init__(description)
        self.__handle = pact.v3.ffi.new_interaction(pact_handle, description)
        self.__interaction_part = pact.v3.ffi.InteractionPart.REQUEST
        self._request_indices: dict[
            tuple[pact.v3.ffi.InteractionPart, str],
            int,
        ] = defaultdict(int)
        self._parameter_indices: dict[str, int] = defaultdict(int)

    @property
    def _handle(self) -> pact.v3.ffi.InteractionHandle:
        """
        Handle for the Interaction.

        This is used internally by the library to pass the Interaction to the
        underlying Pact library.
        """
        return self.__handle

    @property
    def _interaction_part(self) -> pact.v3.ffi.InteractionPart:
        """
        Interaction part.

        Keeps track whether we are setting by default the request or the
        response in the HTTP interaction.
        """
        return self.__interaction_part

    def with_request(self, method: str, path: str) -> Self:
        """
        Set the request.

        This is the request that the consumer will make to the provider.

        Args:
            method:
                HTTP method for the request.
            path:
                Path for the request.
        """
        pact.v3.ffi.with_request(self._handle, method, path)
        return self

    def with_header(
        self,
        name: str,
        value: str,
        part: Literal["Request", "Response"] | None = None,
    ) -> Self:
        r"""
        Add a header to the request.

        # Repeated Headers

        If the same header has multiple values ([see RFC9110
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

        # JSON Matching

        Pact's matching rules are defined in the [upstream
        documentation](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.18/rust/pact_ffi/IntegrationJson.md)
        and support a wide range of matching rules. These can be specified
        using a JSON object as a strong using `json.dumps(...)`. For example,
        the above rule whereby the `X-Foo` header has multiple values can be
        specified as:

        ```python
        (
            pact.upon_receiving("a request")
            .with_header(
                "X-Foo",
                json.dumps({
                    "value": ["bar", "baz"],
                }),
            )
        )
        ```

        It is also possible to have a more complicated Regex pattern for the
        header. For example, a pattern for an `Accept-Version` header might be
        specified as:

        ```python
        (
            pact.upon_receiving("a request").with_header(
                "Accept-Version",
                json.dumps({
                    "value": "1.2.3",
                    "pact:matcher:type": "regex",
                    "regex": r"\d+\.\d+\.\d+",
                }),
            )
        )
        ```

        If the value of the header is expected to be a JSON object and clashes
        with the above syntax, then it is recommended to make use of the
        [`set_header(...)`][pact.v3.Interaction.set_header] method instead.

        Args:
            name:
                Name of the header.

            value:
                Value of the header.

            part:
                Whether the header should be added to the request or the
                response. If `None`, then the function intelligently determines
                whether the header should be added to the request or the
                response, based on whether the
                [`will_respond_with(...)`][pact.v3.Interaction.will_respond_with]
                method has been called.
        """
        interaction_part = self._parse_interaction_part(part)
        name_lower = name.lower()
        index = self._request_indices[(interaction_part, name_lower)]
        self._request_indices[(interaction_part, name_lower)] += 1
        pact.v3.ffi.with_header_v2(
            self._handle,
            interaction_part,
            name,
            index,
            value,
        )
        return self

    def with_headers(
        self,
        headers: dict[str, str] | Iterable[tuple[str, str]],
        part: Literal["Request", "Response"] | None = None,
    ) -> Self:
        """
        Add multiple headers to the request.

        Note that due to the requirement of Python dictionaries to
        have unique keys, it is _not_ possible to specify a header multiple
        times to create a multi-valued header. Instead, you may:

        -   Use an alternative data structure. Any iterable of key-value pairs
            is accepted, including a list of tuples, a list of lists, or a
            dictionary view.

        -   Make multiple calls to
            [`with_header(...)`][pact.v3.Interaction.with_header] or
            [`with_headers(...)`][pact.v3.Interaction.with_headers].

        -   Specify the multiple values in a JSON object of the form:

            ```python
            (
                pact.upon_receiving("a request")
                .with_headers({
                    "X-Foo": json.dumps({
                        "value": ["bar", "baz"],
                    }),
                )
            )
            ```

        See [`with_header(...)`][pact.v3.Interaction.with_header] for more
        information.

        Args:
            headers:
                Headers to add to the request.

            part:
                Whether the header should be added to the request or the
                response. If `None`, then the function intelligently determines
                whether the header should be added to the request or the
                response, based on whether the
                [`will_respond_with(...)`][pact.v3.Interaction.will_respond_with]
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

        Unlike [`with_header(...)`][pact.v3.Interaction.with_header], this
        function does no additional processing of the header value. This is
        useful for headers that contain a JSON object.

        Args:
            name:
                Name of the header.

            value:
                Value of the header.

            part:
                Whether the header should be added to the request or the
                response. If `None`, then the function intelligently determines
                whether the header should be added to the request or the
                response, based on whether the
                [`will_respond_with(...)`][pact.v3.Interaction.will_respond_with]
                method has been called.
        """
        pact.v3.ffi.set_header(
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

        This function intelligently determines whether the header should be
        added to the request or the response, based on whether the
        [`will_respond_with(...)`][pact.v3.Interaction.will_respond_with] method
        has been called.

        See [`set_header(...)`][pact.v3.Interaction.set_header] for more
        information.

        Args:
            headers:
                Headers to add to the request.

            part:
                Whether the headers should be added to the request or the
                response. If `None`, then the function intelligently determines
                whether the header should be added to the request or the
                response, based on whether the
                [`will_respond_with(...)`][pact.v3.Interaction.will_respond_with]
                method has been called.
        """
        if isinstance(headers, dict):
            headers = headers.items()
        for name, value in headers:
            self.set_header(name, value, part)
        return self

    def with_query_parameter(self, name: str, value: str) -> Self:
        r"""
        Add a query to the request.

        This is the query parameter(s) that the consumer will send to the
        provider.

        If the same parameter can support multiple values, then the same
        parameter can be specified multiple times:

        ```python
        (
            pact.upon_receiving("a request")
            .with_query_parameter("name", "John")
            .with_query_parameter("name", "Mary")
        )
        ```

        The above can equivalently be specified as:

        ```python
        (
            pact.upon_receiving("a request").with_query_parameter(
                "name",
                json.dumps({
                    "value": ["John", "Mary"],
                }),
            )
        )
        ```

        It is also possible to have a more complicated Regex pattern for the
        paramater. For example, a pattern for an `version` parameter might be
        specified as:

        ```python
        (
            pact.upon_receiving("a request").with_query_parameter(
                "version",
                json.dumps({
                    "value": "1.2.3",
                    "pact:matcher:type": "regex",
                    "regex": r"\d+\.\d+\.\d+",
                }),
            )
        )
        ```

        For more information on the format of the JSON object, see the [upstream
        documentation](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.18/rust/pact_ffi/IntegrationJson.md).

        Args:
            name:
                Name of the query parameter.

            value:
                Value of the query parameter.
        """
        index = self._parameter_indices[name]
        self._parameter_indices[name] += 1
        pact.v3.ffi.with_query_parameter_v2(
            self._handle,
            name,
            index,
            value,
        )
        return self

    def with_query_parameters(
        self,
        parameters: dict[str, str] | Iterable[tuple[str, str]],
    ) -> Self:
        """
        Add multiple query parameters to the request.

        See [`with_query_parameter(...)`][pact.v3.Interaction.with_query_parameter]
        for more information.

        Args:
            parameters:
                Query parameters to add to the request.
        """
        if isinstance(parameters, dict):
            parameters = parameters.items()
        for name, value in parameters:
            self.with_query_parameter(name, value)
        return self

    def will_respond_with(self, status: int) -> Self:
        """
        Set the response status.

        Ideally, this function is called once all of the request information has
        been set. This allows functions such as
        [`with_header(...)`][pact.v3.Interaction.with_header] to intelligently
        determine whether this is a request or response header.

        Alternatively, the `part` argument can be used to explicitly specify
        whether the header should be added to the request or the response.

        Args:
            status:
                Status for the response.
        """
        pact.v3.ffi.response_status(self._handle, status)
        self.__interaction_part = pact.v3.ffi.InteractionPart.RESPONSE
        return self
