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
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Literal, Set

from yarl import URL

import pact.v3.ffi

if TYPE_CHECKING:
    from types import TracebackType

    try:
        from typing import Self
    except ImportError:
        from typing_extensions import Self


class Interaction:
    """
    Interaction between a consumer and a provider.

    This class defines an interaction between a consumer and a provider. It
    defines a specific request that the consumer makes to the provider, and the
    response that the provider should return.

    A set of interactions between a consumer and a provider is called a Pact.
    """

    def __init__(self, pact_handle: pact.v3.ffi.PactHandle, description: str) -> None:
        """
        Initialise a new Interaction.

        This function should not be called directly. Instead, an Interaction
        should be created using the
        [`upon_receiving(...)`][pact.v3.Pact.upon_receiving] method of a
        [`Pact`][pact.v3.Pact] instance.
        """
        self._handle = pact.v3.ffi.new_interaction(pact_handle, description)
        self._is_request = True
        self._request_indices: dict[
            tuple[pact.v3.ffi.InteractionPart, str],
            int,
        ] = defaultdict(int)
        self._parameter_indices: dict[str, int] = defaultdict(int)

    def __str__(self) -> str:
        """
        Informal string representation of the Interaction.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """
        Information-rich string representation of the Interaction.
        """
        raise NotImplementedError

    def given(self, state: str) -> Interaction:
        """
        Set the provider state.

        This is the state that the provider should be in when the Interaction is
        executed.

        Args:
            state:
                Provider state for the Interaction.
        """
        pact.v3.ffi.given(self._handle, state)
        return self

    def with_request(self, method: str, path: str) -> Interaction:
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

    def _interaction_part(
        self,
        part: Literal["Request", "Response", None],
    ) -> pact.v3.ffi.InteractionPart:
        """
        Convert the input into an InteractionPart.
        """
        part = part or ("Request" if self._is_request else "Response")
        if part == "Request":
            return pact.v3.ffi.InteractionPart.REQUEST
        if part == "Response":
            return pact.v3.ffi.InteractionPart.RESPONSE
        msg = f"Invalid part: {part}"
        raise ValueError(msg)

    def with_header(
        self,
        name: str,
        value: str,
        part: Literal["Request", "Response"] | None = None,
    ) -> Interaction:
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
        documentation](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.9/rust/pact_ffi/IntegrationJson.md)
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
            pact.upon_receiving("a request")
            .with_header(
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
        interaction_part = self._interaction_part(part)
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
    ) -> Interaction:
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
    ) -> Interaction:
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
            self._interaction_part(part),
            name,
            value,
        )
        return self

    def set_headers(
        self,
        headers: dict[str, str] | Iterable[tuple[str, str]],
        part: Literal["Request", "Response"] | None = None,
    ) -> Interaction:
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

    def with_query_parameter(self, name: str, value: str) -> Interaction:
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
            pact.upon_receiving("a request")
            .with_query_parameter(
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
            pact.upon_receiving("a request")
            .with_query_parameter(
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
        documentation](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.9/rust/pact_ffi/IntegrationJson.md).

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
    ) -> Interaction:
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

    def with_body(
        self,
        body: str | None = None,
        content_type: str = "text/plain",
        part: Literal["Request", "Response"] | None = None,
    ) -> Interaction:
        """
        Set the body of the request.

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
                the body should be added to the request or the response, based
                on whether the
                [`will_respond_with(...)`][pact.v3.Interaction.will_respond_with]
                method has been called.
        """
        pact.v3.ffi.with_body(
            self._handle,
            self._interaction_part(part),
            content_type,
            body,
        )
        return self

    def will_respond_with(self, status: int) -> Interaction:
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
        self._is_request = False
        return self


class Pact:
    """
    A Pact between a consumer and a provider.

    This class defines a Pact between a consumer and a provider. It is the
    central class in Pact's framework, and is responsible for defining the
    interactions between the two parties.

    One Pact instance should be created for each provider that a consumer
    interacts with. This instance can then be used to define the interactions
    between the two parties.
    """

    def __init__(
        self,
        consumer: str,
        provider: str,
    ) -> None:
        """
        Initialise a new Pact.

        Args:
            consumer:
                Name of the consumer.

            provider:
                Name of the provider.
        """
        if not consumer:
            msg = "Consumer name cannot be empty."
            raise ValueError(msg)
        if not provider:
            msg = "Provider name cannot be empty."
            raise ValueError(msg)

        self._consumer = consumer
        self._provider = provider
        self._interactions: Set[Interaction] = set()
        self._handle: pact.v3.ffi.PactHandle = pact.v3.ffi.new_pact(
            consumer,
            provider,
        )

    def __str__(self) -> str:
        """
        Informal string representation of the Pact.
        """
        return f"{self.consumer} -> {self.provider}"

    def __repr__(self) -> str:
        """
        Information-rich string representation of the Pact.
        """
        return "<Pact: {}>".format(
            ", ".join(
                [
                    f"consumer={self.consumer!r}",
                    f"provider={self.provider!r}",
                    f"handle={self._handle!r}",
                ],
            ),
        )

    @property
    def consumer(self) -> str:
        """
        Consumer name.
        """
        return self._consumer

    @property
    def provider(self) -> str:
        """
        Provider name.
        """
        return self._provider

    def upon_receiving(self, description: str) -> Interaction:
        """
        Create a new Interaction.

        This is an alias for [`interaction(...)`][pact.v3.Pact.interaction].

        Args:
            description:
                Description of the interaction. This must be unique
                within the Pact.
        """
        return Interaction(self._handle, description)

    def serve(
        self,
        addr: str = "localhost",
        port: int = 0,
        transport: str = "http",
        transport_config: str | None = None,
    ) -> PactServer:
        """
        Return a mock server for the Pact.

        This function configures a mock server for the Pact. The mock server
        is then started when the Pact is entered into a `with` block:

        ```python
        pact = Pact("consumer", "provider")
        with pact.serve() as srv:
            ...
        ```

        Args:
            addr:
                Address to bind the mock server to. Defaults to `localhost`.

            port:
                Port to bind the mock server to. Defaults to `0`, which will
                select a random port.

            transport:
                Transport to use for the mock server. Defaults to `HTTP`.

            transport_config:
                Configuration for the transport. This is specific to the
                transport being used and should be a JSON string.
        """
        return PactServer(
            self._handle,
            addr,
            port,
            transport,
            transport_config,
        )


class PactServer:
    """
    Pact Server.

    This class handles the lifecycle of the Pact mock server. It is responsible
    for starting the mock server when the Pact is entered into a `with` block,
    and stopping the mock server when the block is exited.
    """

    def __init__(  # noqa: PLR0913
        self,
        pact_handle: pact.v3.ffi.PactHandle,
        host: str = "localhost",
        port: int = 0,
        transport: str = "HTTP",
        transport_config: str | None = None,
    ) -> None:
        """
        Initialise a new Pact Server.

        This function should not be called directly. Instead, a Pact Server
        should be created using the
        [`serve(...)`][pact.v3.Pact.serve] method of a
        [`Pact`][pact.v3.Pact] instance:

        ```python
        pact = Pact("consumer", "provider")
        with pact.serve(...) as srv:
            ...
        ```

        Args:
            pact_handle:
                Handle for the Pact.

            host:
                Hostname of IP for the mock server.

            port:
                Port to bind the mock server to. The value of `0` will select a
                random available port.

            transport:
                Transport to use for the mock server.

            transport_config:
                Configuration for the transport. This is specific to the
                transport being used and should be a JSON string.
        """
        self._host = host
        self._port = port
        self._transport = transport
        self._transport_config = transport_config
        self._pact_handle = pact_handle
        self._handle: None | pact.v3.ffi.PactServerHandle = None

    @property
    def port(self) -> int:
        """
        Port on which the server is running.

        If the server is not running, then this will be `0`.
        """
        # Unlike the other properties, this value might be different to what was
        # passed in to the constructor as the server can be started on a random
        # port.
        return self._handle.port if self._handle else 0

    @property
    def host(self) -> str:
        """
        Address to which the server is bound.
        """
        return self._host

    @property
    def transport(self) -> str:
        """
        Transport method.
        """
        return self._transport

    @property
    def url(self) -> URL:
        """
        Base URL for the server.
        """
        return URL(str(self))

    def __str__(self) -> str:
        """
        URL for the server.
        """
        return f"{self.transport}://{self.host}:{self.port}"

    def __repr__(self) -> str:
        """
        Information-rich string representation of the Pact Server.
        """
        return "<PactServer: {}>".format(
            ", ".join(
                [
                    f"transport={self.transport!r}",
                    f"host={self.host!r}",
                    f"port={self.port!r}",
                    f"handle={self._handle!r}",
                    f"pact={self._pact_handle!r}",
                ],
            ),
        )

    def __enter__(self) -> Self:
        """
        Launch the server.

        Once the server is running, it is generally no possible to make
        modifications to the underlying Pact.
        """
        self._handle = pact.v3.ffi.create_mock_server_for_transport(
            self._pact_handle,
            self._host,
            self._port,
            self._transport,
            self._transport_config,
        )

        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        """
        Stop the server.
        """
        if self._handle:
            self._handle = None

    def __truediv__(self, other: str) -> URL:
        """
        URL for the server.
        """
        if isinstance(other, str):
            return self.url / other
        return NotImplemented

    def write_file(
        self,
        directory: str | Path | None = None,
        *,
        overwrite: bool = False,
    ) -> None:
        """
        Write out the pact to a file.

        Args:
            directory:
                The directory to write the pact to. If the directory does not
                exist, it will be created. The filename will be
                automatically generated from the underlying Pact.

            overwrite:
                Whether or not to overwrite the file if it already exists.
        """
        if not self._handle:
            msg = "The server is not running."
            raise RuntimeError(msg)

        directory = Path(directory) if directory else Path.cwd()
        if not directory.exists():
            directory.mkdir(parents=True)
        elif not directory.is_dir():
            msg = f"{directory} is not a directory"
            raise ValueError(msg)

        pact.v3.ffi.write_pact_file(
            self._handle,
            str(directory),
            overwrite=overwrite,
        )
