"""
Pact between a consumer and a provider.

This module defines the classes that are used to define a Pact between a
consumer and a provider. It defines the interactions between the two parties,
and provides the functionality to verify that the interactions are satisfied.

For the roles of consumer and provider, see the documentation for the
`pact.v3.service` module.
"""

from __future__ import annotations

import pact.v3.ffi
from pact.v3.interaction import Interaction


class AsyncMessageInteraction(Interaction):
    """
    An asynchronous message interaction.

    This class defines an asynchronous message interaction between a consumer
    and a provider. It defines the kind of messages a consumer can accept, and
    the is agnostic of the underlying protocol, be it a message queue, Apache
    Kafka, or some other asynchronous protocol.
    """

    def __init__(self, pact_handle: pact.v3.ffi.PactHandle, description: str) -> None:
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
