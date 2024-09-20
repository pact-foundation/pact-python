"""
Typing definitions for the matchers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence

AtomicType = str | int | float | bool | None


class Matcher(ABC):
    """
    Matcher interface for exporting.
    """

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the matcher to a dictionary for json serialization.
        """


MatchType = (
    AtomicType
    | Matcher
    | dict[AtomicType, "MatchType"]
    | list["MatchType"]
    | tuple["MatchType"]
    | Sequence["MatchType"]
    | Mapping[AtomicType, "MatchType"]
)
