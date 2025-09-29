r"""
Matching functionality.

This module defines flexible matching rules for use in Pact contracts. These
rules specify the expected content of exchanged data, allowing for more robust
contract testing than simple equality checks.

For example, a contract may specify how a new record is created via a POST
request. The consumer defines the data to send and the expected response. The
response may include additional fields from the provider, such as an ID or
creation timestamp. The contract can require the ID to match a specific format
(e.g., integer or UUID) and the timestamp to be ISO 8601.

!!! warning

    Do not import functions directly from this module. Instead, import the
    `match` module and use its functions:

    ```python
    # Recommended
    from pact import match

    match.int(...)

    # Not recommended
    from pact.match import int

    int(...)
    ```

Many functions in this module are named after the types they match (e.g., `int`,
`str`, `bool`). Importing directly from this module may shadow Python built-in
types, so always use the `match` module.

Matching rules are often combined with generators, which allow Pact to produce
values dynamically during contract tests. If a `value` is not provided, a
generator is used; if a `value` is provided, a generator is not used. This is
_not_ advised, as leads to non-deterministic tests.

!!! note

    You do not need to specify everything that will be returned from the
    provider in a JSON response. Any extra data that is received will be
    ignored and the tests will still pass, as long as the expected fields
    match the defined patterns.

For more information about the Pact matching specification, see
[Matching](https://docs.pact.io/getting_started/matching).

## Type Matching

The most common matchers validate that values are of a specific type. These
matchers can optionally accept example values:

```python
from pact import match

response = {
    "id": match.int(123),  # Any integer (example: 123)
    "name": match.str("Alice"),  # Any string (example: "Alice")
    "score": match.float(98.5),  # Any float (example: 98.5)
    "active": match.bool(True),  # Any boolean (example: True)
    "tags": match.each_like("admin"),  # Array of strings (example: ["admin"])
}
```

When no example value is provided, Pact will generate appropriate values
automatically, but this is _not_ advised, as it leads to non-deterministic
tests.

## Regular Expression Matching

For values that must match a specific pattern, use `match.regex()` with a
regular expression:

```python
response = {
    "reference": match.regex("X1234-456def", regex=r"[A-Z]\d{3,6}-[0-9a-f]{6}"),
    "phone": match.regex("+1-555-123-4567", regex=r"\+1-\d{3}-\d{3}-\d{4}"),
}
```

Note that the regular expression should be provided as a raw string (using the
`r"..."` syntax) to avoid issues with escape sequences. Advanced regex features
like lookaheads and lookbehinds should be avoided, as they may not be supported
by all Pact implementations.

## Complex Objects

For complex nested objects, matchers can be combined to create sophisticated
matching rules:

```python
from pact import match

user_response = {
    "id": match.int(123),
    "name": match.str("Alice"),
    "email": match.regex(
        "alice@example.com",
        regex=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    ),
    "confirmed": match.bool(True),
    "address": {
        "street": match.str("123 Main St"),
        "city": match.str("Anytown"),
        "postal_code": match.regex("12345", regex=r"\d{5}"),
    },
    "roles": match.each_like(match.str("admin")),  # Array of strings
}
```

The `match.type()` (or its alias `match.like()`) function provides generic type
matching for any value:

```python
# These are equivalent to the specific type matchers
response = {
    "id": match.type(123),  # Same as match.int(123)
    "name": match.like("Alice"),  # Same as match.str("Alice")
}
```

## Array Matching

For arrays where each element should match a specific pattern, use
`match.each_like()`:

```python
from pact import match

# Simple arrays
response = {
    "tags": match.each_like(match.str("admin")),  # Array of strings
    "scores": match.each_like(match.int(95)),  # Array of integers
    "active": match.each_like(match.bool(True)),  # Array of booleans
}

# Complex nested objects in arrays
users_response = {
    "users": match.each_like({
        "id": match.int(123),
        "username": match.regex("alice123", regex=r"[a-zA-Z]+\d*"),
        "roles": match.each_like(match.str("user")),  # Nested array
    })
}
```

You can also control the minimum and maximum number of array elements:

```python
response = {"items": match.each_like(match.str("item"), min=1, max=10)}
```

For arrays that must contain specific elements regardless of order, use
`match.array_containing()`. For example, to ensure an array includes certain
permissions:

```python
response = {
    "permissions": match.array_containing([
        match.str("read"),
        match.str("write"),
        match.regex("admin-edit", regex=r"admin-\w+"),
    ])
}
```

Note that additional elements may be present in the array; the matcher only
ensures the specified elements are included.

## Date and Time Matching

The `match` module provides specialized matchers for date and time values:

```python
from pact import match
from datetime import date, time, datetime

response = {
    # Date matching (YYYY-MM-DD format by default)
    "birth_date": match.date("2024-07-20"),
    "birth_date_obj": match.date(date(2024, 7, 20)),
    # Time matching (HH:MM:SS format by default)
    "start_time": match.time("14:30:00"),
    "start_time_obj": match.time(time(14, 30, 0)),
    # DateTime matching (ISO 8601 format by default)
    "created_at": match.datetime("2024-07-20T14:30:00+00:00"),
    "updated_at": match.datetime(datetime(2024, 7, 20, 14, 30, 0)),
    # Custom formats using Python strftime patterns
    "custom_date": match.date("07/20/2024", format="%m/%d/%Y"),
    "custom_time": match.time("2:30 PM", format="%I:%M %p"),
}
```

## Specialized Matchers

Other commonly used matchers include:

```python
from pact import match

response = {
    # UUID matching with different formats
    "id": match.uuid("550e8400-e29b-41d4-a716-446655440000"),
    "simple_id": match.uuid(format="simple"),  # No hyphens
    "uppercase_id": match.uuid(format="uppercase"),  # Uppercase letters
    # Number matching with constraints
    "age": match.int(25, min=18, max=99),
    "price": match.float(19.99, precision=2),
    "count": match.number(42),  # Generic number matcher
    # String matching with constraints
    "username": match.str("alice123", size=8),
    "description": match.str(),  # Any string
    # Null values
    "optional_field": match.none(),  # or match.null()
    # String inclusion matching
    "message": match.includes("success"),  # Must contain "success"
}
```

## Advanced Dictionary Matching

For dynamic dictionary structures, you can match keys and values separately:

```python
# Match each key against a pattern
user_permissions = match.each_key_matches(
    {"admin-read": True, "admin-write": False},
    rules=match.regex("admin-read", regex=r"admin-\w+"),
)

# Match each value against a pattern
user_scores = match.each_value_matches(
    {"math": 95, "science": 87}, rules=match.int(85, min=0, max=100)
)
```

"""

from __future__ import annotations

import builtins
import datetime as dt
import warnings
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Literal, TypeVar, overload

from pact import generate
from pact._util import strftime_to_simple_date_format
from pact.match.matcher import (
    AbstractMatcher,
    ArrayContainsMatcher,
    EachKeyMatcher,
    EachValueMatcher,
    GenericMatcher,
)
from pact.types import UNSET, Matchable, Unset

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from types import ModuleType

    from pact.generate import AbstractGenerator

# ruff: noqa: A001
#       We provide a more 'Pythonic' interface by matching the names of the
#       functions to the types they match (e.g., `match.int` matches integers).
#       This overrides the built-in types which are accessed via the `builtins`
#       module.
# ruff: noqa: A002
#       We only for overrides of built-ins like `min`, `max` and `type` as
#       arguments to provide a nicer interface for the user.

# The Pact specification allows for arbitrary matching rules to be defined;
# however in practice, only the matchers provided by the FFI are used and
# supported.
#
# <https://github.com/pact-foundation/pact-reference/blob/303073c/rust/pact_models/src/matchingrules/mod.rs#L62>
__all__ = [
    "AbstractMatcher",
    "array_containing",
    "bool",
    "boolean",
    "date",
    "datetime",
    "decimal",
    "each_key_matches",
    "each_like",
    "each_value_matches",
    "float",
    "includes",
    "int",
    "integer",
    "like",
    "none",
    "null",
    "number",
    "regex",
    "str",
    "string",
    "time",
    "timestamp",
    "type",
    "uuid",
]

_T = TypeVar("_T")


# We prevent users from importing from this module to avoid shadowing built-ins.
__builtins_import = builtins.__import__


def __import__(  # noqa: N807
    name: builtins.str,
    globals: Mapping[builtins.str, object] | None = None,
    locals: Mapping[builtins.str, object] | None = None,
    fromlist: Sequence[builtins.str] = (),
    level: builtins.int = 0,
) -> ModuleType:
    """
    Override to warn when importing functions directly from this module.

    This function overrides the built-in `__import__` to warn
    users when importing functions directly from this module, helping to
    avoid shadowing built-in types and functions.
    """
    __tracebackhide__ = True
    if name == "pact.match" and len(set(fromlist) - {"AbstractMatcher"}) > 0:
        warnings.warn(
            "Avoid `from pact.match import <func>`. "
            "Prefer importing `match` and use `match.<func>`",
            stacklevel=2,
        )
    return __builtins_import(name, globals, locals, fromlist, level)


builtins.__import__ = __import__


def int(
    value: builtins.int | Unset = UNSET,
    /,
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
) -> AbstractMatcher[builtins.int]:
    """
    Match an integer value.

    Args:
        value:
            Example value for consumer test generation.

        min:
            Minimum value to generate, if set.

        max:
            Maximum value to generate, if set.

    Returns:
        Matcher for integer values.
    """
    if value is UNSET:
        return GenericMatcher(
            "integer",
            generator=generate.int(min=min, max=max),
        )
    return GenericMatcher(
        "integer",
        value=value,
    )


def integer(
    value: builtins.int | Unset = UNSET,
    /,
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
) -> AbstractMatcher[builtins.int]:
    """
    Alias for [`match.int`][pact.match.int].
    """
    return int(value, min=min, max=max)


_NumberT = TypeVar("_NumberT", builtins.int, builtins.float, Decimal)


def float(
    value: _NumberT | Unset = UNSET,
    /,
    *,
    precision: builtins.int | None = None,
) -> AbstractMatcher[_NumberT]:
    """
    Match a floating-point number.

    Args:
        value:
            Example value for consumer test generation.

        precision:
            Number of decimal places to generate.

    Returns:
        Matcher for floating-point numbers.
    """
    if value is UNSET:
        return GenericMatcher(
            "decimal",
            generator=generate.float(precision),
        )
    return GenericMatcher(
        "decimal",
        value,
    )


def decimal(
    value: _NumberT | Unset = UNSET,
    /,
    *,
    precision: builtins.int | None = None,
) -> AbstractMatcher[_NumberT]:
    """
    Alias for [`match.float`][pact.match.float].
    """
    return float(value, precision=precision)


@overload
def number(
    value: builtins.int,
    /,
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
) -> AbstractMatcher[builtins.int]: ...
@overload
def number(
    value: builtins.float,
    /,
    *,
    precision: builtins.int | None = None,
) -> AbstractMatcher[builtins.float]: ...
@overload
def number(
    value: Decimal,
    /,
    *,
    precision: builtins.int | None = None,
) -> AbstractMatcher[Decimal]: ...
@overload
def number(
    value: Unset = UNSET,
    /,
) -> AbstractMatcher[builtins.float]: ...
def number(
    value: builtins.int | builtins.float | Decimal | Unset = UNSET,  # noqa: PYI041
    /,
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
    precision: builtins.int | None = None,
) -> (
    AbstractMatcher[builtins.int]
    | AbstractMatcher[builtins.float]
    | AbstractMatcher[Decimal]
):
    """
    Match any number (integer, float, or Decimal).

    Args:
        value:
            Example value for consumer test generation.

        min:
            Minimum value to generate (for integers).

        max:
            Maximum value to generate (for integers).

        precision:
            Number of decimal digits to generate (for floats).

    Returns:
        Matcher for numbers (integer, float, or Decimal).
    """
    if value is UNSET:
        if min is not None or max is not None:
            generator = generate.int(min=min, max=max)
        elif precision is not None:
            generator = generate.float(precision)
        else:
            msg = "At least one of min, max, or precision must be provided."
            raise ValueError(msg)
        return GenericMatcher("number", generator=generator)

    if isinstance(value, builtins.int):
        if precision is not None:
            warnings.warn(
                "The precision argument is ignored when value is an integer.",
                stacklevel=2,
            )
        return GenericMatcher(
            "number",
            value=value,
        )

    if isinstance(value, builtins.float):
        if min is not None or max is not None:
            warnings.warn(
                "The min and max arguments are ignored when value is not an integer.",
                stacklevel=2,
            )
        return GenericMatcher(
            "number",
            value=value,
        )

    if isinstance(value, Decimal):
        if min is not None or max is not None:
            warnings.warn(
                "The min and max arguments are ignored when value is not an integer.",
                stacklevel=2,
            )
        return GenericMatcher(
            "number",
            value=value,
        )

    msg = f"Unsupported number type: {builtins.type(value)}"
    raise TypeError(msg)


def str(
    value: builtins.str | Unset = UNSET,
    /,
    *,
    size: builtins.int | None = None,
    generator: AbstractGenerator | None = None,
) -> AbstractMatcher[builtins.str]:
    """
    Match a string value, optionally with a specific length.

    Args:
        value:
            Example value for consumer test generation.

        size:
            Length of string to generate for consumer test.

        generator:
            Alternative generator for consumer test. If set, ignores `size`.

    Returns:
        Matcher for string values.
    """
    if value is UNSET:
        if size and generator:
            warnings.warn(
                "The size argument is ignored when a generator is provided.",
                stacklevel=2,
            )
        return GenericMatcher(
            "type",
            value="string",
            generator=generator or generate.str(size),
        )

    if size is not None or generator:
        warnings.warn(
            "The size and generator arguments are ignored when a value is provided.",
            stacklevel=2,
        )
    return GenericMatcher(
        "type",
        value=value,
    )


def string(
    value: builtins.str | Unset = UNSET,
    /,
    *,
    size: builtins.int | None = None,
    generator: AbstractGenerator | None = None,
) -> AbstractMatcher[builtins.str]:
    """
    Alias for [`match.str`][pact.match.str].
    """
    return str(value, size=size, generator=generator)


def regex(
    value: builtins.str | Unset = UNSET,
    /,
    *,
    regex: builtins.str | None = None,
) -> AbstractMatcher[builtins.str]:
    """
    Match a string against a regular expression.

    Args:
        value:
            Example value for consumer test generation.

        regex:
            Regular expression pattern to match.

    Returns:
        Matcher for strings matching the given regular expression.
    """
    if regex is None:
        msg = "A regex pattern must be provided."
        raise ValueError(msg)

    if value is UNSET:
        return GenericMatcher(
            "regex",
            generator=generate.regex(regex),
            regex=regex,
        )
    return GenericMatcher(
        "regex",
        value,
        regex=regex,
    )


_UUID_FORMAT_NAMES = Literal["simple", "lowercase", "uppercase", "urn"]
_UUID_FORMATS: dict[_UUID_FORMAT_NAMES, builtins.str] = {
    "simple": r"[0-9a-fA-F]{32}",
    "lowercase": r"[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}",
    "uppercase": r"[0-9A-F]{8}(-[0-9A-F]{4}){3}-[0-9A-F]{12}",
    "urn": r"urn:uuid:[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}",
}


def uuid(
    value: builtins.str | Unset = UNSET,
    /,
    *,
    format: _UUID_FORMAT_NAMES | None = None,
) -> AbstractMatcher[builtins.str]:
    """
    Match a UUID value.

    See [RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122) for details
    about the UUID format. Some common, albeit non-compliant, alternative
    formats are also supported.

    Args:
        value:
            Example value for consumer test generation.

        format:
            Specify UUID format:

            -   `simple`: 32 hexadecimal digits, no hyphens (not standard, for
                convenience).
            -   `lowercase`: Lowercase hexadecimal digits with hyphens.
            -   `uppercase`: Uppercase hexadecimal digits with hyphens.
            -   `urn`: Lowercase hexadecimal digits with hyphens and `urn:uuid:` prefix.

            If not set, matches any case.

    Returns:
        Matcher for UUID strings.
    """
    pattern = (
        rf"^{_UUID_FORMATS[format]}$"
        if format
        else rf"^({_UUID_FORMATS['lowercase']}|{_UUID_FORMATS['uppercase']})$"
    )
    if value is UNSET:
        return GenericMatcher(
            "regex",
            generator=generate.uuid(format or "lowercase"),
            regex=pattern,
        )
    return GenericMatcher(
        "regex",
        value=value,
        regex=pattern,
    )


def bool(value: builtins.bool | Unset = UNSET, /) -> AbstractMatcher[builtins.bool]:
    """
    Match a boolean value.

    Args:
        value:
            Example value for consumer test generation.

    Returns:
        Matcher for boolean values.
    """
    if value is UNSET:
        return GenericMatcher("boolean", generator=generate.bool())
    return GenericMatcher("boolean", value)


def boolean(value: builtins.bool | Unset = UNSET, /) -> AbstractMatcher[builtins.bool]:
    """
    Alias for [`match.bool`][pact.match.bool].
    """
    return bool(value)


def date(
    value: dt.date | builtins.str | Unset = UNSET,
    /,
    format: builtins.str | None = None,
    *,
    disable_conversion: builtins.bool = False,
) -> AbstractMatcher[builtins.str]:
    """
    Match a date value (string, no time component).

    Uses Python's
    [strftime](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
    format, converted to [Java
    `SimpleDateFormat`](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
    for Pact compatibility.

    Args:
        value:
            Example value for consumer test generation.

        format:
            Date format string. Defaults to ISO 8601 (`%Y-%m-%d`).

        disable_conversion:
            If True, the conversion from Python's `strftime` format to Java's
            `SimpleDateFormat` format will be disabled, and the format must be
            in Java's `SimpleDateFormat` format. As a result, the value must
            be a string as Python cannot format the date in the target format.

    Returns:
        Matcher for date strings.
    """
    if disable_conversion:
        if not isinstance(value, builtins.str):
            msg = "When disable_conversion is True, the value must be a string."
            raise ValueError(msg)
        format = format or "yyyy-MM-dd"
        if value is UNSET:
            return GenericMatcher(
                "date",
                format=format,
                generator=generate.date(format, disable_conversion=True),
            )
        return GenericMatcher(
            "date",
            value=value,
            format=format,
        )

    format = format or "%Y-%m-%d"
    if isinstance(value, dt.date):
        value = value.strftime(format)
    format = strftime_to_simple_date_format(format)

    if value is UNSET:
        return GenericMatcher(
            "date",
            format=format,
            generator=generate.date(format, disable_conversion=True),
        )
    return GenericMatcher(
        "date",
        value=value,
        format=format,
    )


def time(
    value: dt.time | builtins.str | Unset = UNSET,
    /,
    format: builtins.str | None = None,
    *,
    disable_conversion: builtins.bool = False,
) -> AbstractMatcher[builtins.str]:
    """
    Match a time value (string, no date component).

    Uses Python's
    [strftime](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
    format, converted to [Java
    `SimpleDateFormat`](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
    for Pact compatibility.

    Args:
        value:
            Example value for consumer test generation.

        format:
            Time format string. Defaults to ISO 8601 (`%H:%M:%S`).

        disable_conversion:
            If True, disables conversion and expects Java format. Value must be
            a string.

    Returns:
        Matcher for time strings.
    """
    if disable_conversion:
        if not isinstance(value, builtins.str):
            msg = "When disable_conversion is True, the value must be a string."
            raise ValueError(msg)
        format = format or "HH:mm:ss"
        if value is UNSET:
            return GenericMatcher(
                "time",
                format=format,
                generator=generate.time(format, disable_conversion=True),
            )
        return GenericMatcher(
            "time",
            value=value,
            format=format,
        )
    format = format or "%H:%M:%S"
    if isinstance(value, dt.time):
        value = value.strftime(format)
    format = strftime_to_simple_date_format(format)
    if value is UNSET:
        return GenericMatcher(
            "time",
            format=format,
            generator=generate.time(format, disable_conversion=True),
        )
    return GenericMatcher(
        "time",
        value=value,
        format=format,
    )


def datetime(
    value: dt.datetime | builtins.str | Unset = UNSET,
    /,
    format: builtins.str | None = None,
    *,
    disable_conversion: builtins.bool = False,
) -> AbstractMatcher[builtins.str]:
    """
    Match a datetime value (string, date and time).

    Uses Python's
    [strftime](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
    format, converted to [Java
    `SimpleDateFormat`](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
    for Pact compatibility.

    Args:
        value:
            Example value for consumer test generation.

        format:
            Datetime format string. Defaults to ISO 8601 (`%Y-%m-%dT%H:%M:%S%z`).

        disable_conversion:
            If True, disables conversion and expects Java format. Value must be
            a string.

    Returns:
        Matcher for datetime strings.
    """
    if disable_conversion:
        if not isinstance(value, builtins.str):
            msg = "When disable_conversion is True, the value must be a string."
            raise ValueError(msg)
        format = format or "yyyy-MM-dd'T'HH:mm:ssZ"
        if value is UNSET:
            return GenericMatcher(
                "timestamp",
                format=format,
                generator=generate.datetime(format, disable_conversion=True),
            )
        return GenericMatcher(
            "timestamp",
            value=value,
            format=format,
        )
    format = format or "%Y-%m-%dT%H:%M:%S%z"
    if isinstance(value, dt.datetime):
        value = value.strftime(format)
    format = strftime_to_simple_date_format(format)
    if value is UNSET:
        return GenericMatcher(
            "timestamp",
            format=format,
            generator=generate.datetime(format, disable_conversion=True),
        )
    return GenericMatcher(
        "timestamp",
        value=value,
        format=format,
    )


def timestamp(
    value: dt.datetime | builtins.str | Unset = UNSET,
    /,
    format: builtins.str | None = None,
    *,
    disable_conversion: builtins.bool = False,
) -> AbstractMatcher[builtins.str]:
    """
    Alias for [`match.datetime`][pact.match.datetime].
    """
    return datetime(value, format, disable_conversion=disable_conversion)


def none() -> AbstractMatcher[None]:
    """
    Match a null value.
    """
    return GenericMatcher("null")


def null() -> AbstractMatcher[None]:
    """
    Alias for [`match.none`][pact.match.none].
    """
    return none()


def type(
    value: _T,
    /,
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
    generator: AbstractGenerator | None = None,
) -> AbstractMatcher[_T]:
    """
    Match a value by type (primitive or complex).

    Args:
        value:
            Value to match (primitive or complex).

        min:
            Minimum number of items to match.

        max:
            Maximum number of items to match.

        generator:
            Generator to use for value generation.

    Returns:
        Matcher for the given value type.
    """
    if value is UNSET:
        if not generator:
            msg = "A generator must be provided when value is not set."
            raise ValueError(msg)
        return GenericMatcher("type", min=min, max=max, generator=generator)
    return GenericMatcher("type", value, min=min, max=max, generator=generator)


def like(
    value: _T,
    /,
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
    generator: AbstractGenerator | None = None,
) -> AbstractMatcher[_T]:
    """
    Alias for [`match.type`][pact.match.type].
    """
    return type(value, min=min, max=max, generator=generator)


def each_like(
    value: _T,
    /,
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
) -> AbstractMatcher[Sequence[_T]]:  # type: ignore[type-var]
    """
    Match each item in an array against a value (can be a matcher).

    Args:
        value:
            Value to match against (can be a matcher).

        min:
            Minimum number of items to match (minimum is always 1).

        max:
            Maximum number of items to match.

    Returns:
        Matcher for arrays where each item matches the value.
    """
    if min is not None and min < 1:
        warnings.warn(
            "The minimum number of items must be at least 1.",
            stacklevel=2,
        )
    return GenericMatcher("type", value=[value], min=min, max=max)  # type: ignore[return-value]


def includes(
    value: builtins.str,
    /,
    *,
    generator: AbstractGenerator | None = None,
) -> AbstractMatcher[builtins.str]:
    """
    Match a string that includes a given value.

    Args:
        value:
            Value to match against.

        generator:
            Generator to use for value generation.

    Returns:
        Matcher for strings that include the given value.
    """
    return GenericMatcher(
        "include",
        value=value,
        generator=generator,
    )


def array_containing(
    variants: Sequence[_T | AbstractMatcher[_T]], /
) -> AbstractMatcher[Sequence[_T]]:
    """
    Match an array containing the given variants.

    Each variant must occur at least once. Variants may be matchers or objects.

    Args:
        variants:
            List of variants to match against.

    Returns:
        Matcher for arrays containing the given variants.
    """
    return ArrayContainsMatcher(variants=variants)


def each_key_matches(
    value: Mapping[_T, Any],
    /,
    *,
    rules: AbstractMatcher[_T] | list[AbstractMatcher[_T]],
) -> AbstractMatcher[Mapping[_T, Matchable]]:
    """
    Match each key in a dictionary against rules.

    Args:
        value:
            Dictionary to match against.

        rules:
            Matching rules for each key.

    Returns:
        Matcher for dictionaries where each key matches the rules.
    """
    if isinstance(rules, AbstractMatcher):
        rules = [rules]
    return EachKeyMatcher(value=value, rules=rules)


def each_value_matches(
    value: Mapping[Any, _T],
    /,
    *,
    rules: AbstractMatcher[_T] | list[AbstractMatcher[_T]],
) -> AbstractMatcher[Mapping[Matchable, _T]]:
    """
    Match each value in a dictionary against rules.

    Args:
        value:
            Dictionary to match against.

        rules:
            Matching rules for each value.

    Returns:
        Matcher for dictionaries where each value matches the rules.
    """
    if isinstance(rules, AbstractMatcher):
        rules = [rules]
    return EachValueMatcher(value=value, rules=rules)
