"""
Asynchronous message interaction.
"""

from __future__ import annotations
from typing import Callable
import json

import pact.v3.ffi
from pact.v3.interaction._base import Interaction


class AsyncMessageInteraction(Interaction):
    """
    An asynchronous message interaction.

    This class defines an asynchronous message interaction between a consumer
    and a provider. It defines the kind of messages a consumer can accept, and
    the is agnostic of the underlying protocol, be it a message queue, Apache
    Kafka, or some other asynchronous protocol.

    !!! warning

        This class is not yet fully implemented and is not yet usable.
    """

    def __init__(
        self,
        pact_handle: pact.v3.ffi.PactHandle,
        description: str
    ) -> None:
        """
        Initialise a new Asynchronous Message Interaction.

        This function should not be called directly. Instead, an
        AsyncMessageInteraction should be created using the
        [`upon_receiving(...)`][pact.v3.Pact.upon_receiving] method of a
        [`Pact`][pact.v3.Pact] instance using the `"Async"` interaction type.

        Args:
            pact_handle:
                Handle for the Pact.

            description:
                Description of the interaction. This must be unique within the
                Pact.
        """
        super().__init__(description)
        self.__handle = pact.v3.ffi.new_message_interaction(pact_handle, description)

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
        return pact.v3.ffi.InteractionPart.REQUEST

    def with_content(self, content: dict[str, Any], content_type='application/json') -> Self:
        """
        Set the content of the message.

        Args:
            content:
                The content of the message, as a dictionary.

        Returns:
            The current instance of the interaction.
        """
        pact.v3.ffi.message_with_contents(
            self._handle,
            content_type,
            json.dumps(content),
            0
        )
        return self

    def with_metadata(self, metadata: dict[str, Any]) -> Self:
        """
        Set the metadata of the message.

        Args:
            metadata:
                The metadata of the message, as a dictionary.

        Returns:
            The current instance of the interaction.
        """
        [
            pact.v3.ffi.message_with_metadata_v2(self._handle, k, v)
            for k, v in metadata.items()
        ]
        return self

