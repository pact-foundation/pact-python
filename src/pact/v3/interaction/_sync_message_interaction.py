"""
Synchronous message interaction.
"""

from __future__ import annotations

from typing_extensions import Self

import pact.v3.ffi
from pact.v3.interaction._base import Interaction


class SyncMessageInteraction(Interaction):
    """
    A synchronous message interaction.

    This class defines a synchronous message interaction between a consumer and
    a provider. As with [`HttpInteraction`][pact.v3.pact.HttpInteraction], it
    defines a specific request that the consumer makes to the provider, and the
    response that the provider should return.

    !!! warning

        This class is not yet fully implemented and is not yet usable.
    """

    def __init__(self, pact_handle: pact.v3.ffi.PactHandle, description: str) -> None:
        """
        Initialise a new Synchronous Message Interaction.

        This function should not be called directly. Instead, an
        AsyncMessageInteraction should be created using the
        [`upon_receiving(...)`][pact.v3.Pact.upon_receiving] method of a
        [`Pact`][pact.v3.Pact] instance using the `"Sync"` interaction type.

        Args:
            pact_handle:
                Handle for the Pact.

            description:
                Description of the interaction. This must be unique within the
                Pact.
        """
        super().__init__(description)
        self.__handle = pact.v3.ffi.new_sync_message_interaction(
            pact_handle,
            description,
        )
        self.__interaction_part = pact.v3.ffi.InteractionPart.REQUEST

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
        return self.__interaction_part

    def will_respond_with(self) -> Self:
        """
        Begin the response part of the interaction.

        This method is a convenience method to separate the request and response
        parts of the interaction. This function is analogous to the
        [`will_respond_with()`][pact.v3.pact.HttpInteraction.will_respond_with]
        method of the [`HttpInteraction`][pact.v3.pact.HttpInteraction] class,
        albeit more generic for synchronous message interactions.

        For example, the following two snippets are
        equivalent:

        ```python
        Pact(...).upon_receiving("A sync request", interaction="Sync")
            .with_body("request body", part="Request")
            .with_body("response body", part="Response")
        ```

        ```python
        Pact(...).upon_receiving("A sync request", interaction="Sync")
            .with_body("request body")
            .will_respond_with()
            .with_body("response body")
        ```

        Returns:
            The current instance of the interaction.

        """
        self.__interaction_part = pact.v3.ffi.InteractionPart.RESPONSE
        return self
