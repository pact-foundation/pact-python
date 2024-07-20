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
from pact.v3 import Verifier


# In the case of local Pact files
verifier = Verifier().set_info("My Provider", url="http://localhost:8080")
verifier.add_source("pact/to/pacts/")
verifier.verify()

# In the case of a Pact Broker
verifier = Verifier().set_info("My Provider", url="http://localhost:8080")
verifier.broker_source("https://broker.example.com/")
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
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, overload

from typing_extensions import Self
from yarl import URL

import pact.v3.ffi

if TYPE_CHECKING:
    from collections.abc import Iterable


class Verifier:
    """
    A Verifier between a consumer and a provider.

    This class encapsulates the logic for verifying that a provider meets the
    expectations of a consumer. This is done by replaying interactions from the
    consumer against the provider, and ensuring that the provider's responses
    match the expectations set by the consumer.
    """

    def __init__(self) -> None:
        """
        Create a new Verifier.
        """
        self._handle: pact.v3.ffi.VerifierHandle = (
            pact.v3.ffi.verifier_new_for_application()
        )

        # In order to provide a fluent interface, we remember some options which
        # are set using the same FFI method.
        self._disable_ssl_verification = False
        self._request_timeout = 5000

    def __str__(self) -> str:
        """
        Informal string representation of the Verifier.
        """
        return "Verifier"

    def __repr__(self) -> str:
        """
        Information-rish string representation of the Verifier.
        """
        return f"<Verifier: {self._handle}>"

    def set_info(  # noqa: PLR0913
        self,
        name: str,
        *,
        url: str | URL | None = None,
        scheme: str | None = None,
        host: str | None = None,
        port: int | None = None,
        path: str | None = None,
    ) -> Self:
        """
        Set the provider information.

        This sets up information about the provider as well as the way it
        communicates with the consumer. Note that for historical reasons, a
        HTTP(S) transport method is always added.

        For a provider which uses other protocols (such as message queues), the
        [`add_transport`][pact.v3.verifier.Verifier.add_transport] must be used.
        This method can be called multiple times to add multiple transport
        methods.

        Args:
            name:
                A user-friendly name for the provider.

            url:
                The URL on which requests are made to the provider by Pact.

                It is recommended to use this parameter to set the provider URL.
                If the port is not explicitly set, the default port for the
                scheme will be used.

                This parameter is mutually exclusive with the individual
                parameters.

            scheme:
                The provider scheme. This must be one of `http` or `https`.

            host:
                The provider hostname or IP address. If the provider is running
                on the same machine as the verifier, `localhost` can be used.

            port:
                The provider port. If not specified, the default port for the
                schema will be used.

            path:
                The provider context path. If not specified, the root path will
                be used.

                If a non-root path is used, the path given here will be
                prepended to the path in the interaction. For example, if the
                path is `/api`, and the interaction path is `/users`, the
                request will be made to `/api/users`.
        """
        if url is not None:
            if any(param is not None for param in (scheme, host, port, path)):
                msg = "Cannot specify both `url` and individual parameters"
                raise ValueError(msg)

            url = URL(url)
            scheme = url.scheme
            host = url.host
            port = url.explicit_port
            path = url.path

            if port is None:
                msg = "Unable to determine default port for scheme {scheme}"
                raise ValueError(msg)

            pact.v3.ffi.verifier_set_provider_info(
                self._handle,
                name,
                scheme,
                host,
                port,
                path,
            )
            return self

        url = URL.build(
            scheme=scheme or "http",
            host=host or "localhost",
            port=port,
            path=path or "",
        )
        return self.set_info(name, url=url)

    def add_transport(
        self,
        *,
        protocol: str,
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
        parameters are optional.

        Args:
            protocol:
                The protocol to use. This will typically be one of:

                -   `http` for communications over HTTP(S). Note that when
                    setting up the provider information in
                    [`set_info`][pact.v3.verifier.Verifier.set_info], a HTTP
                    transport method is always added and it is unlikely that an
                    additional HTTP transport method will be needed unless the
                    provider is running on additional ports.

                -   `message` for non-plugin synchronous message-based
                    communications.

                Any other protocol will be treated as a custom protocol and will
                be handled by a plugin.

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
        """
        if port is None and scheme:
            if scheme.lower() == "http":
                port = 80
            elif scheme.lower() == "https":
                port = 443

        pact.v3.ffi.verifier_add_provider_transport(
            self._handle,
            protocol,
            port or 0,
            path,
            scheme,
        )
        return self

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
                The interaction description. This should be a regular
                expression. If unspecified, no filtering will be done based on
                the description.

            state:
                The interaction state. This should be a regular expression. If
                unspecified, no filtering will be done based on the state.

            no_state:
                Whether to include interactions with no state.
        """
        pact.v3.ffi.verifier_set_filter_info(
            self._handle,
            description,
            state,
            filter_no_state=no_state,
        )
        return self

    def set_state(
        self,
        url: str | URL,
        *,
        teardown: bool = False,
        body: bool = False,
    ) -> Self:
        """
        Set the provider state URL.

        The URL is used when the provider's internal state needs to be changed.
        For example, a consumer might have an interaction that requires a
        specific user to be present in the database. The provider state URL is
        used to change the provider's internal state to include the required
        user.

        Args:
            url:
                The URL to which a `GET` request will be made to change the
                provider's internal state.

            teardown:
                Whether to teardown the provider state after an interaction is
                validated.

            body:
                Whether to include the state change request in the body (`True`)
                or in the query string (`False`).
        """
        pact.v3.ffi.verifier_set_provider_state(
            self._handle,
            url if isinstance(url, str) else str(url),
            teardown=teardown,
            body=body,
        )
        return self

    def disable_ssl_verification(self) -> Self:
        """
        Disable SSL verification.
        """
        self._disable_ssl_verification = True
        pact.v3.ffi.verifier_set_verification_options(
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
        """
        if timeout < 0:
            msg = "Request timeout must be a positive integer"
            raise ValueError(msg)

        self._request_timeout = timeout
        pact.v3.ffi.verifier_set_verification_options(
            self._handle,
            disable_ssl_verification=self._disable_ssl_verification,
            request_timeout=self._request_timeout,
        )
        return self

    def set_coloured_output(self, *, enabled: bool = True) -> Self:
        """
        Toggle coloured output.
        """
        pact.v3.ffi.verifier_set_coloured_output(self._handle, enabled=enabled)
        return self

    def set_error_on_empty_pact(self, *, enabled: bool = True) -> Self:
        """
        Toggle error on empty pact.

        If enabled, a Pact file with no interactions will cause the verifier to
        return an error. If disabled, a Pact file with no interactions will be
        ignored.
        """
        pact.v3.ffi.verifier_set_no_pacts_is_error(self._handle, enabled=enabled)
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
        """
        pact.v3.ffi.verifier_set_publish_options(
            self._handle,
            version,
            url,
            tags or [],
            branch,
        )
        return self

    def filter_consumers(self, *filters: str) -> Self:
        """
        Filter the consumers.

        Args:
            filters:
                Filters to apply to the consumers.
        """
        pact.v3.ffi.verifier_set_consumer_filters(self._handle, filters)
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
        pact.v3.ffi.verifier_add_custom_header(self._handle, name, value)
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
                The headers to add. This can be a dictionary or an iterable of
                key-value pairs. The iterable is preferred as it ensures that
                repeated headers are not lost.
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
                The source of the interactions. This may be either of the
                following:

                - A local file path to a Pact file.
                - A local file path to a directory containing Pact files.
                - A URL to a Pact file.

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
        """
        source = Path(source)
        if source.is_dir():
            pact.v3.ffi.verifier_add_directory_source(self._handle, str(source))
            return self
        if source.is_file():
            pact.v3.ffi.verifier_add_file_source(self._handle, str(source))
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

        pact.v3.ffi.verifier_url_source(
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
        url: str | URL,
        *,
        username: str | None = None,
        password: str | None = None,
        selector: Literal[False] = False,
    ) -> Self: ...

    @overload
    def broker_source(
        self,
        url: str | URL,
        *,
        token: str | None = None,
        selector: Literal[False] = False,
    ) -> Self: ...

    @overload
    def broker_source(
        self,
        url: str | URL,
        *,
        username: str | None = None,
        password: str | None = None,
        selector: Literal[True],
    ) -> BrokerSelectorBuilder: ...

    @overload
    def broker_source(
        self,
        url: str | URL,
        *,
        token: str | None = None,
        selector: Literal[True],
    ) -> BrokerSelectorBuilder: ...

    def broker_source(
        self,
        url: str | URL,
        *,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        selector: bool = False,
    ) -> BrokerSelectorBuilder | Self:
        """
        Adds a broker source to the verifier.

        Args:
            url:
                The broker URL. TThe URL may contain a username and password for
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
                Whether to return a BrokerSelectorBuilder instance.
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

        if selector:
            return BrokerSelectorBuilder(
                self,
                str(url.with_user(None).with_password(None)),
                username,
                password,
                token,
            )
        pact.v3.ffi.verifier_broker_source(
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
        """
        pact.v3.ffi.verifier_execute(self._handle)
        return self

    @property
    def logs(self) -> str:
        """
        Get the logs.
        """
        return pact.v3.ffi.verifier_logs(self._handle)

    @classmethod
    def logs_for_provider(cls, provider: str) -> str:
        """
        Get the logs for a provider.
        """
        return pact.v3.ffi.verifier_logs_for_provider(provider)

    def output(self, *, strip_ansi: bool = False) -> str:
        """
        Get the output.
        """
        return pact.v3.ffi.verifier_output(self._handle, strip_ansi=strip_ansi)

    @property
    def results(self) -> dict[str, Any]:
        """
        Get the results.
        """
        return json.loads(pact.v3.ffi.verifier_json(self._handle))


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
        """
        self._provider_branch = branch
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
        pact.v3.ffi.verifier_broker_source_with_selectors(
            self._verifier._handle,  # noqa: SLF001
            self._url,
            self._username,
            self._password,
            self._token,
            self._include_pending,
            self._include_wip_since,
            self._provider_tags or [],
            self._provider_branch,
            self._consumer_versions or [],
            self._consumer_tags or [],
        )
        self._built = True
        return self._verifier

    def __del__(self) -> None:
        """
        Destructor for the Broker Selector.

        This destructor will raise a warning if the instance is dropped without
        having the [`build()`][pact.v3.verifier.BrokerSelectorBuilder.build]
        method called.
        """
        if not self._built:
            msg = "BrokerSelectorBuilder was dropped before being built."
            raise Warning(msg)
