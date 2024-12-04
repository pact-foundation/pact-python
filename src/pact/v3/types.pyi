# Types stubs file
#
# This file is only used during type checking, and is ignored during runtime.
# As a result, it is safe to perform expensive imports, even if they are not
# used or available at runtime.

from collections.abc import Callable, Collection, Mapping, Sequence
from collections.abc import Set as AbstractSet
from datetime import date, datetime, time
from decimal import Decimal
from fractions import Fraction
from typing import Any, Literal, TypedDict

from pydantic import BaseModel
from typing_extensions import TypeAlias
from yarl import URL

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

class Message(TypedDict):
    contents: bytes
    metadata: dict[str, Any] | None
    content_type: str | None

MessageProducerFull: TypeAlias = Callable[[str, dict[str, Any] | None], Message]
"""
Full message producer signature.

This is the signature for a message producer that takes two arguments:

1.  The message name, as a string.
2.  A dictionary of parameters, or `None` if no parameters are provided.

The function must return a `bytes` object.
"""

MessageProducerNoName: TypeAlias = Callable[[dict[str, Any] | None], Message]
"""
Message producer signature without the name.

This is the signature for a message producer that takes one argument:

1.  A dictionary of parameters, or `None` if no parameters are provided.

The function must return a `bytes` object.

This function must be provided as part of a dictionary mapping message names to
functions.
"""

StateHandlerFull: TypeAlias = Callable[[str, str, dict[str, Any] | None], None]
"""
Full state handler signature.

This is the signature for a state handler that takes three arguments:

1.  The state name, as a string.
2.  The action (either `setup` or `teardown`), as a string.
3.  A dictionary of parameters, or `None` if no parameters are provided.
"""
StateHandlerNoAction: TypeAlias = Callable[[str, dict[str, Any] | None], None]
"""
State handler signature without the action.

This is the signature for a state handler that takes two arguments:

1.  The state name, as a string.
2.  A dictionary of parameters, or `None` if no parameters are provided.
"""
StateHandlerNoState: TypeAlias = Callable[[str, dict[str, Any] | None], None]
"""
State handler signature without the state.

This is the signature for a state handler that takes two arguments:

1.  The action (either `setup` or `teardown`), as a string.
2.  A dictionary of parameters, or `None` if no parameters are provided.

This function must be provided as part of a dictionary mapping state names to
functions.
"""
StateHandlerNoActionNoState: TypeAlias = Callable[[dict[str, Any] | None], None]
"""
State handler signature without the state or action.

This is the signature for a state handler that takes one argument:

1.  A dictionary of parameters, or `None` if no parameters are provided.

This function must be provided as part of a dictionary mapping state names to
functions.
"""
StateHandlerUrl: TypeAlias = str | URL
"""
State handler URL signature.

Instead of providing a function to handle state changes, it is possible to
provide a URL endpoint to which the request should be made.
"""

class Unset: ...

UNSET = Unset()
