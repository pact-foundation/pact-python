"""
Typing definitions for the matchers.
"""

from typing import Any, TypeAlias, TypeVar

# Make _MatchableT explicitly public, despite ultimately only being used
# privately.
__all__ = ["Matchable", "_MatchableT"]

Matchable: TypeAlias = Any
"""
All supported matchable types.
"""

_MatchableT = TypeVar("_MatchableT")
"""
Matchable type variable.
"""
