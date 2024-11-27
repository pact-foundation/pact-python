"""
Matching functionality.

This module provides the functionality to define matching rules to be used
within a Pact contract. These rules define the expected content of the data
being exchanged in a way that is more flexible than a simple equality check.

As an example, a contract may define how a new record is to be created through a
POST request. The consumer would define the new information to be sent, and the
expected response. The response may contain additional data added by the
provider, such as an ID and a creation timestamp. The contract would define that
the ID is of a specific format (e.g., an integer or a UUID), and that the
creation timestamp is ISO 8601 formatted.

!!! warning

    Do not import functions directly from this module. Instead, import the
    `match` module and use the functions from there:

    ```python
    # Good
    from pact.v3 import match

    match.int(...)

    # Bad
    from pact.v3.match import int

    int(...)
    ```

A number of functions in this module are named after the types they match (e.g.,
`int`, `str`, `bool`). These functions will have aliases as well for better
interoperability with the rest of the Pact ecosystem. It is important to note
that these functions will shadow the built-in types if imported directly from
this module. This is why we recommend importing the `match` module and using the
functions from there.

Matching rules are frequently combined with generators which allow for Pact to
generate values on the fly during contract testing. As a general rule for the
functions below, if a `value` is _not_ provided, a generator will be used; and
conversely, if a `value` is provided, a generator will _not_ be used.
"""

from __future__ import annotations

import builtins
import datetime as dt
import warnings
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Literal, TypeVar, overload

from pact.v3 import generate
from pact.v3._util import strftime_to_simple_date_format
from pact.v3.match.matcher import (
    ArrayContainsMatcher,
    EachKeyMatcher,
    EachValueMatcher,
    GenericMatcher,
    Matcher,
)
from pact.v3.types import UNSET, Matchable, Unset

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from types import ModuleType

    from pact.v3.generate import Generator

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
    "Matcher",
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

    This function is used to override the built-in `__import__` function to
    warn users when they import functions directly from this module. This is
    done to avoid shadowing built-in types and functions.
    """
    if name == "pact.v3.match" and len(set(fromlist) - {"Matcher"}) > 0:
        warnings.warn(
            "Avoid `from pact.v3.match import <func>`. "
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
) -> Matcher[builtins.int]:
    """
    Match an integer value.

    Args:
        value:
            Default value to use when generating a consumer test.
        min:
            If provided, the minimum value of the integer to generate.
        max:
            If provided, the maximum value of the integer to generate.
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
) -> Matcher[builtins.int]:
    """
    Alias for [`match.int`][pact.v3.match.int].
    """
    return int(value, min=min, max=max)


_NumberT = TypeVar("_NumberT", builtins.int, builtins.float, Decimal)


def float(
    value: _NumberT | Unset = UNSET,
    /,
    *,
    precision: builtins.int | None = None,
) -> Matcher[_NumberT]:
    """
    Match a floating point number.

    Args:
        value:
            Default value to use when generating a consumer test.
        precision:
            The number of decimal precision to generate.
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
) -> Matcher[_NumberT]:
    """
    Alias for [`match.float`][pact.v3.match.float].
    """
    return float(value, precision=precision)


@overload
def number(
    value: builtins.int,
    /,
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
) -> Matcher[builtins.int]: ...
@overload
def number(
    value: builtins.float,
    /,
    *,
    precision: builtins.int | None = None,
) -> Matcher[builtins.float]: ...
@overload
def number(
    value: Decimal,
    /,
    *,
    precision: builtins.int | None = None,
) -> Matcher[Decimal]: ...
@overload
def number(
    value: Unset = UNSET,
    /,
) -> Matcher[builtins.float]: ...
def number(
    value: builtins.int | builtins.float | Decimal | Unset = UNSET,  # noqa: PYI041
    /,
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
    precision: builtins.int | None = None,
) -> Matcher[builtins.int] | Matcher[builtins.float] | Matcher[Decimal]:
    """
    Match a general number.

    This matcher is a generalization of the [`integer`][pact.v3.match.integer]
    and [`decimal`][pact.v3.match.decimal] matchers. It can be used to match any
    number, whether it is an integer or a float.

    Args:
        value:
            Default value to use when generating a consumer test.
        min:
            The minimum value of the number to generate. Only used when value is
            an integer. Defaults to None.
        max:
            The maximum value of the number to generate. Only used when value is
            an integer. Defaults to None.
        precision:
            The number of decimal digits to generate. Only used when value is a
            float. Defaults to None.
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
    generator: Generator | None = None,
) -> Matcher[builtins.str]:
    """
    Match a string value.

    This function can be used to match a string value, merely verifying that the
    value is a string, possibly with a specific length.

    Args:
        value:
            Default value to use when generating a consumer test.
        size:
            The size of the string to generate during a consumer test.
        generator:
            Alternative generator to use when generating a consumer test. If
            set, the `size` argument is ignored.
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
    generator: Generator | None = None,
) -> Matcher[builtins.str]:
    """
    Alias for [`match.str`][pact.v3.match.str].
    """
    return str(value, size=size, generator=generator)


def regex(
    value: builtins.str | Unset = UNSET,
    /,
    *,
    regex: builtins.str | None = None,
) -> Matcher[builtins.str]:
    """
    Match a string against a regular expression.

    Args:
        value:
            Default value to use when generating a consumer test.
        regex:
            The regular expression to match against.
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


_UUID_FORMATS = {
    "simple": r"[0-9a-fA-F]{32}",
    "lowercase": r"[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}",
    "uppercase": r"[0-9A-F]{8}(-[0-9A-F]{4}){3}-[0-9A-F]{12}",
    "urn": r"urn:uuid:[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}",
}


def uuid(
    value: builtins.str | Unset = UNSET,
    /,
    *,
    format: Literal["uppercase", "lowercase", "urn", "simple"] | None = None,
) -> Matcher[builtins.str]:
    """
    Match a UUID value.

    This matcher internally combines the [`regex`][pact.v3.match.regex] matcher
    with a UUID regex pattern. See [RFC
    4122](https://datatracker.ietf.org/doc/html/rfc4122) for details about the
    UUID format.

    While RFC 4122 requires UUIDs to be output as lowercase, UUIDs are case
    insensitive on input. Some common alternative formats can be enforced using
    the `format` parameter.

    Args:
        value:
            Default value to use when generating a consumer test.
        format:
            Enforce a specific UUID format. The following formats are supported:

            -   `simple`: 32 hexadecimal digits with no hyphens. This is _not_ a
                valid UUID format, but is provided for convenience.
            -   `lowercase`: Lowercase hexadecimal digits with hyphens.
            -   `uppercase`: Uppercase hexadecimal digits with hyphens.
            -   `urn`: Lowercase hexadecimal digits with hyphens and a
                `urn:uuid:`

            If not provided, the matcher will accept any lowercase or uppercase.
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


def bool(value: builtins.bool | Unset = UNSET, /) -> Matcher[builtins.bool]:
    """
    Match a boolean value.

    Args:
        value:
            Default value to use when generating a consumer test.
    """
    if value is UNSET:
        return GenericMatcher("boolean", generator=generate.bool())
    return GenericMatcher("boolean", value)


def boolean(value: builtins.bool | Unset = UNSET, /) -> Matcher[builtins.bool]:
    """
    Alias for [`match.bool`][pact.v3.match.bool].
    """
    return bool(value)


def date(
    value: dt.date | builtins.str | Unset = UNSET,
    /,
    format: builtins.str | None = None,
    *,
    disable_conversion: builtins.bool = False,
) -> Matcher[builtins.str]:
    """
    Match a date value.

    A date value is a string that represents a date in a specific format. It
    does _not_ have any time information.

    Args:
        value:
            Default value to use when generating a consumer test.
        format:
            Expected format of the date. This uses Python's [`strftime`
            format](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)

            Pact internally uses the [Java
            SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
            and the conversion from Python's `strftime` format to Java's
            `SimpleDateFormat` format is done in
            [`strftime_to_simple_date_format`][pact.v3.util.strftime_to_simple_date_format].

            If not provided, an ISO 8601 date format will be used: `%Y-%m-%d`.
        disable_conversion:
            If True, the conversion from Python's `strftime` format to Java's
            `SimpleDateFormat` format will be disabled, and the format must be
            in Java's `SimpleDateFormat` format. As a result, the value must
            be a string as Python cannot format the date in the target format.
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
) -> Matcher[builtins.str]:
    """
    Match a time value.

    A time value is a string that represents a time in a specific format. It
    does _not_ have any date information.

    Args:
        value:
            Default value to use when generating a consumer test.
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
) -> Matcher[builtins.str]:
    """
    Match a datetime value.

    A timestamp value is a string that represents a date and time in a specific
    format.

    Args:
        value:
            Default value to use when generating a consumer test.
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
            a string as Python cannot format the timestamp in the target format.
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
    format = format or "%Y-%m-%dT%H:%M:%S.%f%z"
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
) -> Matcher[builtins.str]:
    """
    Alias for [`match.datetime`][pact.v3.match.datetime].
    """
    return datetime(value, format, disable_conversion=disable_conversion)


def none() -> Matcher[None]:
    """
    Match a null value.
    """
    return GenericMatcher("null")


def null() -> Matcher[None]:
    """
    Alias for [`match.none`][pact.v3.match.none].
    """
    return none()


def type(
    value: _T,
    /,
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
    generator: Generator | None = None,
) -> Matcher[_T]:
    """
    Match a value by type.

    Args:
        value:
            A value to match against. This can be a primitive value, or a more
            complex object or array.
        min:
            The minimum number of items that must match the value.
        max:
            The maximum number of items that must match the value.
        generator:
            The generator to use when generating the value.
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
    generator: Generator | None = None,
) -> Matcher[_T]:
    """
    Alias for [`match.type`][pact.v3.match.type].
    """
    return type(value, min=min, max=max, generator=generator)


def each_like(
    value: _T,
    /,
    *,
    min: builtins.int | None = None,
    max: builtins.int | None = None,
) -> Matcher[Sequence[_T]]:  # type: ignore[type-var]
    """
    Match each item in an array against a given value.

    The value itself is arbitrary, and can include other matchers.

    Args:
        value:
            The value to match against.
        min:
            The minimum number of items that must match the value. The minimum
            value is always 1, even if min is set to 0.
        max:
            The maximum number of items that must match the value.
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
    generator: Generator | None = None,
) -> Matcher[builtins.str]:
    """
    Match a string that includes a given value.

    Args:
        value:
            The value to match against.
        generator:
            The generator to use when generating the value.
    """
    return GenericMatcher(
        "include",
        value=value,
        generator=generator,
    )


def array_containing(variants: Sequence[_T | Matcher[_T]], /) -> Matcher[Sequence[_T]]:
    """
    Match an array that contains the given variants.

    Matching is successful if each variant occurs once in the array. Variants
    may be objects containing matching rules.

    Args:
        variants:
            A list of variants to match against.
    """
    return ArrayContainsMatcher(variants=variants)


def each_key_matches(
    value: Mapping[_T, Any],
    /,
    *,
    rules: Matcher[_T] | list[Matcher[_T]],
) -> Matcher[Mapping[_T, Matchable]]:
    """
    Match each key in a dictionary against a set of rules.

    Args:
        value:
            The value to match against.
        rules:
            The matching rules to match against each key.
    """
    if isinstance(rules, Matcher):
        rules = [rules]
    return EachKeyMatcher(value=value, rules=rules)


def each_value_matches(
    value: Mapping[Any, _T],
    /,
    *,
    rules: Matcher[_T] | list[Matcher[_T]],
) -> Matcher[Mapping[Matchable, _T]]:
    """
    Returns a matcher that matches each value in a dictionary against a set of rules.

    Args:
        value:
            The value to match against.
        rules:
            The matching rules to match against each value.
    """
    if isinstance(rules, Matcher):
        rules = [rules]
    return EachValueMatcher(value=value, rules=rules)
