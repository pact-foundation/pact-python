"""
Pact between a consumer and a provider.

This module defines the classes that are used to define a Pact between a
consumer and a provider. It defines the interactions between the two parties,
and provides the functionality to verify that the interactions are satisfied.

As Pact is a consumer-driven contract testing tool, the consumer is responsible
for defining the interactions between the two parties. The provider is then
responsible for ensuring that these interactions are satisfied.

## Usage

The main class in this module is the [`Pact`][pact.Pact] class. This class
defines the Pact between the consumer and the provider. It is responsible for
defining the interactions between the two parties.

The general usage of this module is as follows:

```python
from pact import Pact
import aiohttp


pact = Pact("consumer", "provider")

interaction = pact.upon_receiving("a basic request")
interaction.given("user 123 exists")
interaction.with_request("GET", "/user/123")
interaction.will_respond_with(200)
interaction.with_header("Content-Type", "application/json")
interaction.with_body({"id": 123, "name": "Alice"})

with pact.serve() as srv:
    async with aiohttp.ClientSession(srv.url) as session:
        async with session.get("/user/123") as resp:
            assert resp.status == 200
            assert resp.headers["Content-Type"] == "application/json"
            data = await resp.json()
            assert data == {"id": 123, "name": "Alice"}
```

The repeated calls to `interaction` can be chained together to define the
interaction in a more concise manner:

```python
pact = Pact("consumer", "provider")

(
    pact.upon_receiving("a basic request")
    .given("user 123 exists")
    .with_request("GET", "/user/123")
    .will_respond_with(200)
    .with_header("Content-Type", "application/json")
    .with_body({"id": 123, "name": "Alice"})
)
```

Note that the parentheses are required to ensure that the method chaining works
correctly, as this form of method chaining is not typical in Python.
"""

from __future__ import annotations

import json
import logging
import warnings
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Literal,
    overload,
)

from yarl import URL

import pact_ffi
from pact._util import find_free_port
from pact.error import (
    InteractionVerificationError,
    Mismatch,
    MismatchesError,
    PactVerificationError,
)
from pact.interaction._async_message_interaction import AsyncMessageInteraction
from pact.interaction._http_interaction import HttpInteraction
from pact.interaction._sync_message_interaction import SyncMessageInteraction

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from types import TracebackType

    from typing_extensions import Self

    from pact.interaction import Interaction

logger = logging.getLogger(__name__)


class Pact:
    """
    A Pact between a consumer and a provider.

    This class defines a Pact between a consumer and a provider. It is the
    central class in Pact's framework, and is responsible for defining the
    interactions between the two parties.

    One `Pact` instance should be created for each provider that a consumer
    interacts with. The methods on this class are used to define the broader
    attributes of the Pact, such as the consumer and provider names, the Pact
    specification, any plugins that are used, and any metadata that is attached
    to the Pact.

    Each interaction between the consumer and the provider is defined through
    the [`upon_receiving`][pact.pact.Pact.upon_receiving] method, which
    returns a sub-class of [`Interaction`][pact.interaction.Interaction].
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

        Raises:
            ValueError:
                If the consumer or provider name is empty.
        """
        if not consumer:
            msg = "Consumer name cannot be empty."
            raise ValueError(msg)
        if not provider:
            msg = "Provider name cannot be empty."
            raise ValueError(msg)

        self._consumer = consumer
        self._provider = provider
        self._interactions: set[Interaction] = set()
        self._handle: pact_ffi.PactHandle = pact_ffi.new_pact(
            consumer,
            provider,
        )

        # Default to the latest version of the Pact specification, which
        # can be changed later if required.
        self.with_specification("V4")

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

    @property
    def specification(self) -> pact_ffi.PactSpecification:
        """
        Pact specification version.
        """
        return pact_ffi.handle_get_pact_spec_version(self._handle)

    def with_specification(
        self,
        version: str | pact_ffi.PactSpecification,
    ) -> Self:
        """
        Set the Pact specification version.

        The Pact specification version indicates the features which are
        supported by the Pact, and certain default behaviours.

        If this method is not called, then the Pact will use version 4 of the
        specification by default.

        Args:
            version:
                Pact specification version. This can be either a string or a
                [`PactSpecification`][pact_ffi.PactSpecification] instance.

                The version string is case insensitive and has an optional `v`
                prefix.
        """
        if isinstance(version, str):
            version = pact_ffi.PactSpecification.from_str(version)
        pact_ffi.with_specification(self._handle, version)
        return self

    def using_plugin(self, name: str, version: str | None = None) -> Self:
        """
        Add a plugin to be used by the test.

        Plugins extend the functionality of Pact.

        Args:
            name:
                Name of the plugin.

            version:
                Version of the plugin. This is optional and can be `None`.
        """
        pact_ffi.using_plugin(self._handle, name, version)
        return self

    def with_metadata(
        self,
        namespace: str,
        metadata: dict[str, str],
    ) -> Self:
        """
        Set additional metadata for the Pact.

        A common use for this function is to add information about the client
        library (name, version, hash, etc.) to the Pact.

        Args:
            namespace:
                Namespace for the metadata. This is used to group the metadata
                together.

            metadata:
                Key-value pairs of metadata to add to the Pact.
        """
        for k, v in metadata.items():
            pact_ffi.with_pact_metadata(self._handle, namespace, k, v)
        return self

    @overload
    def upon_receiving(
        self,
        description: str,
        interaction: Literal["HTTP"] = ...,
    ) -> HttpInteraction: ...

    @overload
    def upon_receiving(
        self,
        description: str,
        interaction: Literal["Async"],
    ) -> AsyncMessageInteraction: ...

    @overload
    def upon_receiving(
        self,
        description: str,
        interaction: Literal["Sync"],
    ) -> SyncMessageInteraction: ...

    def upon_receiving(
        self,
        description: str,
        interaction: Literal["HTTP", "Sync", "Async"] = "HTTP",
    ) -> HttpInteraction | AsyncMessageInteraction | SyncMessageInteraction:
        """
        Create a new Interaction.

        Args:
            description:
                Description of the interaction. This must be unique
                within the Pact.

            interaction:
                Type of interaction. Defaults to `HTTP`. This must be one of
                `HTTP`, `Async`, or `Sync`.

        Raises:
            ValueError:
                If the interaction type is invalid.
        """
        if interaction == "HTTP":
            return HttpInteraction(self._handle, description)
        if interaction == "Async":
            return AsyncMessageInteraction(self._handle, description)
        if interaction == "Sync":
            return SyncMessageInteraction(self._handle, description)

        msg = f"Invalid interaction type: {interaction}"
        raise ValueError(msg)

    def serve(  # noqa: PLR0913
        self,
        addr: str = "localhost",
        port: int = 0,
        transport: str = "http",
        transport_config: str | None = None,
        *,
        raises: bool = True,
        verbose: bool = True,
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

            raises:
                Whether to raise an exception if there are mismatches between
                the Pact and the server. If set to `False`, then the mismatches
                must be handled manually.

            verbose:
                Whether or not to print the mismatches to the logger. This works
                independently of `raises`.

        Returns:
            PactServer instance.
        """
        return PactServer(
            self._handle,
            addr,
            port,
            transport,
            transport_config,
            raises=raises,
            verbose=verbose,
        )

    @overload
    def interactions(
        self,
        kind: Literal["HTTP"],
    ) -> Generator[pact_ffi.SynchronousHttp, None, None]: ...

    @overload
    def interactions(
        self,
        kind: Literal["Sync"],
    ) -> Generator[pact_ffi.SynchronousMessage, None, None]: ...

    @overload
    def interactions(
        self,
        kind: Literal["Async"],
    ) -> Generator[pact_ffi.AsynchronousMessage, None, None]: ...

    def interactions(
        self,
        kind: Literal["HTTP", "Sync", "Async"] = "HTTP",
    ) -> (
        Generator[pact_ffi.SynchronousHttp, None, None]
        | Generator[pact_ffi.SynchronousMessage, None, None]
        | Generator[pact_ffi.AsynchronousMessage, None, None]
    ):
        """
        Return an iterator over the Pact's interactions.

        The kind is used to specify the type of interactions that will be
        iterated over.

        Raises:
            ValueError:
                If the kind is unknown.
        """
        # TODO: Add an iterator for `All` interactions.
        # https://github.com/pact-foundation/pact-python/issues/451
        if kind == "HTTP":
            yield from pact_ffi.pact_handle_get_sync_http_iter(self._handle)
        elif kind == "Sync":
            yield from pact_ffi.pact_handle_get_sync_message_iter(self._handle)
        elif kind == "Async":
            yield from pact_ffi.pact_handle_get_async_message_iter(self._handle)
        else:
            msg = f"Unknown interaction type: {kind}"
            raise ValueError(msg)
        return  # Ensures that the parent object outlives the generator

    @overload
    def verify(
        self,
        handler: Callable[[str | bytes | None, dict[str, object]], None],
        kind: Literal["Async", "Sync"],
        *,
        raises: Literal[True] = True,
    ) -> None: ...
    @overload
    def verify(
        self,
        handler: Callable[[str | bytes | None, dict[str, object]], None],
        kind: Literal["Async", "Sync"],
        *,
        raises: Literal[False],
    ) -> list[InteractionVerificationError]: ...

    def verify(
        self,
        handler: Callable[[str | bytes | None, dict[str, object]], None],
        kind: Literal["Async", "Sync"],
        *,
        raises: bool = True,
    ) -> list[InteractionVerificationError] | None:
        """
        Verify message interactions.

        This function is used to ensure that the consumer is able to handle the
        messages that are defined in the Pact. The `handler` function is called
        for each message in the Pact.

        The end-user is responsible for defining the `handler` function and
        verifying that the messages are handled correctly. For example, if the
        handler is meant to call an API, then the API call should be mocked out
        and once the verification is complete, the mock should be verified. Any
        exceptions raised by the handler will be caught and reported as
        mismatches.

        Args:
            handler:
                The function that will be called for each message in the Pact.

                The first argument to the function is the message body, either as
                a string or byte array.

                The second argument is the metadata for the message. If there
                is no metadata, then this will be an empty dictionary.

            kind:
                The type of message interaction. This must be one of `Async`
                or `Sync`.

            raises:
                Whether or not to raise an exception if the handler fails to
                process a message. If set to `False`, then the function will
                return a list of errors.

        Returns:
            `None` if raises is True and no errors occurred, otherwise a list of
            [`InteractionVerificationError`][pact.error.InteractionVerificationError].

        Raises:
            TypeError:
                If the message type is unknown.

            PactVerificationError:
                If raises is True and there are errors.
        """
        errors: list[InteractionVerificationError] = []
        for message in self.interactions(kind):
            request: pact_ffi.MessageContents | None = None
            if isinstance(message, pact_ffi.SynchronousMessage):
                request = message.request_contents
            elif isinstance(message, pact_ffi.AsynchronousMessage):
                request = message.contents
            else:
                msg = f"Unknown message type: {type(message).__name__}"
                raise TypeError(msg)

            if request is None:
                warnings.warn(
                    f"Message '{message.description}' has no contents",
                    stacklevel=2,
                )
                continue

            body = request.contents
            metadata: dict[str, object] = {}
            for pair in request.metadata:
                try:
                    v = json.loads(pair.value)
                except json.JSONDecodeError:
                    v = pair.value
                metadata[pair.key] = v

            try:
                handler(body, metadata)
            except Exception as e:  # noqa: BLE001
                errors.append(InteractionVerificationError(message.description, e))

        if raises:
            if errors:
                raise PactVerificationError(errors)
            return None
        return errors

    def write_file(
        self,
        directory: Path | str | None = None,
        *,
        overwrite: bool = False,
    ) -> None:
        """
        Write out the pact to a file.

        This function should be called once all of the consumer tests have been
        run. It writes the Pact to a file, which can then be used to validate
        the provider.

        Args:
            directory:
                The directory to write the pact to. If the directory does not
                exist, it will be created. The filename will be
                automatically generated from the underlying Pact.

            overwrite:
                If set to True, the file will be overwritten if it already
                exists. Otherwise, the contents of the file will be merged with
                the existing file.
        """
        if directory is None:
            directory = Path.cwd()
        pact_ffi.pact_handle_write_file(
            self._handle,
            directory,
            overwrite=overwrite,
        )


class PactServer:
    """
    Pact Server.

    This class handles the lifecycle of the Pact mock server. It is responsible
    for starting the mock server when the Pact is entered into a [`with`
    block](https://docs.python.org/3/reference/compound_stmts.html#with), and
    stopping the mock server when the block is exited.

    Note that the server should not be started directly, but rather through the
    [`serve`][pact.Pact.serve] method of a [`Pact`][pact.Pact]:

    ```python
    pact = Pact("consumer", "provider")
    # Define interactions...
    with pact.serve() as srv:
        ...
    ```

    The URL for the server can be accessed through its
    [`url`][pact.pact.PactServer.url] attribute, which will be required in
    order to point the consumer client to the mock server:

    ```python
    pact = Pact("consumer", "provider")
    with pact.serve() as srv:
        api_client = MyApiClient(srv.url)
        # Test the client...
    ```

    If the server is instantiated with `raises=True` (the default), then the
    server will raise a `MismatchesError` if there are mismatches in any of the
    interactions. If `raises=False`, then the mismatches must be handled
    manually.
    """

    def __init__(  # noqa: PLR0913
        self,
        pact_handle: pact_ffi.PactHandle,
        host: str = "localhost",
        port: int | None = None,
        transport: str = "HTTP",
        transport_config: str | None = None,
        *,
        raises: bool = True,
        verbose: bool = True,
    ) -> None:
        """
        Initialise a new Pact Server.

        Args:
            pact_handle:
                Handle for the Pact.

            host:
                Hostname or IP for the mock server.

            port:
                Port to bind the mock server to. The value of `None` will select
                a random available port.

            transport:
                Transport to use for the mock server.

            transport_config:
                Configuration for the transport. This is specific to the
                transport being used and should be a JSON string.

            raises:
                Whether or not to raise an exception if the server is not
                matched upon exit.

            verbose:
                Whether or not to print the mismatches to the logger. This works
                independently of `raises`.
        """
        self._host = host
        self._port = port or find_free_port()
        self._transport = transport
        self._transport_config = transport_config
        self._pact_handle = pact_handle
        self._handle: None | pact_ffi.PactServerHandle = None
        self._raises = raises
        self._verbose = verbose
        self._mismatches: list[Mismatch] | None = None

    @property
    def port(self) -> int | None:
        """
        Port on which the server is running.

        If the server is not running, then this will be `None`.
        """
        # Unlike the other properties, this value might be different to what was
        # passed in to the constructor as the server can be started on a random
        # port.
        return self._handle.port if self._handle else None

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

    @property
    def matched(self) -> bool:
        """
        Whether or not the server has been matched.

        This is `True` if the server has been matched, and `False` otherwise.

        Raises:
            RuntimeError:
                If the server is not running.
        """
        if not self._handle:
            msg = "The server is not running."
            raise RuntimeError(msg)
        return pact_ffi.mock_server_matched(self._handle)

    @property
    def mismatches(self) -> list[Mismatch]:
        """
        Mismatches between the Pact and the server.

        This is a string containing the mismatches between the Pact and the
        server. If there are no mismatches, then this is an empty string.

        Raises:
            RuntimeError:
                If the server is not running.
        """
        if self._mismatches is not None:
            return self._mismatches

        if not self._handle:
            msg = "The server is not running."
            raise RuntimeError(msg)
        return list(
            map(
                Mismatch.from_dict,
                pact_ffi.mock_server_mismatches(self._handle),
            )
        )

    @property
    def logs(self) -> str | None:
        """
        Logs from the server.

        This is a string containing the logs from the server. If there are no
        logs, then this is `None`. For this to be populated, the logging must
        be configured to make use of the internal buffer.

        Raises:
            RuntimeError:
                If the server is not running.
        """
        if not self._handle:
            msg = "The server is not running."
            raise RuntimeError(msg)

        try:
            return pact_ffi.mock_server_logs(self._handle)
        except RuntimeError:
            return None

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
        self._handle = pact_ffi.create_mock_server_for_transport(
            self._pact_handle,
            self._host,
            self._port,
            self._transport,
            self._transport_config,
        )

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Stop the server.

        Raises:
            MismatchesError:
                If the server has not been fully matched and the server is
                configured to raise an exception.
        """
        if self._handle and not self.matched:
            if self._verbose:
                msg = "\n".join([
                    "Mismatches:",
                    *(f"  ({i + 1}) {m}" for i, m in enumerate(self.mismatches)),
                ])
                logger.error(msg)
            if self._raises:
                raise MismatchesError(*self.mismatches)
            self._mismatches = self.mismatches
            self._handle = None

    def __truediv__(self, other: str | object) -> URL:
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

        Raises:
            RuntimeError:
                If the server is not running.

            ValueError:
                If the path specified is not a directory.
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

        pact_ffi.write_pact_file(
            self._handle,
            str(directory),
            overwrite=overwrite,
        )
