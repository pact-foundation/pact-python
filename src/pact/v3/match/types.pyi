from collections.abc import Collection, Mapping, Sequence
from collections.abc import Set as AbstractSet
from datetime import date, datetime, time
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
    | Mapping[Matchable, Matchable]
    | Collection[Matchable]
)
"""
Containers that can be further decomposed.

These are defined based on the abstract base classes defined in the
[`collections.abc`][collections.abc] module.
"""

_StdlibMatchable: TypeAlias = Decimal | Fraction | date | time | datetime
"""
Standard library types.
"""

_ExtraMatchable: TypeAlias = BaseModel
"""
Additional matchable types, typically from third-party libraries.
"""

Matchable: TypeAlias = (
    _BaseMatchable | _ContainerMatchable | _StdlibMatchable | _ExtraMatchable
)
"""
All supported matchable types.
"""

_MatchableT = TypeVar(
    "_MatchableT",
    # BaseMatchable
    int,
    float,
    complex,
    bool,
    str,
    bytes,
    bytearray,
    memoryview,
    None,
    # ContainerMatchable
    Sequence[Matchable],
    AbstractSet[Matchable],
    Mapping[Matchable, Matchable],
    Collection[Matchable],
    # StdlibMatchable
    Decimal,
    Fraction,
    date,
    time,
    datetime,
    # ExtraMatchable
    BaseModel,
    # This last one silences a number of mypy complaints if trying to have a
    # generic `Matcher[Matchable]` type.
    Matchable,
)
