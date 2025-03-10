"""
Generator module.
"""

from __future__ import annotations

import builtins
import warnings
from typing import TYPE_CHECKING, Literal

from pact.v3._util import strftime_to_simple_date_format
from pact.v3.generate.generator import (
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
    if name == "pact.v3.generate" and len(set(fromlist) - {"Matcher"}) > 0:
        warnings.warn(
            "Avoid `from pact.v3.generate import <func>`. "
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
    Alias for [`generate.int`][pact.v3.generate.int].
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
    """
    params: dict[builtins.str, builtins.int] = {}
    if precision is not None:
        params["digits"] = precision
    return GenericGenerator("RandomDecimal", extra_fields=params)


def decimal(precision: builtins.int | None = None) -> Generator:
    """
    Alias for [`generate.float`][pact.v3.generate.float].
    """
    return float(precision=precision)


def hex(digits: builtins.int | None = None) -> Generator:
    """
    Create a random hexadecimal generator.

    Args:
        digits:
            The number of digits to generate.
    """
    params: dict[builtins.str, builtins.int] = {}
    if digits is not None:
        params["digits"] = digits
    return GenericGenerator("RandomHexadecimal", extra_fields=params)


def hexadecimal(digits: builtins.int | None = None) -> Generator:
    """
    Alias for [`generate.hex`][pact.v3.generate.hex].
    """
    return hex(digits=digits)


def str(size: builtins.int | None = None) -> Generator:
    """
    Create a random string generator.

    Args:
        size:
            The size of the string to generate.
    """
    params: dict[builtins.str, builtins.int] = {}
    if size is not None:
        params["size"] = size
    return GenericGenerator("RandomString", extra_fields=params)


def string(size: builtins.int | None = None) -> Generator:
    """
    Alias for [`generate.str`][pact.v3.generate.str].
    """
    return str(size=size)


def regex(regex: builtins.str) -> Generator:
    """
    Create a regex generator.

    The generator will generate a string that matches the given regex pattern.

    Args:
        regex:
            The regex pattern to match.
    """
    return GenericGenerator("Regex", {"regex": regex})


_UUID_FORMATS = {
    "simple": "simple",
    "lowercase": "lower-case-hyphenated",
    "uppercase": "upper-case-hyphenated",
    "urn": "URN",
}


def uuid(
    format: Literal["simple", "lowercase", "uppercase", "urn"] = "lowercase",
) -> Generator:
    """
    Create a UUID generator.

    Args:
        format:
            The format of the UUID to generate. This parameter is only supported
            under the V4 specification.
    """
    return GenericGenerator("Uuid", {"format": format})


def date(
    format: builtins.str = "%Y-%m-%d",
    *,
    disable_conversion: builtins.bool = False,
) -> Generator:
    """
    Create a date generator.

    Args:
        format:
            Expected format of the date. This uses Python's [`strftime`
            format](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)

            Pact internally uses the [Java
            SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
            and the conversion from Python's `strftime` format to Java's
            `SimpleDateFormat` format is done in
            [`strftime_to_simple_date_format`][pact.v3.util.strftime_to_simple_date_format].

            If not provided, an ISO 8601 date format is used: `%Y-%m-%d`.
        disable_conversion:
            If True, the conversion from Python's `strftime` format to Java's
            `SimpleDateFormat` format will be disabled, and the format must be
            in Java's `SimpleDateFormat` format. As a result, the value must
            be a string as Python cannot format the date in the target format.
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

    Args:
        format:
            Expected format of the time. This uses Python's [`strftime`
            format](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)

            Pact internally uses the [Java
            SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
            and the conversion from Python's `strftime` format to Java's
            `SimpleDateFormat` format is done in
            [`strftime_to_simple_date_format`][pact.v3.util.strftime_to_simple_date_format].

            If not provided, an ISO 8601 time format will be used: `%H:%M:%S`.
        disable_conversion:
            If True, the conversion from Python's `strftime` format to Java's
            `SimpleDateFormat` format will be disabled, and the format must be
            in Java's `SimpleDateFormat` format. As a result, the value must
            be a string as Python cannot format the time in the target format.
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
    Create a date-time generator.

    Args:
        format:
            Expected format of the timestamp. This uses Python's [`strftime`
            format](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)

            Pact internally uses the [Java
            SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
            and the conversion from Python's `strftime` format to Java's
            `SimpleDateFormat` format is done in
            [`strftime_to_simple_date_format`][pact.v3.util.strftime_to_simple_date_format].

            If not provided, an ISO 8601 timestamp format will be used:
            `%Y-%m-%dT%H:%M:%S%z`.
        disable_conversion:
            If True, the conversion from Python's `strftime` format to Java's
            `SimpleDateFormat` format will be disabled, and the format must be
            in Java's `SimpleDateFormat` format. As a result, the value must be
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
    Alias for [`generate.datetime`][pact.v3.generate.datetime].
    """
    return datetime(format=format, disable_conversion=disable_conversion)


def bool() -> Generator:
    """
    Create a random boolean generator.
    """
    return GenericGenerator("RandomBoolean")


def boolean() -> Generator:
    """
    Alias for [`generate.bool`][pact.v3.generate.bool].
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
    """
    params: dict[builtins.str, builtins.str] = {}
    if regex is not None:
        params["regex"] = regex
    if example is not None:
        params["example"] = example
    return GenericGenerator("MockServerURL", extra_fields=params)
