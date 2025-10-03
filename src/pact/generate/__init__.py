r"""
Generator functionality.

This module provides flexible value generators for use in Pact contracts.
Generators allow you to specify dynamic values for contract testing, ensuring
that your tests remain robust and non-deterministic where appropriate. These
generators are typically used in conjunction with matchers to produce example
data for consumer-driven contract tests.

Generators are essential for producing dynamic values in contract tests, such as
random integers, dates, UUIDs, and more. This helps ensure that your contracts
are resilient to changes and do not rely on hardcoded values, which can lead to
brittle tests.

!!! warning

    Do not import functions directly from `pact.generate` to avoid shadowing
    Python built-in types. Instead, import the `generate` module and use its
    functions as `generate.int`, `generate.str`, etc.

    ```python
    # Recommended
    from pact import generate

    generate.int(...)

    # Not recommended
    from pact.generate import int

    int(...)
    ```

Many functions in this module are named after the type they generate (e.g.,
`int`, `str`, `bool`). Importing directly from this module may shadow Python
built-in types, so always use the `generate` module.

Generators are typically used in conjunction with matchers, which allow Pact to
validate values during contract tests. If a `value` is not provided within a
matcher, a generator will produce a random value that conforms to the specified
constraints.

## Basic Types

Generate random values for basic types:

```python
from pact import generate

random_bool = generate.bool()
random_int = generate.int(min=0, max=100)
random_float = generate.float(precision=2)
random_str = generate.str(size=12)
```

## Dates, Times, and UUIDs

Produce values in specific formats:

```python
random_date = generate.date(format="%Y-%m-%d")
random_time = generate.time(format="%H:%M:%S")
random_datetime = generate.datetime(format="%Y-%m-%dT%H:%M:%S%z")
random_uuid = generate.uuid(format="lowercase")
```

## Regex and Hexadecimal

Generate values matching a pattern or hexadecimal format:

```python
random_code = generate.regex(r"[A-Z]{3}-\d{4}")
random_hex = generate.hex(digits=8)
```

### Provider State and Mock Server URLs

For advanced contract scenarios:

```python
provider_value = generate.provider_state(expression="user_id")
mock_url = generate.mock_server_url(regex=r"http://localhost:\d+")
```

For more details and advanced usage, see the documentation for each function
below.
"""

from __future__ import annotations

import builtins
import warnings
from typing import TYPE_CHECKING, Literal

from pact._util import strftime_to_simple_date_format
from pact.generate.generator import (
    AbstractGenerator,
    GenericGenerator,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from types import ModuleType

# ruff: noqa: A001
#       We provide a more 'Pythonic' interface by matching the names of the
#       functions to the types they generate (e.g., `generate.int` generates
#       integers). This overrides the built-in types which are accessed via the
#       `builtins` module.
# ruff: noqa: A002
#       We only for overrides of built-ins like `min`, `max` and `type` as
#       arguments to provide a nicer interface for the user.


# The Pact specification allows for arbitrary generators to be defined; however
# in practice, only the matchers provided by the FFI are used and supported.
#
# <https://github.com/pact-foundation/pact-reference/blob/303073c/rust/pact_models/src/generators/mod.rs#L121>
__all__ = [
    "AbstractGenerator",
    "bool",
    "boolean",
    "date",
    "datetime",
    "decimal",
    "float",
    "hex",
    "hexadecimal",
    "int",
    "integer",
    "mock_server_url",
    "provider_state",
    "regex",
    "str",
    "string",
    "time",
    "timestamp",
    "uuid",
]

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

    This function is used to override the built-in `__import__` function to
    warn users when they import functions directly from this module. This is
    done to avoid shadowing built-in types and functions.
    """
    __tracebackhide__ = True
    if name == "pact.generate" and len(set(fromlist) - {"AbstractGenerator"}) > 0:
        warnings.warn(
            "Avoid `from pact.generate import <func>`. "
            "Prefer importing `generate` and use `generate.<func>`",
            stacklevel=2,
        )
    return __builtins_import(name, globals, locals, fromlist, level)


builtins.__import__ = __import__


def int(
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
) -> AbstractGenerator:
    """
    Generate a random integer.

    Args:
        min:
            Minimum value for the integer.

        max:
            Maximum value for the integer.

    Returns:
        Generator producing random integers.
    """
    params: dict[builtins.str, builtins.int] = {}
    if min is not None:
        params["min"] = min
    if max is not None:
        params["max"] = max
    return GenericGenerator("RandomInt", extra_fields=params)


def integer(
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
) -> AbstractGenerator:
    """
    Alias for [`generate.int`][pact.generate.int].

    Args:
        min:
            Minimum value for the integer.

        max:
            Maximum value for the integer.

    Returns:
        Generator producing random integers.
    """
    return int(min=min, max=max)


def float(precision: builtins.int | None = None) -> AbstractGenerator:
    """
    Generate a random decimal number.

    Precision refers to the total number of digits (excluding leading zeros),
    not decimal places. For example, precision of 3 may yield `0.123` or `12.3`.

    Args:
        precision:
            Number of digits to generate.

    Returns:
        Generator producing random decimal values.
    """
    params: dict[builtins.str, builtins.int] = {}
    if precision is not None:
        params["digits"] = precision
    return GenericGenerator("RandomDecimal", extra_fields=params)


def decimal(precision: builtins.int | None = None) -> AbstractGenerator:
    """
    Alias for [`generate.float`][pact.generate.float].

    Args:
        precision:
            Number of digits to generate.

    Returns:
        Generator producing random decimal values.
    """
    return float(precision=precision)


def hex(digits: builtins.int | None = None) -> AbstractGenerator:
    """
    Generate a random hexadecimal value.

    Args:
        digits:
            Number of digits to generate.

    Returns:
        Generator producing random hexadecimal values.
    """
    params: dict[builtins.str, builtins.int] = {}
    if digits is not None:
        params["digits"] = digits
    return GenericGenerator("RandomHexadecimal", extra_fields=params)


def hexadecimal(digits: builtins.int | None = None) -> AbstractGenerator:
    """
    Alias for [`generate.hex`][pact.generate.hex].

    Args:
        digits:
            Number of digits to generate.

    Returns:
        Generator producing random hexadecimal values.
    """
    return hex(digits=digits)


def str(size: builtins.int | None = None) -> AbstractGenerator:
    """
    Generate a random string.

    Args:
        size:
            Size of the string to generate.

    Returns:
        Generator producing random strings.
    """
    params: dict[builtins.str, builtins.int] = {}
    if size is not None:
        params["size"] = size
    return GenericGenerator("RandomString", extra_fields=params)


def string(size: builtins.int | None = None) -> AbstractGenerator:
    """
    Alias for [`generate.str`][pact.generate.str].

    Args:
        size:
            Size of the string to generate.

    Returns:
        Generator producing random strings.
    """
    return str(size=size)


def regex(regex: builtins.str) -> AbstractGenerator:
    """
    Generate a string matching a regex pattern.

    Args:
        regex:
            Regex pattern to match.

    Returns:
        Generator producing strings matching the pattern.
    """
    return GenericGenerator("Regex", {"regex": regex})


_UUID_FORMAT_NAMES = Literal["simple", "lowercase", "uppercase", "urn"]
_UUID_FORMATS: dict[_UUID_FORMAT_NAMES, builtins.str] = {
    "simple": "simple",
    "lowercase": "lower-case-hyphenated",
    "uppercase": "upper-case-hyphenated",
    "urn": "URN",
}


def uuid(
    format: _UUID_FORMAT_NAMES = "lowercase",
) -> AbstractGenerator:
    """
    Generate a UUID.

    Args:
        format:
            Format of the UUID to generate. Only supported under the V4 specification.

    Returns:
        Generator producing UUIDs in the specified format.
    """
    return GenericGenerator("Uuid", {"format": format})


def date(
    format: builtins.str = "%Y-%m-%d",
    *,
    disable_conversion: builtins.bool = False,
) -> AbstractGenerator:
    """
    Generate a date value.

    Uses Python's
    [strftime](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
    format, converted to [Java
    `SimpleDateFormat`](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
    for Pact compatibility.

    Args:
        format:
            Expected format of the date. Defaults to ISO 8601: `%Y-%m-%d`.

        disable_conversion:
            If True, disables conversion from Python's format to Java's format.
            The value must then be a Java format string.

    Returns:
        Generator producing dates in the specified format.
    """
    if not disable_conversion:
        format = strftime_to_simple_date_format(format or "%Y-%m-%d")
    return GenericGenerator("Date", {"format": format or "%yyyy-MM-dd"})


def time(
    format: builtins.str = "%H:%M:%S",
    *,
    disable_conversion: builtins.bool = False,
) -> AbstractGenerator:
    """
    Generate a time value.

    Uses Python's
    [strftime](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
    format, converted to [Java
    `SimpleDateFormat`](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)

    Args:
        format:
            Expected format of the time. Defaults to ISO 8601: `%H:%M:%S`.

        disable_conversion:
            If True, disables conversion from Python's format to Java's format.
            The value must then be a Java format string.

    Returns:
        Generator producing times in the specified format.
    """
    if not disable_conversion:
        format = strftime_to_simple_date_format(format or "%H:%M:%S")
    return GenericGenerator("Time", {"format": format or "HH:mm:ss"})


def datetime(
    format: builtins.str,
    *,
    disable_conversion: builtins.bool = False,
) -> AbstractGenerator:
    """
    Generate a datetime value.

    Uses Python's
    [strftime](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
    format, converted to [Java
    `SimpleDateFormat`](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
    for Pact compatibility.

    Args:
        format:
            Expected format of the timestamp. Defaults to ISO 8601:
            `%Y-%m-%dT%H:%M:%S%z`.

        disable_conversion:
            If True, disables conversion from Python's format to Java's format.
            The value must then be a Java format string.

    Returns:
        Generator producing datetimes in the specified format.
    """
    if not disable_conversion:
        format = strftime_to_simple_date_format(format or "%Y-%m-%dT%H:%M:%S%z")
    return GenericGenerator("DateTime", {"format": format or "yyyy-MM-dd'T'HH:mm:ssZ"})


def timestamp(
    format: builtins.str,
    *,
    disable_conversion: builtins.bool = False,
) -> AbstractGenerator:
    """
    Alias for [`generate.datetime`][pact.generate.datetime].

    Returns:
        Generator producing datetimes in the specified format.
    """
    return datetime(format=format, disable_conversion=disable_conversion)


def bool() -> AbstractGenerator:
    """
    Generate a random boolean value.

    Returns:
        Generator producing random boolean values.
    """
    return GenericGenerator("RandomBoolean")


def boolean() -> AbstractGenerator:
    """
    Alias for [`generate.bool`][pact.generate.bool].

    Returns:
        Generator producing random boolean values.
    """
    return bool()


def provider_state(expression: builtins.str | None = None) -> AbstractGenerator:
    """
    Generate a value from provider state context.

    Args:
        expression:
            Expression to look up provider state.

    Returns:
        Generator producing values from provider state context.
    """
    params: dict[builtins.str, builtins.str] = {}
    if expression is not None:
        params["expression"] = expression
    return GenericGenerator("ProviderState", extra_fields=params)


def mock_server_url(
    regex: builtins.str | None = None,
    example: builtins.str | None = None,
) -> AbstractGenerator:
    """
    Generate a mock server URL.

    Args:
        regex:
            Regex pattern to match.

        example:
            Example URL to use.

    Returns:
        Generator producing mock server URLs.
    """
    params: dict[builtins.str, builtins.str] = {}
    if regex is not None:
        params["regex"] = regex
    if example is not None:
        params["example"] = example
    return GenericGenerator("MockServerURL", extra_fields=params)
