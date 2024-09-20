"""
Implementations of generators for the V3 and V4 specifications.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import chain
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pact.v3.types import GeneratorType


class Generator(ABC):
    """
    Abstract generator.

    In Pact, a generator is used by Pact to generate data on-the-fly during the
    contract verification process. Generators are used in combination with
    matchers to provide more flexible matching of data.

    This class is abstract and should not be used directly. Instead, use one of
    the concrete generator classes. Alternatively, you can create your own
    generator by subclassing this class

    The matcher provides methods to convert into an integration JSON object and
    a matching rule. These methods are used internally by the Pact library when
    communicating with the FFI and generating the Pact file.
    """

    @abstractmethod
    def to_integration_json(self) -> dict[str, Any]:
        """
        Convert the matcher to an integration JSON object.

        This method is used internally to convert the matcher to a JSON object
        which can be embedded directly in a number of places in the Pact FFI.

        For more information about this format, see the docs:

        > https://docs.pact.io/implementation_guides/rust/pact_ffi/integrationjson

        Returns:
            The matcher as an integration JSON object.
        """

    @abstractmethod
    def to_generator_json(self) -> dict[str, Any]:
        """
        Convert the generator to a generator JSON object.

        This method is used internally to convert the generator to a JSON object
        which can be embedded directly in a number of places in the Pact FFI.

        For more information about this format, see the docs:

        > https://github.com/pact-foundation/pact-specification/tree/version-4

        and

        > https://github.com/pact-foundation/pact-specification/tree/version-2?tab=readme-ov-file#matchers

        Returns:
            The generator as a generator JSON object.
        """


class GenericGenerator(Generator):
    """
    Generic generator.

    A generic generator, with the ability to specify the generator type and
    additional configuration elements.
    """

    def __init__(
        self,
        type: GeneratorType,  # noqa: A002
        /,
        extra_fields: Mapping[str, Any] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """
        Instantiate the generator class.

        Args:
            type:
                The type of the generator.

            extra_fields:
                Additional configuration elements to pass to the generator.
                These fields will be used when converting the generator to both an
                integration JSON object and a generator JSON object.

            **kwargs:
                Alternative way to pass additional configuration elements to the
                generator. See the `extra_fields` argument for more information.
        """
        self.type = type
        """
        The type of the generator.
        """

        self._extra_fields = dict(chain((extra_fields or {}).items(), kwargs.items()))

    def to_integration_json(self) -> dict[str, Any]:
        """
        Convert the matcher to an integration JSON object.

        This method is used internally to convert the matcher to a JSON object
        which can be embedded directly in a number of places in the Pact FFI.

        For more information about this format, see the docs:

        > https://docs.pact.io/implementation_guides/rust/pact_ffi/integrationjson

        Returns:
            The matcher as an integration JSON object.
        """
        return {
            "pact:generator:type": self.type,
            **self._extra_fields,
        }

    def to_generator_json(self) -> dict[str, Any]:
        """
        Convert the generator to a generator JSON object.

        This method is used internally to convert the generator to a JSON object
        which can be embedded directly in a number of places in the Pact FFI.

        For more information about this format, see the docs:

        > https://github.com/pact-foundation/pact-specification/tree/version-4

        and

        > https://github.com/pact-foundation/pact-specification/tree/version-2?tab=readme-ov-file#matchers

        Returns:
            The generator as a generator JSON object.
        """
        return {
            "type": self.type,
            **self._extra_fields,
        }
