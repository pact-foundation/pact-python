# Types stubs file
#
# This file is only used during type checking, and is ignored during runtime.
# As a result, it is safe to perform expensive imports, even if they are not
# used or available at runtime.

from collections.abc import Collection, Mapping, Sequence
from collections.abc import Set as AbstractSet
from datetime import date, datetime, time
from decimal import Decimal
from fractions import Fraction
from typing import Literal

from pydantic import BaseModel
from typing_extensions import TypeAlias

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

_MatcherTypeV3: TypeAlias = Literal[
    "equality",
    "regex",
    "type",
    "include",
    "integer",
    "decimal",
    "number",
    "timestamp",
    "time",
    "date",
    "null",
    "boolean",
    "contentType",
    "values",
    "arrayContains",
]
"""
Matchers defined in the V3 specification.
"""

_MatcherTypeV4: TypeAlias = Literal[
    "statusCode",
    "notEmpty",
    "semver",
    "eachKey",
    "eachValue",
]
"""
Matchers defined in the V4 specification.
"""

MatcherType: TypeAlias = _MatcherTypeV3 | _MatcherTypeV4
"""
All supported matchers.
"""

_GeneratorTypeV3: TypeAlias = Literal[
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

_GeneratorTypeV4: TypeAlias = Literal["ProviderState", "MockServerURL"]
"""
Generators defined in the V4 specification.
"""

GeneratorType: TypeAlias = _GeneratorTypeV3 | _GeneratorTypeV4
"""
All supported generator types.
"""

class Unset: ...

UNSET = Unset()
