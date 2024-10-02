"""
Typing definitions for the matchers.

This module provides basic type definitions, and is the runtime counterpart to
the `types.pyi` stub file. The latter is used to provide much richer type
information to static type checkers like `mypy`.
"""

from typing import Any

from typing_extensions import TypeAlias

Matchable: TypeAlias = Any
"""
All supported matchable types.
"""

MatcherType: TypeAlias = str
"""
All supported matchers.
"""

GeneratorType: TypeAlias = str
"""
All supported generator types.
"""


class Unset:
    """
    Special type to represent an unset value.

    Typically, the value `None` is used to represent an unset value. However, we
    need to differentiate between a null value and an unset value. For example,
    a matcher may have a value of `None`, which is different from a matcher
    having no value at all. This class is used to represent the latter.
    """


UNSET = Unset()
"""
Instance of the `Unset` class.

This is used to provide a default value for an optional argument that needs to
differentiate between a `None` value and an unset value.
"""
