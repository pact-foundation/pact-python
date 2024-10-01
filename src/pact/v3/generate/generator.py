"""
Implementations of generators for the V3 and V4 specifications.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from pact.v3.types import GeneratorType


class Generator(ABC):
    """
    Generator interface for exporting.
    """

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the generator to a dictionary for json serialization.
        """


class ConcreteGenerator(Generator):
    """
    ConcreteGenerator class.

    A generator is used to generate values for a field in a response.
    """

    def __init__(
        self,
        generator_type: GeneratorType,
        extra_args: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Instantiate the generator class.

        Args:
            generator_type (GeneratorTypeV4):
                The type of generator to use.
            extra_args (dict[str, Any], optional):
                Additional configuration elements to pass to the generator.
        """
        self.type = generator_type
        self.extra_args = extra_args if extra_args is not None else {}

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the generator to a dictionary for json serialization.
        """
        data = {
            "pact:generator:type": self.type,
        }
        data.update({k: v for k, v in self.extra_args.items() if v is not None})
        return data
