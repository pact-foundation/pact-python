from collections.abc import Collection, Mapping, Sequence
from collections.abc import Set as AbstractSet
from decimal import Decimal
from fractions import Fraction
from typing import TypeAlias, TypeVar

from pydantic import BaseModel

# Make _MatchableT explicitly public, despite ultimately only being used
# privately.
__all__ = ["Matchable", "_MatchableT"]

_BaseMatchable: TypeAlias = (
    int | float | complex | bool | str | bytes | bytearray | memoryview | None
)
"""
Base types that generally can't be further decomposed.

See: https://docs.python.org/3/library/stdtypes.html
"""

_ContainerMatchable: TypeAlias = (
    Sequence[Matchable]
    | AbstractSet[Matchable]
    | Mapping[_BaseMatchable, Matchable]
    | Collection[Matchable]
)
"""
Containers that can be further decomposed.

These are defined based on the abstract base classes defined in the
[`collections.abc`][collections.abc] module.
"""

_ExtraMatchable: TypeAlias = BaseModel | Decimal | Fraction

Matchable: TypeAlias = _BaseMatchable | _ContainerMatchable | _ExtraMatchable
"""
All supported matchable types.
"""

_MatchableT = TypeVar(
    "_MatchableT",
    int,
    float,
    complex,
    bool,
    str,
    bytes,
    bytearray,
    memoryview,
    None,
    Sequence[Matchable],
    AbstractSet[Matchable],
    Mapping[_BaseMatchable, Matchable],
    Collection[Matchable],
    BaseModel,
    Decimal,
    Fraction,
)
