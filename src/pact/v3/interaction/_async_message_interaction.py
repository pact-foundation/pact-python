"""
Asynchronous message interaction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict

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

    def __init__(self, pact_handle: pact.v3.ffi.PactHandle, description: str) -> None:
        """
        Initialise a new Asynchronous Message Interaction.

        This function should not be called directly. Instead, an
        AsyncMessageInteraction should be created using the
        [`upon_receiving(...)`][pact.v3.Pact.upon_receiving] method of a
        [`Pact`][pact.v3.Pact] instance using the `"Async"` interaction type.

        Args:
            pact_handle:
                The Pact instance this interaction belongs to.

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
        """
        Interaction part.

        Where interactions have multiple parts, this property keeps track
        of which part is currently being set.

        As this is an asynchronous message interaction, this will always
        return a [`REQUEST`][pact.v3.ffi.InteractionPart.REQUEST], as there the
        consumer of the message does not send any responses.
        """
        return pact.v3.ffi.InteractionPart.REQUEST

    def verify(
        self, handler: Callable[[Any, dict[str, Any]], Any]
    ) -> AsyncMessageInteractionResult | None:
        reified_msg = pact.v3.ffi.message_reify(self._handle)  # type: ignore[arg-type] # TODO: Check InteractionHandle vs MessageHandle # noqa: TD003
        if not reified_msg:
            return None
        result = AsyncMessageInteractionResult(**json.loads(reified_msg))
        response = handler(result.contents or {}, result.metadata or {})
        result.response = response
        return result


@dataclass
class AsyncMessageInteractionResult:
    """
    Result of the message verification.
    """

    description: str
    contents: str | None = None
    metadata: Dict[str, str] | None = None
    response: Any | None = None
    generators: Dict[str, Any] | None = None
    matching_rules: Dict[str, Any] | None = None
