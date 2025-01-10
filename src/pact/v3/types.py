# noqa: A005
"""
Typing definitions for the matchers.

This module provides basic type definitions, and is the runtime counterpart to
the `types.pyi` stub file. The latter is used to provide much richer type
information to static type checkers like `mypy`.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Optional, TypedDict, Union

from typing_extensions import TypeAlias
from yarl import URL

Matchable: TypeAlias = Any
"""
All supported matchable types.
"""

MatcherType: TypeAlias = str
"""
All supported matchers.
"""

GeneratorType: TypeAlias = str
"""
All supported generator types.
"""


class Message(TypedDict):
    """
    Message definition.

    This is a dictionary that is used to represent the message. This class can
    be used as an initializer to create a new message, or the return of a
    dictionary can be used directly.
    """

    contents: bytes
    """
    Message contents.

    These are the actual contents of the message, as a `bytes` object.
    """
    metadata: dict[str, Any] | None
    """
    Any additional metadata associated with the message.
    """
    content_type: str | None
    """
    Content type of the message.

    This should be specified as a MIME type, such as `application/json`.
    """


MessageProducerFull: TypeAlias = Callable[[str, Optional[dict[str, Any]]], Message]
"""
Full message producer signature.

This is the signature for a message producer that takes two arguments:

1.  The message name, as a string.
2.  A dictionary of parameters, or `None` if no parameters are provided.

The function must return a `bytes` object.
"""

MessageProducerNoName: TypeAlias = Callable[[Optional[dict[str, Any]]], Message]
"""
Message producer signature without the name.

This is the signature for a message producer that takes one argument:

1.  A dictionary of parameters, or `None` if no parameters are provided.

The function must return a `bytes` object.

This function must be provided as part of a dictionary mapping message names to
functions.
"""

StateHandlerFull: TypeAlias = Callable[[str, str, Optional[dict[str, Any]]], None]
"""
Full state handler signature.

This is the signature for a state handler that takes three arguments:

1.  The state name, as a string.
2.  The action (either `setup` or `teardown`), as a string.
3.  A dictionary of parameters, or `None` if no parameters are provided.
"""
StateHandlerNoAction: TypeAlias = Callable[[str, Optional[dict[str, Any]]], None]
"""
State handler signature without the action.

This is the signature for a state handler that takes two arguments:

1.  The state name, as a string.
2.  A dictionary of parameters, or `None` if no parameters are provided.
"""
StateHandlerNoState: TypeAlias = Callable[[str, Optional[dict[str, Any]]], None]
"""
State handler signature without the state.

This is the signature for a state handler that takes two arguments:

1.  The action (either `setup` or `teardown`), as a string.
2.  A dictionary of parameters, or `None` if no parameters are provided.

This function must be provided as part of a dictionary mapping state names to
functions.
"""
StateHandlerNoActionNoState: TypeAlias = Callable[[Optional[dict[str, Any]]], None]
"""
State handler signature without the state or action.

This is the signature for a state handler that takes one argument:

1.  A dictionary of parameters, or `None` if no parameters are provided.

This function must be provided as part of a dictionary mapping state names to
functions.
"""
StateHandlerUrl: TypeAlias = Union[str, URL]
"""
State handler URL signature.

Instead of providing a function to handle state changes, it is possible to
provide a URL endpoint to which the request should be made.
"""


class Unset:
    """
    Special type to represent an unset value.

    Typically, the value `None` is used to represent an unset value. However, we
    need to differentiate between a null value and an unset value. For example,
    a matcher may have a value of `None`, which is different from a matcher
    having no value at all. This class is used to represent the latter.
    """


UNSET = Unset()
"""
Instance of the `Unset` class.

This is used to provide a default value for an optional argument that needs to
differentiate between a `None` value and an unset value.
"""
