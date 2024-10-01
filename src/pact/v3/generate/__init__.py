"""
Generator module.
"""

from typing import Literal, Optional

from pact.v3.generate.generator import (
    ConcreteGenerator,
    Generator,
)

__all__ = [
    "Generator",
    "random_int",
    "random_decimal",
    "random_hexadecimal",
    "random_string",
    "regex",
    "uuid",
    "date",
    "time",
    "date_time",
    "random_boolean",
    "provider_state",
    "mock_server_url",
]


def random_int(
    min_val: Optional[int] = None, max_val: Optional[int] = None
) -> Generator:
    """
    Create a random integer generator.

    Args:
        min_val (Optional[int], optional):
            The minimum value for the integer.
        max_val (Optional[int], optional):
            The maximum value for the integer.
    """
    return ConcreteGenerator("RandomInt", {"min": min_val, "max": max_val})


def random_decimal(digits: Optional[int] = None) -> Generator:
    """
    Create a random decimal generator.

    Args:
        digits (Optional[int], optional):
            The number of digits to generate.
    """
    return ConcreteGenerator("RandomDecimal", {"digits": digits})


def random_hexadecimal(digits: Optional[int] = None) -> Generator:
    """
    Create a random hexadecimal generator.

    Args:
        digits (Optional[int], optional):
            The number of digits to generate.
    """
    return ConcreteGenerator("RandomHexadecimal", {"digits": digits})


def random_string(size: Optional[int] = None) -> Generator:
    """
    Create a random string generator.

    Args:
        size:
            The size of the string to generate.
    """
    return ConcreteGenerator("RandomString", {"size": size})


def regex(regex: str) -> Generator:
    """
    Create a regex generator.

    This will generate a string that matches the given regex.

    Args:
        regex (str):
            The regex pattern to match.
    """
    return ConcreteGenerator("Regex", {"regex": regex})


def uuid(
    format_str: Optional[
        Literal["simple", "lower-case-hyphenated", "upper-case-hyphenated", "URN"]
    ] = None,
) -> Generator:
    """
    Create a UUID generator.

    Args:
        format_str (Optional[Literal[]], optional):
            The format of the UUID to generate. This parameter is only supported
            under the V4 specification.
    """
    return ConcreteGenerator("Uuid", {"format": format_str})


def date(format_str: str) -> Generator:
    """
    Create a date generator.

    This will generate a date string that matches the given format. See
    [Java SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
    for more information on the format string.

    Args:
        format_str (str):
            The format string to use for the date.
    """
    return ConcreteGenerator("Date", {"format": format_str})


def time(format_str: str) -> Generator:
    """
    Create a time generator.

    This will generate a time string that matches the given format. See
    [Java SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
    for more information on the format string.

    Args:
        format_str (str):
            The format string to use for the time.
    """
    return ConcreteGenerator("Time", {"format": format_str})


def date_time(format_str: str) -> Generator:
    """
    Create a date-time generator.

    This will generate a date-time string that matches the given format. See
    [Java SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
    for more information on the format string.

    Args:
        format_str (str):
            The format string to use for the date-time.
    """
    return ConcreteGenerator("DateTime", {"format": format_str})


def random_boolean() -> Generator:
    """
    Create a random boolean generator.
    """
    return ConcreteGenerator("RandomBoolean")


def provider_state(expression: Optional[str] = None) -> Generator:
    """
    Create a provider state generator.

    Generates a value that is looked up from the provider state context
    using the given expression.

    Args:
        expression (Optional[str], optional):
            The expression to use to look up the provider state.
    """
    return ConcreteGenerator("ProviderState", {"expression": expression})


def mock_server_url(
    regex: Optional[str] = None, example: Optional[str] = None
) -> Generator:
    """
    Create a mock server URL generator.

    Generates a URL with the mock server as the base URL.

    Args:
        regex (Optional[str], optional):
            The regex pattern to match.
        example (Optional[str], optional):
            An example URL to use.
    """
    return ConcreteGenerator("MockServerURL", {"regex": regex, "example": example})
