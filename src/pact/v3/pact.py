"""
Pact between a consumer and a provider.

This module defines the classes that are used to define a Pact between a
consumer and a provider. It defines the interactions between the two parties,
and provides the functionality to verify that the interactions are satisfied.

For the roles of consumer and provider, see the documentation for the
`pact.v3.service` module.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Set, overload

from yarl import URL

import pact.v3.ffi
from pact.v3.interaction.async_message_interaction import AsyncMessageInteraction
from pact.v3.interaction.http_interaction import HttpInteraction
from pact.v3.interaction.sync_message_interaction import SyncMessageInteraction

if TYPE_CHECKING:
    from types import TracebackType

    from pact.v3.interaction import Interaction

    try:
        from typing import Self
    except ImportError:
        from typing_extensions import Self


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

    @property
    def specification(self) -> pact.v3.ffi.PactSpecification:
        """
        Pact specification version.
        """
        return pact.v3.ffi.handle_get_pact_spec_version(self._handle)

    def with_specification(
        self,
        version: str | pact.v3.ffi.PactSpecification,
    ) -> Self:
        """
        Set the Pact specification version.

        The Pact specification version indicates the features which are
        supported by the Pact, and certain default behaviours.

        Args:
            version:
                Pact specification version. The can be either a string or a
                [`PactSpecification`][pact.v3.ffi.PactSpecification] instance.

                The version string is case insensitive and has an optional `v`
                prefix.
        """
        if isinstance(version, str):
            version = pact.v3.ffi.PactSpecification.from_str(version)
        pact.v3.ffi.with_specification(self._handle, version)
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
        pact.v3.ffi.using_plugin(self._handle, name, version)
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
            pact.v3.ffi.with_pact_metadata(self._handle, namespace, k, v)
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

        This is an alias for [`interaction(...)`][pact.v3.Pact.interaction].

        Args:
            description:
                Description of the interaction. This must be unique
                within the Pact.

            interaction:
                Type of interaction. Defaults to `HTTP`. This must be one of
                `HTTP`, `Async`, or `Sync`.
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

            raises: Whether to raise an exception if there are mismatches
                between the Pact and the server. If set to `False`, then the
                mismatches must be handled manually.

        Returns:
            A [`PactServer`][pact.v3.pact.PactServer] instance.
        """
        return PactServer(
            self._handle,
            addr,
            port,
            transport,
            transport_config,
            raises=raises,
        )

    def messages(self) -> pact.v3.ffi.PactMessageIterator:
        """
        Iterate over the messages in the Pact.

        This function returns an iterator over the messages in the Pact. This
        is useful for validating the Pact against the provider.

        ```python
        pact = Pact("consumer", "provider")
        with pact.serve() as srv:
            for message in pact.messages():
                # Validate the message against the provider.
                ...
        ```

        Note that the Pact must be written to a file before the messages can be
        iterated over. This is because the messages are not stored in memory,
        but rather are streamed directly from the file.
        """
        return pact.v3.ffi.pact_handle_get_message_iter(self._handle)

    @overload
    def interactions(
        self,
        kind: Literal["HTTP"],
    ) -> pact.v3.ffi.PactSyncHttpIterator: ...

    @overload
    def interactions(
        self,
        kind: Literal["Sync"],
    ) -> pact.v3.ffi.PactSyncMessageIterator: ...

    @overload
    def interactions(
        self,
        kind: Literal["Async"],
    ) -> pact.v3.ffi.PactMessageIterator: ...

    def interactions(
        self,
        kind: str = "HTTP",
    ) -> (
        pact.v3.ffi.PactSyncHttpIterator
        | pact.v3.ffi.PactSyncMessageIterator
        | pact.v3.ffi.PactMessageIterator
    ):
        """
        Return an iterator over the Pact's interactions.

        The kind is used to specify the type of interactions that will be
        iterated over.
        """
        # TODO: Add an iterator for `All` interactions.
        # https://github.com/pact-foundation/pact-python/issues/451
        if kind == "HTTP":
            return pact.v3.ffi.pact_handle_get_sync_http_iter(self._handle)
        if kind == "Sync":
            return pact.v3.ffi.pact_handle_get_sync_message_iter(self._handle)
        if kind == "Async":
            return pact.v3.ffi.pact_handle_get_message_iter(self._handle)
        msg = f"Unknown interaction type: {kind}"
        raise ValueError(msg)

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
        pact.v3.ffi.pact_handle_write_file(
            self._handle,
            directory,
            overwrite=overwrite,
        )


class MismatchesError(Exception):
    """
    Exception raised when there are mismatches between the Pact and the server.
    """

    def __init__(self, mismatches: list[dict[str, Any]]) -> None:
        """
        Initialise a new MismatchesError.

        Args:
            mismatches:
                Mismatches between the Pact and the server.
        """
        super().__init__(f"Mismatched interaction (count: {len(mismatches)})")
        self._mismatches = mismatches

    @property
    def mismatches(self) -> list[dict[str, Any]]:
        """
        Mismatches between the Pact and the server.
        """
        return self._mismatches


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
        *,
        raises: bool = True,
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

            raises: Whether or not to raise an exception if the server
                is not matched upon exit.
        """
        self._host = host
        self._port = port
        self._transport = transport
        self._transport_config = transport_config
        self._pact_handle = pact_handle
        self._handle: None | pact.v3.ffi.PactServerHandle = None
        self._raises = raises

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

    @property
    def matched(self) -> bool:
        """
        Whether or not the server has been matched.

        This is `True` if the server has been matched, and `False` otherwise.
        """
        if not self._handle:
            msg = "The server is not running."
            raise RuntimeError(msg)
        return pact.v3.ffi.mock_server_matched(self._handle)

    @property
    def mismatches(self) -> list[dict[str, Any]]:
        """
        Mismatches between the Pact and the server.

        This is a string containing the mismatches between the Pact and the
        server. If there are no mismatches, then this is an empty string.
        """
        if not self._handle:
            msg = "The server is not running."
            raise RuntimeError(msg)
        return pact.v3.ffi.mock_server_mismatches(self._handle)

    @property
    def logs(self) -> str | None:
        """
        Logs from the server.

        This is a string containing the logs from the server. If there are no
        logs, then this is `None`. For this to be populated, the logging must
        be configured to make use of the internal buffer.
        """
        if not self._handle:
            msg = "The server is not running."
            raise RuntimeError(msg)

        try:
            return pact.v3.ffi.mock_server_logs(self._handle)
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

        Raises:
            MismatchesError:
                If the server has not been fully matched and the server is
                configured to raise an exception.
        """
        if self._handle:
            if self._raises and not self.matched:
                raise MismatchesError(self.mismatches)
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
