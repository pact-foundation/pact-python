"""
Utility functions to help with testing.

## Sharing PyTest BDD Steps

The PyTest BDD library does some 'magic' to make the given/when/then steps
available in the test context. This is done by inspecting the stack frame of the
calling function and injecting the step definition function as a fixture.

This is a problem when sharing steps between different test suites, as the stack
frame is different. Fortunately, PyTest BDD allows us to specify the stack level
to inspect, so we can use that to our advantage with the following pattern:

```python
def some_step(stacklevel: int = 1) -> None:
    @when(..., stacklevel=stacklevel + 1)
    def _():
        # Step definition goes here
```
"""

from __future__ import annotations

import base64
import hashlib
import logging
import typing
from collections.abc import Collection, Mapping
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Generic, TypeVar

from multidict import MultiDict

if typing.TYPE_CHECKING:
    from pact.v3.pact import Pact

logger = logging.getLogger(__name__)
SUITE_ROOT = Path(__file__).parent.parent / "definition"
FIXTURES_ROOT = SUITE_ROOT / "fixtures"

_T = TypeVar("_T")


class PactInteractionTuple(Generic[_T]):
    """
    Pact and interaction tuple.

    A number of steps in the compatibility suite require one or both of a `Pact`
    and an `Interaction` subclass. This named tuple is used to pass these
    objects around more easily.

    !!! note

        This should be simplified in the future to simply being a
        [`NamedTuple`][typing.NamedTuple]; however, earlier versions of Python
        do not support inheriting from multiple classes, thereby preventing
        `class PactInteractionTuple(NamedTuple, Generic[_T])` (even if
        [`Generic[_T]`][typing.Generic] serves no purpose other than to allow
        type hinting).
    """

    def __init__(self, pact: Pact, interaction: _T) -> None:
        """
        Instantiate the tuple.
        """
        self.pact = pact
        self.interaction = interaction


def string_to_int(word: str) -> int:
    """
    Convert a word to an integer.

    The word can be a number, or a word representing a number.

    Args:
        word: The word to convert.

    Returns:
        The integer value of the word.

    Raises:
        ValueError: If the word cannot be converted to an integer.
    """
    try:
        return int(word)
    except ValueError:
        pass

    try:
        return {
            "first": 1,
            "second": 2,
            "third": 3,
            "fourth": 4,
            "fifth": 5,
            "sixth": 6,
            "seventh": 7,
            "eighth": 8,
            "ninth": 9,
            "1st": 1,
            "2nd": 2,
            "3rd": 3,
            "4th": 4,
            "5th": 5,
            "6th": 6,
            "7th": 7,
            "8th": 8,
            "9th": 9,
        }[word]
    except KeyError:
        pass

    msg = f"Unable to convert {word!r} to an integer"
    raise ValueError(msg)


def truncate(data: str | bytes) -> str:
    """
    Truncate a large string or bytes object.

    This is useful for printing large strings or bytes objects in tests.
    """
    if len(data) <= 256:
        if isinstance(data, str):
            return f"{data}"
        return data.decode("utf-8", "backslashreplace")

    length = len(data)
    if isinstance(data, str):
        checksum = hashlib.sha256(data.encode()).hexdigest()
        return (
            '"'
            + data[:128]
            + "⋯"
            + data[-128:]
            + '"'
            + f" ({length} bytes, sha256={checksum[:7]})"
        )

    checksum = hashlib.sha256(data).hexdigest()
    return (
        'b"'
        + data[:8].decode("utf-8", "backslashreplace")
        + "⋯"
        + data[-8:].decode("utf-8", "backslashreplace")
        + '"'
        + f" ({length} bytes, sha256={checksum[:7]})"
    )


def parse_horizontal_table(content: list[list[str]]) -> list[dict[str, str]]:
    """
    Parse a table into a list of dictionaries.

    The table is expected to be in the following format:

    ```markdown
    | key1 | key2 | key3 |
    | val1 | val2 | val3 |
    ```

    The parsing of the Markdown table into a list of lists is first done by
    the `pytest-bdd` library. This function then converts this into a list of
    dictionaries.

    Args:
        content:
            The table contents as parsed by `pytest-bdd`.

    Returns:
        A list of dictionaries, where each dictionary represents a row in the
        table.
    """
    if len(content) < 2:
        msg = f"Expected at least two rows in the table, got {len(content)}"
        raise ValueError(msg)

    return [dict(zip(content[0], row)) for row in content[1:]]


def parse_vertical_table(content: list[list[str]]) -> dict[str, str]:
    """
    Parse a table into a single dictionary.

    The table is expected to be in the following format:

    ```markdown
    | key1 | val1 |
    | key2 | val2 |
    | key3 | val3 |
    ```

    The parsing of the Markdown table into a list of lists is first done by
    the `pytest-bdd` library. This function then converts this into a single
    dictionary for easier access.

    Args:
        content:
            The table contents as parsed by `pytest-bdd`.

    Returns:
        A dictionary, where each key is a column in the table
    """
    if len(content[0]) != 2:
        msg = f"Expected exactly two columns in the table, got {len(content[0])}"
        raise ValueError(msg)

    return {row[0]: row[1] for row in content}


def serialize(obj: Any) -> Any:  # noqa: ANN401, PLR0911
    """
    Convert an object to a dictionary.

    This function converts an object to a dictionary by calling `vars` on the
    object. This is useful for classes which are not otherwise serializable
    using `json.dumps`.

    A few special cases are handled:

    -   If the object is a `datetime` object, it is converted to an ISO 8601
        string.
    -   All forms of [`Mapping`][collections.abc.Mapping] are converted to
        dictionaries.
    -   All forms of [`Collection`][collections.abc.Collection] are converted to
        lists.

    All other types are converted to strings using the `repr` function.
    """
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()

    # Basic types which are already serializable
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj

    # Bytes
    if isinstance(obj, bytes):
        return {
            "__class__": obj.__class__.__name__,
            "data": base64.b64encode(obj).decode("utf-8"),
        }

    # Collections
    if isinstance(obj, Mapping):
        return {k: serialize(v) for k, v in obj.items()}

    if isinstance(obj, Collection):
        return [serialize(v) for v in obj]

    # Objects
    if hasattr(obj, "__dict__"):
        return {
            "__class__": obj.__class__.__name__,
            "__module__": obj.__class__.__module__,
            **{k: serialize(v) for k, v in obj.__dict__.items()},
        }

    return repr(obj)


def parse_headers(headers: str) -> MultiDict[str]:
    """
    Parse the headers.

    The headers are in the format:

    ```text
    'X-A: 1', 'X-B: 2', 'X-A: 3'
    ```

    As headers can be repeated, the result is a MultiDict.
    """
    kvs: list[tuple[str, str]] = []
    for header in headers.split(", "):
        k, _sep, v = header.strip("'").partition(": ")
        kvs.append((k, v))
    return MultiDict(kvs)


def parse_matching_rules(matching_rules: str) -> str:
    """
    Parse the matching rules.

    The matching rules are in one of two formats:

    - An explicit JSON object, prefixed by `JSON: `.
    - A fixture file which contains the matching rules.
    """
    if matching_rules.startswith("JSON: "):
        return matching_rules[6:]

    with (FIXTURES_ROOT / matching_rules).open("r") as file:
        return file.read()
