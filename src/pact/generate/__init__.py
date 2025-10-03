"""
Generator module.
"""

from __future__ import annotations

import builtins
import warnings
from typing import TYPE_CHECKING, Literal

from pact._util import strftime_to_simple_date_format
from pact.generate.generator import (
    Generator,
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
    "Generator",
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
) -> Generator:
    """
    Create a random integer generator.

    Args:
        min:
            The minimum value for the integer.

        max:
            The maximum value for the integer.

    Returns:
        A generator that produces random integers.
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
) -> Generator:
    """
    Alias for [`generate.int`][pact.generate.int].

    Args:
        min:
            The minimum value for the integer.

        max:
            The maximum value for the integer.

    Returns:
        A generator that produces random integers.
    """
    return int(min=min, max=max)


def float(precision: builtins.int | None = None) -> Generator:
    """
    Create a random decimal generator.

    Note that the precision is the number of digits to generate _in total_, not
    the number of decimal places. Therefore a precision of `3` will generate
    numbers like `0.123` and `12.3`.

    Args:
        precision:
            The number of digits to generate.

    Returns:
        A generator that produces random decimal values.
    """
    params: dict[builtins.str, builtins.int] = {}
    if precision is not None:
        params["digits"] = precision
    return GenericGenerator("RandomDecimal", extra_fields=params)


def decimal(precision: builtins.int | None = None) -> Generator:
    """
    Alias for [`generate.float`][pact.generate.float].

    Args:
        precision:
            The number of digits to generate.

    Returns:
        A generator that produces random decimal values.
    """
    return float(precision=precision)


def hex(digits: builtins.int | None = None) -> Generator:
    """
    Create a random hexadecimal generator.

    Args:
        digits:
            The number of digits to generate.

    Returns:
        A generator that produces random hexadecimal values.
    """
    params: dict[builtins.str, builtins.int] = {}
    if digits is not None:
        params["digits"] = digits
    return GenericGenerator("RandomHexadecimal", extra_fields=params)


def hexadecimal(digits: builtins.int | None = None) -> Generator:
    """
    Alias for [`generate.hex`][pact.generate.hex].

    Args:
        digits:
            The number of digits to generate.

    Returns:
        A generator that produces random hexadecimal values.
    """
    return hex(digits=digits)


def str(size: builtins.int | None = None) -> Generator:
    """
    Create a random string generator.

    Args:
        size:
            The size of the string to generate.

    Returns:
        A generator that produces random strings.
    """
    params: dict[builtins.str, builtins.int] = {}
    if size is not None:
        params["size"] = size
    return GenericGenerator("RandomString", extra_fields=params)


def string(size: builtins.int | None = None) -> Generator:
    """
    Alias for [`generate.str`][pact.generate.str].

    Args:
        size:
            The size of the string to generate.

    Returns:
        A generator that produces random strings.
    """
    return str(size=size)


def regex(regex: builtins.str) -> Generator:
    """
    Create a regex generator.

    The generator will generate a string that matches the given regex pattern.

    Args:
        regex:
            The regex pattern to match.

    Returns:
        A generator that produces strings matching the given regex pattern.
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
) -> Generator:
    """
    Create a UUID generator.

    Args:
        format:
            The format of the UUID to generate. This parameter is only supported
            under the V4 specification.

    Returns:
        A generator that produces UUIDs in the specified format.
    """
    return GenericGenerator("Uuid", {"format": format})


def date(
    format: builtins.str = "%Y-%m-%d",
    *,
    disable_conversion: builtins.bool = False,
) -> Generator:
    """
    Create a date generator.

    !!! info

        Pact internally uses the Java's
        [`SimpleDateFormat`](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html).
        To ensure compatibility with the rest of the Python ecosystem, this
        function accepts Python's [`strftime`](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
        format and performs the conversion to Java's format internally.

    Args:
        format:
            Expected format of the date.

            If not provided, an ISO 8601 date format is used: `%Y-%m-%d`.

        disable_conversion:
            If True, the conversion from Python's `strftime` format to Java's
            `SimpleDateFormat` format will be disabled, and the format must
            be in Java's `SimpleDateFormat` format. As a result, the value must
            be a string as Python cannot format the date in the target format.

    Returns:
        A generator that produces dates in the specified format.
    """
    if not disable_conversion:
        format = strftime_to_simple_date_format(format or "%Y-%m-%d")
    return GenericGenerator("Date", {"format": format or "%yyyy-MM-dd"})


def time(
    format: builtins.str = "%H:%M:%S",
    *,
    disable_conversion: builtins.bool = False,
) -> Generator:
    """
    Create a time generator.

    !!! info

        Pact internally uses the Java's
        [`SimpleDateFormat`](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html).
        To ensure compatibility with the rest of the Python ecosystem, this
        function accepts Python's
        [`strftime`](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
        format and performs the conversion to Java's format internally.

    Args:
        format:
            Expected format of the time.

            If not provided, an ISO 8601 time format will be used: `%H:%M:%S`.

        disable_conversion:
            If True, the conversion from Python's `strftime` format to Java's
            `SimpleDateFormat` format will be disabled, and the format must be
            in Java's `SimpleDateFormat` format. As a result, the value must be
            a string as Python cannot format the time in the target format.

    Returns:
        A generator that produces times in the specified format.
    """
    if not disable_conversion:
        format = strftime_to_simple_date_format(format or "%H:%M:%S")
    return GenericGenerator("Time", {"format": format or "HH:mm:ss"})


def datetime(
    format: builtins.str,
    *,
    disable_conversion: builtins.bool = False,
) -> Generator:
    """
    Create a datetime generator.

    !!! info

        Pact internally uses the Java's
        [`SimpleDateFormat`](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html).
        To ensure compatibility with the rest of the Python ecosystem, this
        function accepts Python's
        [`strftime`](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
        format and performs the conversion to Java's format internally.

    Args:
        format:
            Expected format of the timestamp.

            If not provided, an ISO 8601 timestamp format will be used:
            `%Y-%m-%dT%H:%M:%S%z`.

        disable_conversion:
            If True, the conversion from Python's `strftime` format to Java's
            `SimpleDateFormat` format will be disabled, and the format must be
            in Java's `SimpleDateFormat` format. As a result, the value must be

    Returns:
        A generator that produces datetimes in the specified format.
    """
    if not disable_conversion:
        format = strftime_to_simple_date_format(format or "%Y-%m-%dT%H:%M:%S%z")
    return GenericGenerator("DateTime", {"format": format or "yyyy-MM-dd'T'HH:mm:ssZ"})


def timestamp(
    format: builtins.str,
    *,
    disable_conversion: builtins.bool = False,
) -> Generator:
    """
    Alias for [`generate.datetime`][pact.generate.datetime].

    Returns:
        A generator that produces datetimes in the specified format.
    """
    return datetime(format=format, disable_conversion=disable_conversion)


def bool() -> Generator:
    """
    Create a random boolean generator.

    Returns:
        A generator that produces random boolean values.
    """
    return GenericGenerator("RandomBoolean")


def boolean() -> Generator:
    """
    Alias for [`generate.bool`][pact.generate.bool].

    Returns:
        A generator that produces random boolean values.
    """
    return bool()


def provider_state(expression: builtins.str | None = None) -> Generator:
    """
    Create a provider state generator.

    Generates a value that is looked up from the provider state context
    using the given expression.

    Args:
        expression:
            The expression to use to look up the provider state.

    Returns:
        A generator that produces values from the provider state context.
    """
    params: dict[builtins.str, builtins.str] = {}
    if expression is not None:
        params["expression"] = expression
    return GenericGenerator("ProviderState", extra_fields=params)


def mock_server_url(
    regex: builtins.str | None = None,
    example: builtins.str | None = None,
) -> Generator:
    """
    Create a mock server URL generator.

    Generates a URL with the mock server as the base URL.

    Args:
        regex:
            The regex pattern to match.

        example:
            An example URL to use.

    Returns:
        A generator that produces mock server URLs.
    """
    params: dict[builtins.str, builtins.str] = {}
    if regex is not None:
        params["regex"] = regex
    if example is not None:
        params["example"] = example
    return GenericGenerator("MockServerURL", extra_fields=params)
