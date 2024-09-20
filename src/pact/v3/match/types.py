"""
Typing definitions for the matchers.
"""

from typing import Mapping, Sequence

AtomicType = str | int | float | bool | None
MatchType = (
    AtomicType
    | dict[AtomicType, AtomicType]
    | list[AtomicType]
    | tuple[AtomicType]
    | Sequence[AtomicType]
    | Mapping[AtomicType, AtomicType]
)
