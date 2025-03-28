"""
Typing definitions for the matchers.

This module provides basic type definitions, and is the runtime counterpart to
the `types.pyi` stub file. The latter is used to provide much richer type
information to static type checkers like `mypy`.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict, Union

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


class MessageProducerArgs(TypedDict, total=False):
    """
    Arguments for the message handler functions.

    The message producer function must be able to accept these arguments. Pact
    Python will inspect the function's type signature to determine how best to
    pass the arguments in (e.g., as keyword arguments, position arguments,
    variadic arguments, or a combination of these). Note that Pact Python will
    prefer the use of keyword arguments if available, and therefore it is
    recommended to allow keyword arguments for the fields below if possible.
    """

    name: str
    """
    The name of the message.

    This is used to identify the message so that the function knows which
    message to generate. This is typically a string that describes the
    message. For example, `"a request to create a new user"` or `"a metric event
    for a user login"`.

    This may be omitted if the message producer functions are passed through a
    dictionary where the key is used to identify the message.
    """

    metadata: dict[str, Any] | None
    """
    Metadata associated with the message.
    """


class StateHandlerArgs(TypedDict, total=False):
    """
    Arguments for the state handler functions.

    The state handler function must be able to accept these arguments. Pact
    Python will inspect the function's type signature to determine how best to
    pass the arguments in (e.g., as keyword arguments, position arguments,
    variadic arguments, or a combination of these). Note that Pact Python will
    prefer the use of keyword arguments if available, and therefore it is
    recommended to allow keyword arguments for the fields below if possible.
    """

    state: str
    """
    The name of the state.

    This is used to identify the state so that the function knows which state to
    generate. This is typically a string that describes the state. For example,
    `"user exists"`.

    If the function is passed through a dictionary where the key is used to
    identify the state, this argument is not required.
    """

    action: Literal["setup", "teardown"]
    """
    The action to perform.

    This is either `"setup"` or `"teardown"`, and indicates whether the state
    should be set up or torn down.

    This argument is only used if the state handler is expected to perform both
    setup and teardown actions (i.e., if `teardown=True` is used when calling
    [`Verifier.state_handler][pact.v3.verifier.Verifier.state_handler]`).
    """

    parameters: dict[str, Any] | None
    """
    Parameters required to generate the state.

    This can be used to pass in any additional parameters that are required to
    generate the state. For example, if the state requires a user ID, this can
    be passed in here.
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
