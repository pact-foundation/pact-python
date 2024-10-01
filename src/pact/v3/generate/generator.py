"""
Implementations of generators for the V3 and V4 specifications.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal, Optional, Union

_GeneratorTypeV3 = Literal[
    "RandomInt",
    "RandomDecimal",
    "RandomHexadecimal",
    "RandomString",
    "Regex",
    "Uuid",
    "Date",
    "Time",
    "DateTime",
    "RandomBoolean",
]
"""
Generators defines in the V3 specification.
"""

_GeneratorTypeV4 = Literal["ProviderState", "MockServerURL"]
"""
Generators defined in the V4 specification.
"""

GeneratorType = Union[_GeneratorTypeV3, _GeneratorTypeV4]
"""
All supported generator types.
"""


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
