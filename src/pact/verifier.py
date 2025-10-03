"""
Verifier for Pact.

The Verifier is used to verify that a provider meets the expectations of a
consumer. This is done by replaying interactions from the consumer against the
provider, and ensuring that the provider's responses match the expectations set
by the consumer.

The interactions to be verified can be sourced either from local Pact files or
from a Pact Broker. The Verifier can be configured to filter interactions based
on their description and state, and to set the provider information and
transports.

When performing the verification, Pact will replay the interactions from the
consumer against the provider and ensure that the provider's responses match the
expectations set by the consumer.

!!! info

    The interface provided by this module could be improved. If you have any
    suggestions, please consider creating a new [GitHub
    discussion](https://github.com/pact-foundation/pact-python/discussions) or
    reaching out over [Slack](https://slack.pact.io).

## Usage

The general usage of the Verifier is as follows:

```python
from pact import Verifier


# In the case of local Pact files
verifier = (
    Verifier("My Provider")
    .add_transport("http", url="http://localhost:8080")
    .add_source("pact/to/pacts/")
)
verifier.verify()

# In the case of a Pact Broker
verifier = (
    Verifier("My Provider")
    .add_transport("http", url="http://localhost:8080")
    .broker_source("https://broker.example.com/")
)
verifier.verify()
```

## State Handling

In general, the consumer will write interactions assuming that the provider is
in a certain state. For example, a consumer requesting information about a user
with ID `123` will have specified `given("user with ID 123 exists")`. It is the
responsibility of the provider to ensure that this state is met before the
interaction is replayed.

In order to change the provider's internal state, Pact relies on a callback
endpoint. The specific manner in which this endpoint is implemented is up to the
provider as it is highly dependent on the provider's architecture.

One common approach is to define the endpoint during testing only, and for the
endpoint to [mock][unittest.mock] the expected calls to the database and/or
external services. This allows the provider to be tested in isolation from the
rest of the system, and assertions can be made about the calls made to the
endpoint.

An alternative approach might be to run a dedicated service which is responsible
for writing to the database such that the provider can retrieve the expected
data. This approach is more complex, but could be useful in cases where test
databases are already in use.
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Callable, Mapping
from contextlib import nullcontext
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypedDict, overload

from yarl import URL

import pact_ffi
from pact._server import MessageProducer, StateCallback
from pact._util import apply_args
from pact.types import (
    UNSET,
    Message,
    MessageProducerArgs,
    StateHandlerArgs,
    StateHandlerUrl,
    Unset,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from typing_extensions import Self

logger = logging.getLogger(__name__)


class _ProviderTransport(TypedDict):
    """
    Provider transport information.

    When the verifier is set up, it needs to communicate with the Provider. This
    is typically done over a single transport method (e.g., HTTP); however, Pact
    _does_ support multiple transport methods.

    This dictionary is used to store information for each transport method and
    is a reflection of Rust's [`ProviderTransport`
    struct](https://github.com/pact-foundation/pact-reference/blob/b55407ef2be897d286af9330506219d17d2a746c/rust/pact_verifier/src/lib.rs#L168).
    """

    transport: str
    """
    The transport method for payloads.

    This is typically one of `http` or `message`. Any other value is used as a
    custom plugin (e.g., `grpc`).
    """
    port: int | None
    """
    The port on which the provider is listening.
    """
    path: str | None
    """
    The path under which the provider is listening.

    This is prefixed to all paths in interactions. For example, if the path is
    `/api`, and the interaction path is `/users`, the request will be made to
    `/api/users`.
    """
    scheme: str | None
    """
    The scheme to use for the provider.

    This is typically only used for the `http` transport method, where this
    value can either be `http` or `https`.
    """


class Verifier:
    """
    A Verifier between a consumer and a provider.

    This class encapsulates the logic for verifying that a provider meets the
    expectations of a consumer. This is done by replaying interactions from the
    consumer against the provider, and ensuring that the provider's responses
    match the expectations set by the consumer.
    """

    def __init__(self, name: str, host: str | None = None) -> None:
        """
        Create a new Verifier.

        Args:
            name:
                The name of the provider to verify. This is used to identify
                which interactions the provider is involved in, and then Pact
                will replay these interactions against the provider.

            host:
                The host on which the Pact verifier is running. This is used to
                communicate with the provider. If not specified, the default
                value is `localhost`.
        """
        self._name = name
        self._host = host or "localhost"
        self._handle = pact_ffi.verifier_new_for_application()
        self._branch: str | None = None

        # In order to provide a fluent interface, we remember some options which
        # are set using the same FFI method. In particular, we remember
        # transport methods defined, and then before verification call the
        # `set_info` and `add_transport` FFI methods as needed.
        self._transports: list[_ProviderTransport] = []
        self._message_producer: (
            MessageProducer[Callable[..., Message]] | nullcontext[None]
        ) = nullcontext()
        self._state_handler: StateCallback[Callable[..., None]] | nullcontext[None] = (
            nullcontext()
        )
        self._disable_ssl_verification = False
        self._request_timeout = 5000
        # Using a broker source requires knowing the provider name, which is
        # only provided to the FFI just before verification. As such, we store
        # the broker source as a hook to be called just before verification, and
        # after the provider name is set.
        self._broker_source_hook: Callable[[], None] | None = None

    def __str__(self) -> str:
        """
        Informal string representation of the Verifier.
        """
        return f"Verifier({self._name})"

    def __repr__(self) -> str:
        """
        Information-rish string representation of the Verifier.
        """
        return f"<Verifier: {self._name}, handle={self._handle}>"

    def add_transport(
        self,
        *,
        url: str | URL | None = None,
        protocol: str | None = None,
        port: int | None = None,
        path: str | None = None,
        scheme: str | None = None,
    ) -> Self:
        """
        Add a provider transport method.

        If the provider supports multiple transport methods, or non-HTTP(S)
        methods, this method allows these additional transport methods to be
        added. It can be called multiple times to add multiple transport
        methods.

        As some transport methods may not use ports, paths or schemes, these
        parameters are optional. Note that while optional, these _may_ still be
        used during testing as Pact uses HTTP(S) to communicate with the
        provider. For example, if you are implementing your own message
        verification, it needs to be exposed over HTTP and the `port` and `path`
        arguments are used for this testing communication.

        Args:
            url:
                A convenient way to set the provider transport. This option
                is mutually exclusive with the other options.

            protocol:
                The protocol to use. This will typically be one of:

                -   `http` for communications over HTTP(S)

                -   `message` for non-plugin message-based communications

                Any other protocol will be treated as a custom protocol and will
                be handled by a plugin.

                If `url` is _not_ specified, this parameter is required.

            port:
                The provider port.

                If the protocol does not use ports, this parameter should be
                `None`. If not specified, the default port for the scheme will
                be used (provided the scheme is known).

            path:
                The provider context path.

                For protocols which do not use paths, this parameter should be
                `None`.

                For protocols which do use paths, this parameter should be
                specified to avoid any ambiguity, though if left unspecified,
                the root path will be used.

                If a non-root path is used, the path given here will be
                prepended to the path in the interaction. For example, if the
                path is `/api`, and the interaction path is `/users`, the
                request will be made to `/api/users`.

            scheme:
                The provider scheme, if applicable to the protocol.

                This is typically only used for the `http` protocol, where this
                value can either be `http` (the default) or `https`.

        Raises:
            ValueError:
                If mutually exclusive parameters are provided, or required
                parameters are missing, or host/protocol mismatches.
        """
        if url and any(x is not None for x in (protocol, port, path, scheme)):
            msg = "The `url` parameter is mutually exclusive with other parameters"
            raise ValueError(msg)

        if url:
            url = URL(url)
            if url.host != self._host:
                msg = f"Host mismatch: {url.host} != {self._host}"
                raise ValueError(msg)
            protocol = url.scheme
            if protocol == "https":
                protocol = "http"
            port = url.port
            path = url.path
            scheme = url.scheme
            return self.add_transport(
                protocol=protocol,
                port=port,
                path=path,
                scheme=scheme,
            )

        if not protocol:
            msg = "A protocol must be specified"
            raise ValueError(msg)

        if port is None and scheme:
            if scheme.lower() == "http":
                port = 80
            elif scheme.lower() == "https":
                port = 443

        logger.debug(
            "Adding transport to verifier",
            extra={
                "protocol": protocol,
                "port": port,
                "path": path,
                "scheme": scheme,
            },
        )
        self._transports.append(
            _ProviderTransport(
                transport=protocol,
                port=port,
                path=path,
                scheme=scheme,
            )
        )

        return self

    def message_handler(
        self,
        handler: Callable[..., Message]
        | dict[str, Callable[..., Message] | Message | bytes],
    ) -> Self:
        """
        Set the message handler.

        This method sets a custom message handler for the verifier. The handler
        can be called to produce a specific message to send to the provider.

        This can be provided in one of two ways:

        1.  A fully fledged function that will be called for all messages. This
            is the most powerful option as it allows for full control over the
            message generation. The function's signature must be compatible with
            the [`MessageProducerArgs`][pact.types.MessageProducerArgs] type.

        2.  A dictionary mapping message names to either (a) producer functions,
            (b) [`Message`][pact.types.Message] dictionaries, or (c) raw
            bytes. If using a producer function, it must be compatible with the
            [`MessageProducerArgs`][pact.types.MessageProducerArgs] type.

        ## Implementation

        There are a large number of ways to send messages, and the specifics of
        the transport methods are not specifically relevant to Pact. As such,
        Pact abstracts the transport layer away and uses a lightweight HTTP
        server to handle messages.

        Pact Python is capable of setting up this server and handling the
        messages internally using user-provided handlers. It is possible to use
        your own HTTP server to handle messages by using the `add_transport`
        method. It is not possible to use both this method and `add_transport`
        to handle messages.

        Args:
            handler:
                The message handler.

                This should be a callable or a dictionary mapping message names
                to callables, Message dicts, or bytes.

        Raises:
            TypeError:
                If the handler or its values are invalid.
        """
        logger.debug(
            "Setting message handler for verifier",
            extra={
                "path": "/_pact/message",
            },
        )

        if callable(handler):

            def _handler(
                name: str,
                metadata: dict[str, Any] | None,
            ) -> Message:
                logger.info("Internal message produced called.")
                return apply_args(
                    handler,
                    MessageProducerArgs(name=name, metadata=metadata),
                )

            self._message_producer = MessageProducer(_handler)
            self.add_transport(
                protocol="message",
                port=self._message_producer.port,
                path=self._message_producer.path,
            )
            return self

        if isinstance(handler, dict):

            def _handler(
                name: str,
                metadata: dict[str, Any] | None,
            ) -> Message:
                logger.info("Internal message produced called.")
                val = handler[name]

                if callable(val):
                    return apply_args(
                        val,
                        MessageProducerArgs(name=name, metadata=metadata),
                    )
                if isinstance(val, bytes):
                    return Message(contents=val, metadata=None, content_type=None)
                if isinstance(val, dict):
                    return Message(
                        contents=val["contents"],
                        metadata=val.get("metadata"),
                        content_type=val.get("content_type"),
                    )

                msg = "Invalid message handler value"
                raise TypeError(msg)

            self._message_producer = MessageProducer(_handler)
            self.add_transport(
                protocol="message",
                port=self._message_producer.port,
                path=self._message_producer.path,
            )

            return self

        msg = "Invalid message handler type"
        raise TypeError(msg)

    def filter(
        self,
        description: str | None = None,
        *,
        state: str | None = None,
        no_state: bool = False,
    ) -> Self:
        """
        Set the filter for the interactions.

        This method can be used to filter interactions based on their
        description and state. Repeated calls to this method will replace the
        previous filter.

        Args:
            description:
                The interaction description.

                This should be a regular expression. If unspecified, no
                filtering will be done based on the description.

            state:
                The interaction state.

                This should be a regular expression. If unspecified, no
                filtering will be done based on the state.

            no_state:
                Whether to include interactions with no state.
        """
        logger.debug(
            "Setting filter for verifier",
            extra={
                "description": description,
                "state": state,
                "no_state": no_state,
            },
        )
        pact_ffi.verifier_set_filter_info(
            self._handle,
            description,
            state,
            filter_no_state=no_state,
        )
        return self

    # Functional argument, either direct or via a dictionary.
    @overload
    def state_handler(
        self,
        handler: Callable[..., None],
        *,
        teardown: bool = False,
        body: None = None,
    ) -> Self: ...
    @overload
    def state_handler(
        self,
        handler: Mapping[str, Callable[..., None]],
        *,
        teardown: bool = False,
        body: None = None,
    ) -> Self: ...
    # Cases where the handler takes a URL. The `body` argument is required in
    # this case.
    @overload
    def state_handler(
        self,
        handler: StateHandlerUrl,
        *,
        teardown: bool = False,
        body: bool,
    ) -> Self: ...

    def state_handler(
        self,
        handler: Callable[..., None]
        | Mapping[str, Callable[..., None]]
        | StateHandlerUrl,
        *,
        teardown: bool = False,
        body: bool | None = None,
    ) -> Self:
        """
        Set the state handler.

        In many interactions, the consumer will assume that the provider is in a
        certain state. For example, a consumer requesting information about a
        user with ID `123` will have specified `given("user with ID 123
        exists")`.

        The state handler is responsible for changing the provider's internal
        state to match the expected state before the interaction is replayed.

        This can be done in one of three ways:

        1.  By providing a single function that will be called for all state
            changes.
        2.  By providing a mapping of state names to functions.
        3.  By providing the URL endpoint to which the request should be made.

        The last option is more complicated as it requires the provider to be
        able to handle the state change requests. The first two options handle
        this internally and are the preferred options if the provider is written
        in Python.

        The function signature must be compatible with the
        [`StateHandlerArgs`][pact.types.StateHandlerArgs]. If the function
        has additional arguments, these must either have default values, or be
        filled by using the [`partial`][functools.partial] function.

        Pact also uses a special state denoted with the empty string `""`. This
        is used as a generic test setup/teardown handler. This key is optional
        in dictionaries, but other implementation should ensure they can handle
        (or safely ignore) this state name.

        Args:
            handler:
                The handler for the state changes. This can be one of the
                following:

                -   A single function that will be called for all state changes.
                -   A dictionary mapping state names to functions.
                -   A URL endpoint to which the request should be made.

                See above for more information on the function signature.

            teardown:
                Whether to teardown the provider state after an interaction is
                validated.

            body:
                Whether to include the state change request in the body (`True`)
                or in the query string (`False`). This must be left as `None` if
                providing one or more handler functions; and it must be set to a
                boolean if providing a URL.

        Raises:
            ValueError:
                If the handler/body combination is invalid.

            TypeError:
                If the handler type is invalid.
        """
        if isinstance(handler, StateHandlerUrl):
            if body is None:
                msg = "The `body` parameter must be a boolean when providing a URL"
                raise ValueError(msg)
            return self._state_handler_url(handler, teardown=teardown, body=body)

        if isinstance(handler, Mapping):
            if body is not None:
                msg = "The `body` parameter must be `None` when providing a dictionary"
                raise ValueError(msg)
            return self._state_handler_dict(handler, teardown=teardown)

        if callable(handler):
            if body is not None:
                msg = "The `body` parameter must be `None` when providing a function"
                raise ValueError(msg)
            return self._state_handler_function(handler, teardown=teardown)

        msg = "Invalid handler type"
        raise TypeError(msg)

    def _state_handler_url(
        self,
        handler: StateHandlerUrl,
        *,
        teardown: bool,
        body: bool,
    ) -> Self:
        """
        Set the state handler to a URL.

        This method is used to set the state handler to a URL endpoint. This
        endpoint will be called to change the provider's state.

        Args:
            handler:
                The URL endpoint to which the request should be made.

            teardown:
                Whether to teardown the provider state after an interaction is
                validated.

            body:
                Whether to include the state change request in the body (`True`)
                or in the query string (`False`).

        Returns:
            The verifier instance.

        Raises:
            ValueError:
                If the body parameter is not a boolean when providing a URL.
        """
        logger.debug(
            "Setting URL state handler for verifier",
            extra={
                "handler": handler,
                "teardown": teardown,
                "body": body,
            },
        )
        pact_ffi.verifier_set_provider_state(
            self._handle,
            str(handler),
            teardown=teardown,
            body=body,
        )
        return self

    def _state_handler_dict(
        self,
        handler: Mapping[str, Callable[..., None]],
        *,
        teardown: bool,
    ) -> Self:
        """
        Set the state handler to a dictionary of functions.

        This method is used to set the state handler to a dictionary of functions.
        Each function is called when the provider's state needs to be changed.

        Args:
            handler:
                The dictionary mapping state names to functions. If `teardown`
                is `True`, the functions must take two arguments: the action and
                the parameters. If `teardown` is `False`, the functions must take
                one argument: the parameters.

                Note that the empty string `""` is used as a special key for a
                generic test setup/teardown handler. If this key is absent,
                these callbacks will be safely ignored.

            teardown:
                Whether to teardown the provider state after an interaction is
                validated.

        Returns:
            The verifier instance.

        Raises:
            TypeError:
                If any value in the dictionary is not callable.
        """
        if any(not callable(f) for f in handler.values()):
            msg = "All values in the dictionary must be callable"
            raise TypeError(msg)

        logger.debug(
            "Setting dictionary state handler for verifier",
            extra={
                "states": list(handler.keys()),
                "teardown": teardown,
            },
        )

        def _handler(
            state: str,
            action: Literal["setup", "teardown"],
            parameters: dict[str, Any] | None,
        ) -> None:
            if state == "" and state not in handler:
                return

            logger.debug(
                "Calling state handler function for state %r",
                state,
                extra={
                    "action": action,
                    "parameters": parameters,
                },
            )

            apply_args(
                handler[state],
                StateHandlerArgs(state=state, action=action, parameters=parameters),
            )

        self._state_handler = StateCallback(_handler)
        pact_ffi.verifier_set_provider_state(
            self._handle,
            self._state_handler.url,
            teardown=teardown,
            body=True,
        )

        return self

    def _state_handler_function(
        self,
        handler: Callable[..., None],
        *,
        teardown: bool,
    ) -> Self:
        """
        Set the state handler to a single function.

        This method is used to set the state handler to a single function. This
        function will be called when the provider's state needs to be changed.

        Args:
            handler:
                The function to call when the provider's state needs to be
                changed. If `teardown` is `True`, the function must take three
                arguments: the state, the action, and the parameters. If
                `teardown` is `False`, the function must take two arguments: the
                state and the parameters.

            teardown:
                Whether to teardown the provider state after an interaction is
                validated.

        Returns:
            The verifier instance.

        Raises:
            TypeError:
                If the handler is not callable.
        """
        logger.debug(
            "Setting function state handler for verifier",
            extra={
                "handler": handler,
                "teardown": teardown,
            },
        )

        def _handler(
            state: str,
            action: Literal["setup", "teardown"],
            parameters: dict[str, Any] | None,
        ) -> None:
            apply_args(
                handler,
                StateHandlerArgs(state=state, action=action, parameters=parameters),
            )

        self._state_handler = StateCallback(_handler)
        pact_ffi.verifier_set_provider_state(
            self._handle,
            self._state_handler.url,
            teardown=teardown,
            body=True,
        )

        return self

    def disable_ssl_verification(self) -> Self:
        """
        Disable SSL verification.
        """
        self._disable_ssl_verification = True
        pact_ffi.verifier_set_verification_options(
            self._handle,
            disable_ssl_verification=self._disable_ssl_verification,
            request_timeout=self._request_timeout,
        )
        return self

    def set_request_timeout(self, timeout: int) -> Self:
        """
        Set the request timeout.

        Args:
            timeout:
                The request timeout in milliseconds.

        Raises:
            ValueError:
                If the timeout is negative.
        """
        if timeout < 0:
            msg = "Request timeout must be a positive integer"
            raise ValueError(msg)

        self._request_timeout = timeout
        pact_ffi.verifier_set_verification_options(
            self._handle,
            disable_ssl_verification=self._disable_ssl_verification,
            request_timeout=self._request_timeout,
        )
        return self

    def set_coloured_output(self, *, enabled: bool = True) -> Self:
        """
        Toggle coloured output.
        """
        pact_ffi.verifier_set_coloured_output(self._handle, enabled=enabled)
        return self

    def set_error_on_empty_pact(self, *, enabled: bool = True) -> Self:
        """
        Toggle error on empty pact.

        If enabled, a Pact file with no interactions will cause the verifier to
        return an error. If disabled, a Pact file with no interactions will be
        ignored.
        """
        pact_ffi.verifier_set_no_pacts_is_error(self._handle, enabled=enabled)
        return self

    def set_publish_options(
        self,
        version: str,
        url: str | None = None,
        branch: str | None = None,
        tags: list[str] | None = None,
    ) -> Self:
        """
        Set options used when publishing results to the Broker.

        Args:
            version:
                The provider version.

            url:
                URL to the build which ran the verification.

            tags:
                Collection of tags for the provider.

            branch:
                Name of the branch used for verification.

                The first time a branch is set here or through
                [`provider_branch`][pact.verifier.BrokerSelectorBuilder.provider_branch],
                the value will be saved and use as a default for both.
        """
        if not self._branch and branch:
            self._branch = branch
        pact_ffi.verifier_set_publish_options(
            self._handle,
            version,
            url,
            tags or [],
            branch or self._branch,
        )
        return self

    def filter_consumers(self, *filters: str) -> Self:
        """
        Filter the consumers.

        Args:
            filters:
                Filters to apply to the consumers.
        """
        pact_ffi.verifier_set_consumer_filters(self._handle, filters)
        return self

    def add_custom_header(self, name: str, value: str) -> Self:
        """
        Add a customer header to the request.

        These headers are added to every request made to the provider.

        Args:
            name:
                The key of the header.

            value:
                The value of the header.
        """
        pact_ffi.verifier_add_custom_header(self._handle, name, value)
        return self

    def add_custom_headers(
        self,
        headers: dict[str, str] | Iterable[tuple[str, str]],
    ) -> Self:
        """
        Add multiple customer headers to the request.

        These headers are added to every request made to the provider.

        Args:
            headers:
                The headers to add.

                The value can be:
                    - a dictionary of header key-value pairs
                    - an iterable of (key, value) tuples
        """
        if isinstance(headers, dict):
            headers = headers.items()
        for name, value in headers:
            self.add_custom_header(name, value)
        return self

    @overload
    def add_source(
        self,
        source: str | URL,
        *,
        username: str | None = None,
        password: str | None = None,
    ) -> Self: ...

    @overload
    def add_source(self, source: str | URL, *, token: str | None = None) -> Self: ...

    @overload
    def add_source(self, source: str | Path) -> Self: ...

    def add_source(
        self,
        source: str | Path | URL,
        *,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
    ) -> Self:
        """
        Adds a source to the verifier.

        This will use one or more Pact files as the source of interactions to
        verify.

        Args:
            source:
                The source of the interactions. This may be either of the following:

                -   A local file path to a Pact file.
                -   A local file path to a directory containing Pact files.
                -   A URL to a Pact file.

                If using a URL, the `username` and `password` parameters can be
                used to provide basic HTTP authentication, or the `token`
                parameter can be used to provide bearer token authentication.
                The `username` and `password` parameters can also be passed as
                part of the URL.

            username:
                The username to use for basic HTTP authentication. This is only
                used when the source is a URL.

            password:
                The password to use for basic HTTP authentication. This is only
                used when the source is a URL.

            token:
                The token to use for bearer token authentication. This is only
                used when the source is a URL. Note that this is mutually
                exclusive with `username` and `password`.

        Raises:
            ValueError:
                If the source scheme is invalid.
        """
        if isinstance(source, Path):
            return self._add_source_local(source)

        if isinstance(source, URL):
            if source.scheme == "file":
                return self._add_source_local(source.path)

            if source.scheme in ("http", "https"):
                return self._add_source_remote(
                    source,
                    username=username,
                    password=password,
                    token=token,
                )

            msg = f"Invalid source scheme: {source.scheme}"
            raise ValueError(msg)

        # Strings are ambiguous, so we need identify them as either local or
        # remote.
        if "://" in source:
            return self._add_source_remote(
                URL(source),
                username=username,
                password=password,
                token=token,
            )
        return self._add_source_local(source)

    def _add_source_local(self, source: str | Path) -> Self:
        """
        Adds a local source to the verifier.

        This will use one or more Pact files as the source of interactions to
        verify.

        Args:
            source:
                The source of the interactions. This may be either of the
                following:

                - A local file path to a Pact file.
                - A local file path to a directory containing Pact files.

        Raises:
            ValueError:
                If the source is not a file or directory.
        """
        source = Path(source)
        if source.is_dir():
            pact_ffi.verifier_add_directory_source(self._handle, str(source))
            return self
        if source.is_file():
            pact_ffi.verifier_add_file_source(self._handle, str(source))
            return self
        msg = f"Invalid source: {source}"
        raise ValueError(msg)

    def _add_source_remote(
        self,
        url: str | URL,
        *,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
    ) -> Self:
        """
        Add a remote source to the verifier.

        This will use a Pact file accessible over HTTP or HTTPS as the source of
        interactions to verify.

        Args:
            url:
                The source of the interactions. This must be a URL to a Pact
                file. The URL may contain a username and password for basic HTTP
                authentication.

            username:
                The username to use for basic HTTP authentication. If the source
                is a URL containing a username, this parameter must be `None`.

            password:
                The password to use for basic HTTP authentication. If the source
                is a URL containing a password, this parameter must be `None`.

            token:
                The token to use for bearer token authentication. This is
                mutually exclusive with `username` and `password` (whether they
                be specified through arguments, or embedded in the URL).

        Raises:
            ValueError:
                If mutually exclusive authentication parameters are provided.
        """
        url = URL(url)

        if url.user and username:
            msg = "Cannot specify both `username` and a username in the URL"
            raise ValueError(msg)
        username = url.user or username

        if url.password and password:
            msg = "Cannot specify both `password` and a password in the URL"
            raise ValueError(msg)
        password = url.password or password

        if token and (username or password):
            msg = "Cannot specify both `token` and `username`/`password`"
            raise ValueError(msg)

        pact_ffi.verifier_url_source(
            self._handle,
            str(url.with_user(None).with_password(None)),
            username,
            password,
            token,
        )
        return self

    @overload
    def broker_source(
        self,
        url: str | URL | Unset = UNSET,
        *,
        username: str | Unset = UNSET,
        password: str | Unset = UNSET,
        selector: Literal[False] = False,
        use_env: bool = True,
    ) -> Self: ...

    @overload
    def broker_source(
        self,
        url: str | URL | None | Unset = UNSET,
        *,
        token: str | None | Unset = UNSET,
        selector: Literal[False] = False,
        use_env: bool = True,
    ) -> Self: ...

    @overload
    def broker_source(
        self,
        url: str | URL | None | Unset = UNSET,
        *,
        username: str | None | Unset = UNSET,
        password: str | None | Unset = UNSET,
        selector: Literal[True],
        use_env: bool = True,
    ) -> BrokerSelectorBuilder: ...

    @overload
    def broker_source(
        self,
        url: str | URL | None | Unset = UNSET,
        *,
        token: str | None | Unset = UNSET,
        selector: Literal[True],
        use_env: bool = True,
    ) -> BrokerSelectorBuilder: ...

    def broker_source(  # noqa: PLR0913
        self,
        url: str | URL | None | Unset = UNSET,
        *,
        username: str | None | Unset = UNSET,
        password: str | None | Unset = UNSET,
        token: str | None | Unset = UNSET,
        selector: bool = False,
        use_env: bool = True,
    ) -> BrokerSelectorBuilder | Self:
        """
        Adds a broker source to the verifier.

        If any of the values are `None`, the value will be read from the
        environment variables unless the `use_env` parameter is set to `False`.
        The known variables are:

        -   `PACT_BROKER_BASE_URL` for the `url` parameter.
        -   `PACT_BROKER_USERNAME` for the `username` parameter.
        -   `PACT_BROKER_PASSWORD` for the `password` parameter.
        -   `PACT_BROKER_TOKEN` for the `token` parameter.

        By default, or if `selector=False`, this function returns the verifier
        instance to allow for method chaining. If `selector=True` is given, this
        function returns a
        [`BrokerSelectorBuilder`][pact.verifier.BrokerSelectorBuilder] instance
        which allows for further configuration of the broker source in a fluent
        interface. The [`build()`][pact.verifier.BrokerSelectorBuilder.build]
        call is then used to finalise the broker source and return the verifier
        instance for further configuration.

        Args:
            url:
                The broker URL. The URL may contain a username and password for
                basic HTTP authentication.

            username:
                The username to use for basic HTTP authentication. If the source
                is a URL containing a username, this parameter must be `None`.

            password:
                The password to use for basic HTTP authentication. If the source
                is a URL containing a password, this parameter must be `None`.

            token:
                The token to use for bearer token authentication. This is
                mutually exclusive with `username` and `password` (whether they
                be specified through arguments, or embedded in the URL).

            selector:
                Whether to return a
                [BrokerSelectorBuilder][pact.verifier.BrokerSelectorBuilder]
                instance. The builder instance allows for further configuration
                of the broker source and must be finalised with a call to
                [`build()`][pact.verifier.BrokerSelectorBuilder.build].

            use_env:
                Whether to read missing values from the environment variables.
                This is `True` by default which allows for easy configuration
                from the standard Pact environment variables. In all cases, the
                explicitly provided values take precedence over the environment
                variables.

        Raises:
            ValueError:
                If mutually exclusive authentication parameters are provided.
        """

        def maybe_var(v: Any | Unset, env: str) -> str | None:  # noqa: ANN401
            if isinstance(v, Unset):
                return os.getenv(env) if use_env else None
            return v

        url = maybe_var(url, "PACT_BROKER_BASE_URL")
        if not url:
            msg = "A broker URL must be provided"
            raise ValueError(msg)
        url = URL(url)

        username = maybe_var(username, "PACT_BROKER_USERNAME")
        if url.user and username:
            msg = "Cannot specify both `username` and a username in the URL"
            raise ValueError(msg)

        password = maybe_var(password, "PACT_BROKER_PASSWORD")
        if url.password and password:
            msg = "Cannot specify both `password` and a password in the URL"
            raise ValueError(msg)

        token = maybe_var(token, "PACT_BROKER_TOKEN")
        if token and (username or password):
            msg = "Cannot specify both `token` and `username`/`password`"
            raise ValueError(msg)

        if selector:
            return BrokerSelectorBuilder(
                self,
                str(url.with_user(None).with_password(None)),
                username,
                password,
                token,
            )

        self._broker_source_hook = lambda: pact_ffi.verifier_broker_source(
            self._handle,
            str(url.with_user(None).with_password(None)),
            username,
            password,
            token,
        )

        return self

    def verify(self) -> Self:
        """
        Verify the interactions.

        Returns:
            Whether the interactions were verified successfully.

        Raises:
            RuntimeError:
                If no transports have been set.
        """
        if not self._transports:
            msg = "No transports have been set"
            raise RuntimeError(msg)

        first, *rest = self._transports

        pact_ffi.verifier_set_provider_info(
            self._handle,
            self._name,
            first["scheme"],
            self._host,
            first["port"],
            first["path"],
        )

        for transport in rest:
            pact_ffi.verifier_add_provider_transport(
                self._handle,
                transport["transport"],
                transport["port"] or 0,
                transport["path"],
                transport["scheme"],
            )

        if self._broker_source_hook:
            self._broker_source_hook()

        with self._message_producer, self._state_handler:
            pact_ffi.verifier_execute(self._handle)
            logger.debug("Verifier executed")

        return self

    @property
    def logs(self) -> str:
        """
        Get the logs.
        """
        return pact_ffi.verifier_logs(self._handle)

    @classmethod
    def logs_for_provider(cls, provider: str) -> str:
        """
        Get the logs for a provider.
        """
        return pact_ffi.verifier_logs_for_provider(provider)

    def output(self, *, strip_ansi: bool = False) -> str:
        """
        Get the output.
        """
        return pact_ffi.verifier_output(self._handle, strip_ansi=strip_ansi)

    @property
    def results(self) -> dict[str, Any]:
        """
        Get the results.
        """
        return json.loads(pact_ffi.verifier_json(self._handle))


class BrokerSelectorBuilder:
    """
    A Broker selector.

    This class encapsulates the logic for selecting Pacts from a Pact broker.
    """

    def __init__(
        self,
        verifier: Verifier,
        url: str,
        username: str | None,
        password: str | None,
        token: str | None,
    ) -> None:
        """
        Instantiate a new Broker Selector.

        This constructor should not be called directly. Instead, use the
        `broker_source` method of the `Verifier` class with `selector=True`.
        """
        self._verifier = verifier
        self._url = url
        self._username = username
        self._password = password
        self._token = token

        # If the instance is dropped without having the `build()` method called,
        # raise a warning.
        self._built = False

        self._include_pending: bool = False
        "Whether to include pending Pacts."

        self._include_wip_since: date | None = None
        "Whether to include work in progress Pacts since a given date."

        self._provider_tags: list[str] | None = None
        "List of provider tags to match."

        self._provider_branch: str | None = None
        "The provider branch."

        self._consumer_versions: list[str] | None = None
        "List of consumer version regex patterns."

        self._consumer_tags: list[str] | None = None
        "List of consumer tags to match."

    def include_pending(self) -> Self:
        """
        Include pending Pacts.
        """
        self._include_pending = True
        return self

    def exclude_pending(self) -> Self:
        """
        Exclude pending Pacts.
        """
        self._include_pending = False
        return self

    def include_wip_since(self, d: str | date) -> Self:
        """
        Include work in progress Pacts since a given date.
        """
        if isinstance(d, str):
            d = date.fromisoformat(d)
        self._include_wip_since = d
        return self

    def exclude_wip(self) -> Self:
        """
        Exclude work in progress Pacts.
        """
        self._include_wip_since = None
        return self

    def provider_tags(self, *tags: str) -> Self:
        """
        Set the provider tags.
        """
        self._provider_tags = list(tags)
        return self

    def provider_branch(self, branch: str) -> Self:
        """
        Set the provider branch.

        The first time a branch is set here or through
        [`set_publish_options`][pact.verifier.Verifier.set_publish_options], the
        value will be saved and use as a default for both.
        """
        self._provider_branch = branch
        if not self._verifier._branch:  # type: ignore  # noqa: PGH003, SLF001
            self._verifier._branch = branch  # type: ignore  # noqa: PGH003, SLF001
        return self

    def consumer_versions(self, *versions: str) -> Self:
        """
        Set the consumer versions.
        """
        self._consumer_versions = list(versions)
        return self

    def consumer_tags(self, *tags: str) -> Self:
        """
        Set the consumer tags.
        """
        self._consumer_tags = list(tags)
        return self

    def build(self) -> Verifier:
        """
        Build the Broker Selector.

        Returns:
            The Verifier instance with the broker source added.
        """
        self._verifier._broker_source_hook = (  # noqa: SLF001
            lambda: pact_ffi.verifier_broker_source_with_selectors(
                self._verifier._handle,  # noqa: SLF001
                self._url,
                self._username,
                self._password,
                self._token,
                self._include_pending,
                self._include_wip_since,
                self._provider_tags or [],
                self._provider_branch or self._verifier._branch,  # noqa: SLF001
                self._consumer_versions or [],
                self._consumer_tags or [],
            )
        )
        self._built = True
        return self._verifier

    def __del__(self) -> None:
        """
        Destructor for the Broker Selector.

        This destructor will raise a warning if the instance is dropped without
        having the [`build()`][pact.verifier.BrokerSelectorBuilder.build]
        method called.
        """
        if not self._built:
            msg = "BrokerSelectorBuilder was dropped before being built."
            raise Warning(msg)
