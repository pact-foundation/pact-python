"""
Utility functions for Pact.

This module defines a number of utility functions that are used in specific
contexts within the Pact library. These functions are not intended to be
used directly by consumers of the library and as such, may change without
notice.
"""

import socket
import warnings
from contextlib import closing

_PYTHON_FORMAT_TO_JAVA_DATETIME = {
    "a": "EEE",
    "A": "EEEE",
    "b": "MMM",
    "B": "MMMM",
    # c is locale dependent, so we can't convert it directly.
    "d": "dd",
    "f": "SSSSSS",
    "G": "YYYY",
    "H": "HH",
    "I": "hh",
    "j": "DDD",
    "m": "MM",
    "M": "mm",
    "p": "a",
    "S": "ss",
    "u": "u",
    "U": "ww",
    "V": "ww",
    # w is 0-indexed in Python, but 1-indexed in Java.
    "W": "ww",
    # x is locale dependent, so we can't convert it directly.
    # X is locale dependent, so we can't convert it directly.
    "y": "yy",
    "Y": "yyyy",
    "z": "Z",
    "Z": "z",
    "%": "%",
    ":z": "XXX",
}


def strftime_to_simple_date_format(python_format: str) -> str:
    """
    Convert a Python datetime format string to Java SimpleDateFormat format.

    Python uses [`strftime`
    codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
    which are ultimately based on the C `strftime` function. Java uses
    [`SimpleDateFormat`
    codes](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
    which generally have corresponding codes, but with some differences.

    Note that this function strictly supports codes explicitly defined in the
    Python documentation. Locale-dependent codes are not supported, and codes
    supported by the underlying C library but not Python are not supported. For
    examples, `%c`, `%x`, and `%X` are not supported as they are locale
    dependent, and `%D` is not supported as it is not part of the Python
    documentation (even though it may be supported by the underlying C and
    therefore work in some Python implementations).

    Args:
        python_format:
            The Python datetime format string to convert.

    Returns:
        The equivalent Java SimpleDateFormat format string.
    """
    # Each Python format code is exactly two characters long, so we can
    # safely iterate through the string.
    idx = 0
    result: str = ""
    escaped = False

    while idx < len(python_format):
        c = python_format[idx]
        idx += 1

        if c == "%":
            c = python_format[idx]
            if escaped:
                result += "'"
                escaped = False
            result += format_code_to_java_format(c)
            # Increment another time to skip the second character of the
            # Python format code.
            idx += 1
            continue

        if c == "'":
            # In Java, single quotes are used to escape characters.
            # To insert a single quote, we need to insert two single quotes.
            # It doesn't matter if we're in an escape sequence or not, as
            # Java treats them the same.
            result += "''"
            continue

        if not escaped and c.isalpha():
            result += "'"
            escaped = True
        result += c

    if escaped:
        result += "'"
    return result


def format_code_to_java_format(code: str) -> str:
    """
    Convert a single Python format code to a Java SimpleDateFormat format.

    Args:
        code:
            The Python format code to convert, without the leading `%`. This
            will typically be a single character, but may be two characters
            for some codes.

    Returns:
        The equivalent Java SimpleDateFormat format string.
    """
    if code in ["U", "V", "W"]:
        warnings.warn(
            f"The Java equivalent for `%{code}` is locale dependent.",
            stacklevel=3,
        )

    # The following are locale-dependent, and aren't directly convertible.
    if code in ["c", "x", "X"]:
        msg = f"Cannot convert locale-dependent Python format code `%{code}` to Java"
        raise ValueError(msg)

    # The following codes simply do not have a direct equivalent in Java.
    if code in ["w"]:
        msg = f"Python format code `%{code}` is not supported in Java"
        raise ValueError(msg)

    if code in _PYTHON_FORMAT_TO_JAVA_DATETIME:
        return _PYTHON_FORMAT_TO_JAVA_DATETIME[code]

    msg = f"Unsupported Python format code `%{code}`"
    raise ValueError(msg)


def find_free_port() -> int:
    """
    Find a free port.

    This is used to find a free port to host the API on when running locally. It
    is allocated, and then released immediately so that it can be used by the
    API.

    Returns:
        The port number.
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
