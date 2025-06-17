"""
Python bindings for the Pact FFI.

This module provides a Python interface to the Pact FFI. It is a thin wrapper
around the C API, and is intended to be used by the Pact Python client library
to provide a Pythonic interface to Pact.

!!! warning

    This module is not intended to be used directly by Pact users. Pact users
    should use the Pact Python client library instead. No guarantees are made
    about the stability of this module's API.

## Developer Notes

This modules should provide the following only:

-   Basic Enum classes
-   Simple wrappers around functions, including the casting of input and output
    values between the high level Python types and the low level C types.
-   Simple wrappers around some of the low-level types. Specifically designed to
    automatically handle the freeing of memory when the Python object is
    destroyed.

These low-level functions may then be combined into higher level classes and
modules. Ideally, all code outside of this module should be written in pure
Python and not worry about allocating or freeing memory.

During initial implementation, a lot of these functions will simply raise a
[`NotImplementedError`][NotImplementedError].

For those unfamiliar with CFFI, please make sure to read the [CFFI
documentation](https://cffi.readthedocs.io/en/latest/using.html).

### Handles

The Rust library exposes a number of handles to internal data structures. This
is done to avoid exposing the internal implementation details of the library to
users of the library, and avoid unnecessarily casting to and from possibly
complicated structs.

In the Rust library, the handles are thin wrappers around integers, and
unfortunately the CFFI interface sees this and automatically unwraps them,
exposing the underlying integer. As a result, we must re-wrap the integer
returned by the CFFI interface. This unfortunately means that we may be subject
to changes in private implementation details upstream.

### Freeing Memory

Python has a garbage collector, and as a result, we don't need to worry about
manually freeing memory. Having said that, Python's garbace collector is only
aware of Python objects, and not of any memory allocated by the Rust library.

To ensure that the memory allocated by the Rust library is freed, we must make
sure to define the
[`__del__`](https://docs.python.org/3/reference/datamodel.html#object.__del__)
method to call the appropriate free function whenever the Python object is
destroyed.

Note that there are some rather subtle details as to when this is called, when
it may never be called, and what global variables are accessible. This is
explained in the documentation for `__del__` above, and in Python's [garbage
collection](https://docs.python.org/3/library/gc.html) module.

### Error Handling

The FFI function should handle all errors raised by the function call, and raise
an appropriate Python exception. The exception should be raised using the
appropriate Python exception class, and should be documented in the function's
docstring.
"""

# The following lints are disabled during initial development and should be
# removed later.
# ruff: noqa: ARG001 (unused-function-argument)
# ruff: noqa: A002 (builtin-argument-shadowing)
# ruff: noqa: D101 (undocumented-public-class)

# The following lints are disabled for this file.
# ruff: noqa: SLF001
#       private-member-access, as we need access to other handles' internal
#       references, without exposing them to the user.
# pyright: reportPrivateUsage=false
#          Ignore private member access, as we frequently need to use the
#          object's underlying pointer stored in `_ptr`.

from __future__ import annotations

import gc
import inspect
import json
import logging
import typing
import warnings
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal

from pact import __version__
from pact.v3._ffi import ffi, lib  # type: ignore[import]

if TYPE_CHECKING:
    import datetime
    from collections.abc import Collection
    from collections.abc import Generator as GeneratorType
    from pathlib import Path

    import cffi
    from typing_extensions import Self

logger = logging.getLogger(__name__)

################################################################################
# Type aliases
################################################################################
# The following type aliases provide a nicer interface for end-users of the
# library, especially when it comes to [`Enum`][Enum] classes which offers
# support for string literals as alternative values.

GeneratorCategoryOptions = Literal[
    "METHOD",   "method",
    "PATH",     "path",
    "HEADER",   "header",
    "QUERY",    "query",
    "BODY",     "body",
    "STATUS",   "status",
    "METADATA", "metadata",
]  # fmt: skip
"""
Generator Category Options.

Type alias for the string literals which represent the Generator Category
Options.
"""

MatchingRuleCategoryOptions = Literal[
    "METHOD",   "method",
    "PATH",     "path",
    "HEADER",   "header",
    "QUERY",    "query",
    "BODY",     "body",
    "STATUS",   "status",
    "CONTENTS", "contents",
    "METADATA", "metadata",
]  # fmt: skip

################################################################################
# Classes
################################################################################
# The follow types are classes defined in the Rust code. Ultimately, a Python
# alternative should be implemented, but for now, the follow lines only serve
# to inform the type checker of the existence of these types.


class AsynchronousMessage:
    def __init__(self, ptr: cffi.FFI.CData, *, owned: bool = False) -> None:
        """
        Initialise a new Asynchronous Message.

        Args:
            ptr:
                CFFI data structure.

            owned:
                Whether the message is owned by something else or not. This
                determines whether the message should be freed when the Python
                object is destroyed.

        Raises:
            TypeError:
                If the `ptr` is not a `struct AsynchronousMessage`.
        """
        if ffi.typeof(ptr).cname != "struct AsynchronousMessage *":
            msg = (
                f"ptr must be a struct AsynchronousMessage, got {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr
        self._owned = owned

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "AsynchronousMessage"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"AsynchronousMessage({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the AsynchronousMessage.
        """
        if not self._owned:
            async_message_delete(self)

    @property
    def description(self) -> str:
        """
        Description of this message interaction.

        This needs to be unique in the pact file.
        """
        return async_message_get_description(self)

    def provider_states(self) -> GeneratorType[ProviderState, None, None]:
        """
        Optional provider state for the interaction.
        """
        yield from async_message_get_provider_state_iter(self)
        return  # Ensures that the parent object outlives the generator

    @property
    def contents(self) -> MessageContents | None:
        """
        The contents of the message.

        This may be `None` if the message has no contents.
        """
        return async_message_generate_contents(self)


class Consumer: ...


class Generator:
    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a generator value.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct Generator`.
        """
        if ffi.typeof(ptr).cname != "struct Generator *":
            msg = f"ptr must be a struct Generator, got {ffi.typeof(ptr).cname}"
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "Generator"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"Generator({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the Generator.
        """

    @property
    def json(self) -> dict[str, Any]:
        """
        Dictionary representation of the generator.
        """
        return json.loads(generator_to_json(self))

    def generate_string(self, context: dict[str, Any] | None = None) -> str:
        """
        Generate a string from the generator.

        Args:
            context:
                JSON payload containing any generator context. For example:

                -   The context for a `MockServerURL` generator should contain
                    details about the running mock server.
                -   The context for a `ProviderStateGenerator` should contain
                    the values returned from the provider state callback
                    function.
        """
        return generator_generate_string(self, json.dumps(context or {}))

    def generate_integer(self, context: dict[str, Any] | None = None) -> int:
        """
        Generate an integer from the generator.

        Args:
            context:
                JSON payload containing any generator context. For example:

                -   The context for a `ProviderStateGenerator` should contain
                    the values returned from the provider state callback
                    function.
        """
        return generator_generate_integer(self, json.dumps(context or {}))


class GeneratorCategoryIterator:
    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new generator category iterator.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct GeneratorCategoryIterator`.
        """
        if ffi.typeof(ptr).cname != "struct GeneratorCategoryIterator *":
            msg = (
                "ptr must be a struct GeneratorCategoryIterator, got"
                f" {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "GeneratorCategoryIterator"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"GeneratorCategoryIterator({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the GeneratorCategoryIterator.
        """
        generators_iter_delete(self)

    def __iter__(self) -> Self:
        """
        Return the iterator itself.
        """
        return self

    def __next__(self) -> GeneratorKeyValuePair:
        """
        Get the next generator category from the iterator.
        """
        return generators_iter_next(self)


class GeneratorKeyValuePair:
    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new key-value generator pair.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct GeneratorKeyValuePair`.
        """
        if ffi.typeof(ptr).cname != "struct GeneratorKeyValuePair *":
            msg = (
                "ptr must be a struct GeneratorKeyValuePair, got"
                f" {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "GeneratorKeyValuePair"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"GeneratorKeyValuePair({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the GeneratorKeyValuePair.
        """
        generators_iter_pair_delete(self)

    @property
    def path(self) -> str:
        """
        Generator path.
        """
        s = ffi.string(self._ptr.path)  # type: ignore[attr-defined]
        if isinstance(s, bytes):
            s = s.decode("utf-8")
        return s

    @property
    def generator(self) -> Generator:
        """
        Generator value.
        """
        return Generator(self._ptr.generator)  # type: ignore[attr-defined]


class HttpRequest: ...


class HttpResponse: ...


class InteractionHandle:
    """
    Handle to a HTTP Interaction.

    [Rust
    `InteractionHandle`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/mock_server/handles/struct.InteractionHandle.html)
    """

    def __init__(self, ref: int) -> None:
        """
        Initialise a new Interaction Handle.

        Args:
            ref:
                Reference to the Interaction Handle.
        """
        self._ref: int = ref

    def __str__(self) -> str:
        """
        String representation of the Interaction Handle.
        """
        return f"InteractionHandle({self._ref})"

    def __repr__(self) -> str:
        """
        String representation of the Interaction Handle.
        """
        return f"InteractionHandle({self._ref!r})"


class MatchingRule:
    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new key-value generator pair.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct MatchingRule`.
        """
        if ffi.typeof(ptr).cname != "struct MatchingRule *":
            msg = f"ptr must be a struct MatchingRule, got {ffi.typeof(ptr).cname}"
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "MatchingRule"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"MatchingRule({self._ptr!r})"

    @property
    def json(self) -> dict[str, Any]:
        """
        Dictionary representation of the matching rule.
        """
        return json.loads(matching_rule_to_json(self))


class MatchingRuleCategoryIterator:
    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new key-value generator pair.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct MatchingRuleCategoryIterator`.
        """
        if ffi.typeof(ptr).cname != "struct MatchingRuleCategoryIterator *":
            msg = (
                "ptr must be a struct MatchingRuleCategoryIterator, got"
                f" {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "MatchingRuleCategoryIterator"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"MatchingRuleCategoryIterator({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the MatchingRuleCategoryIterator.
        """
        matching_rules_iter_delete(self)

    def __iter__(self) -> Self:
        """
        Return the iterator itself.
        """
        return self

    def __next__(self) -> MatchingRuleKeyValuePair:
        """
        Get the next generator category from the iterator.
        """
        return matching_rules_iter_next(self)


class MatchingRuleDefinitionResult: ...


class MatchingRuleIterator: ...


class MatchingRuleKeyValuePair:
    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new key-value generator pair.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct MatchingRuleKeyValuePair`.
        """
        if ffi.typeof(ptr).cname != "struct MatchingRuleKeyValuePair *":
            msg = (
                "ptr must be a struct MatchingRuleKeyValuePair, got"
                f" {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "MatchingRuleKeyValuePair"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"MatchingRuleKeyValuePair({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the MatchingRuleKeyValuePair.
        """
        matching_rules_iter_pair_delete(self)

    @property
    def path(self) -> str:
        """
        Matching Rule path.
        """
        s = ffi.string(self._ptr.path)  # type: ignore[attr-defined]
        if isinstance(s, bytes):
            s = s.decode("utf-8")
        return s

    @property
    def matching_rule(self) -> MatchingRule:
        """
        Matching Rule value.
        """
        return MatchingRule(self._ptr.matching_rule)  # type: ignore[attr-defined]


class MatchingRuleResult: ...


class MessageContents:
    def __init__(self, ptr: cffi.FFI.CData, *, owned: bool = True) -> None:
        """
        Initialise a Message Contents.

        Args:
            ptr:
                CFFI data structure.

            owned:
                Whether the message is owned by something else or not. This
                determines whether the message should be freed when the Python
                object is destroyed.

        Raises:
            TypeError:
                If the `ptr` is not a `struct MessageContents`.
        """
        if ffi.typeof(ptr).cname != "struct MessageContents *":
            msg = f"ptr must be a struct MessageContents, got {ffi.typeof(ptr).cname}"
            raise TypeError(msg)
        self._ptr = ptr
        self._owned = owned

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "MessageContents"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"MessageContents({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the MessageContents.
        """
        if not self._owned:
            message_contents_delete(self)

    @property
    def contents(self) -> str | bytes | None:
        """
        Get the contents of the message.
        """
        return message_contents_get_contents_str(
            self
        ) or message_contents_get_contents_bin(self)

    @property
    def metadata(self) -> GeneratorType[MessageMetadataPair, None, None]:
        """
        Get the metadata for the message contents.
        """
        yield from message_contents_get_metadata_iter(self)
        return  # Ensures that the parent object outlives the generator

    def matching_rules(
        self,
        category: MatchingRuleCategoryOptions | MatchingRuleCategory,
    ) -> GeneratorType[MatchingRuleKeyValuePair, None, None]:
        """
        Get the matching rules for the message contents.
        """
        if isinstance(category, str):
            category = MatchingRuleCategory(category.upper())
        yield from message_contents_get_matching_rule_iter(self, category)
        return  # Ensures that the parent object outlives the generator

    def generators(
        self,
        category: GeneratorCategoryOptions | GeneratorCategory,
    ) -> GeneratorType[GeneratorKeyValuePair, None, None]:
        """
        Get the generators for the message contents.
        """
        if isinstance(category, str):
            category = GeneratorCategory(category.upper())
        yield from message_contents_get_generators_iter(self, category)
        return  # Ensures that the parent object outlives the generator


class MessageMetadataIterator:
    """
    Iterator over an interaction's metadata.
    """

    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new Message Metadata Iterator.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct MessageMetadataIterator`.
        """
        if ffi.typeof(ptr).cname != "struct MessageMetadataIterator *":
            msg = (
                "ptr must be a struct MessageMetadataIterator, got"
                f" {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "MessageMetadataIterator"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"MessageMetadataIterator({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the Pact Interaction Iterator.
        """
        message_metadata_iter_delete(self)

    def __iter__(self) -> Self:
        """
        Return the iterator itself.
        """
        return self

    def __next__(self) -> MessageMetadataPair:
        """
        Get the next interaction from the iterator.
        """
        return message_metadata_iter_next(self)


class MessageMetadataPair:
    """
    A metadata key-value pair.
    """

    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new Message Metadata Pair.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct MessageMetadataPair`.
        """
        if ffi.typeof(ptr).cname != "struct MessageMetadataPair *":
            msg = (
                f"ptr must be a struct MessageMetadataPair, got {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "MessageMetadataPair"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"MessageMetadataPair({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the Pact Interaction Iterator.
        """
        message_metadata_pair_delete(self)

    @property
    def key(self) -> str:
        """
        Metadata key.
        """
        s = ffi.string(self._ptr.key)  # type: ignore[attr-defined]
        if isinstance(s, bytes):
            s = s.decode("utf-8")
        return s

    @property
    def value(self) -> str:
        """
        Metadata value.
        """
        s = ffi.string(self._ptr.value)  # type: ignore[attr-defined]
        if isinstance(s, bytes):
            s = s.decode("utf-8")
        return s


class Mismatch: ...


class Mismatches: ...


class MismatchesIterator: ...


class Pact: ...


class PactAsyncMessageIterator:
    """
    Iterator over a Pact's asynchronous messages.
    """

    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new Pact Asynchronous Message Iterator.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct PactAsyncMessageIterator`.
        """
        if ffi.typeof(ptr).cname != "struct PactAsyncMessageIterator *":
            msg = (
                "ptr must be a struct PactAsyncMessageIterator, got"
                f" {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "PactAsyncMessageIterator"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"PactAsyncMessageIterator({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the Pact Synchronous Message Iterator.
        """
        pact_async_message_iter_delete(self)

    def __iter__(self) -> Self:
        """
        Return the iterator itself.
        """
        return self

    def __next__(self) -> AsynchronousMessage:
        """
        Get the next message from the iterator.
        """
        return pact_async_message_iter_next(self)


class PactHandle:
    """
    Handle to a Pact.

    [Rust
    `PactHandle`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/mock_server/handles/struct.PactHandle.html)
    """

    def __init__(self, ref: int) -> None:
        """
        Initialise a new Pact Handle.

        Args:
            ref:
                Rust library reference to the Pact Handle.
        """
        self._ref: int = ref

    def __del__(self) -> None:
        """
        Destructor for the Pact Handle.
        """
        cleanup_plugins(self)
        free_pact_handle(self)

    def __str__(self) -> str:
        """
        String representation of the Pact Handle.
        """
        return f"PactHandle({self._ref})"

    def __repr__(self) -> str:
        """
        String representation of the Pact Handle.
        """
        return f"PactHandle({self._ref!r})"


class PactServerHandle:
    """
    Handle to a Pact Server.

    This does not have an exact correspondence in the Rust library. It is used
    to manage the lifecycle of the mock server.

    # Implementation Notes

    The Rust library uses the port number as a unique identifier, in much the
    same was as it uses a wrapped integer for the Pact handle.
    """

    def __init__(self, ref: int) -> None:
        """
        Initialise a new Pact Server Handle.

        Args:
            ref:
                Rust library reference to the Pact Server.
        """
        self._ref: int = ref

    def __del__(self) -> None:
        """
        Destructor for the Pact Server Handle.
        """
        cleanup_mock_server(self)

    def __str__(self) -> str:
        """
        String representation of the Pact Server Handle.
        """
        return f"PactServerHandle({self._ref})"

    def __repr__(self) -> str:
        """
        String representation of the Pact Server Handle.
        """
        return f"PactServerHandle({self._ref!r})"

    @property
    def port(self) -> int:
        """
        Port on which the Pact Server is running.
        """
        return self._ref


class PactInteraction: ...


class PactInteractionIterator:
    """
    Iterator over a Pact's interactions.

    Interactions encompasses all types of interactions, including HTTP
    interactions and messages.
    """

    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new Pact Interaction Iterator.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct PactInteractionIterator`.
        """
        if ffi.typeof(ptr).cname != "struct PactInteractionIterator *":
            msg = (
                "ptr must be a struct PactInteractionIterator, got"
                f" {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "PactInteractionIterator"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"PactInteractionIterator({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the Pact Interaction Iterator.
        """
        pact_interaction_iter_delete(self)

    def __next__(self) -> PactInteraction:
        """
        Get the next interaction from the iterator.
        """
        return pact_interaction_iter_next(self)


class PactSyncHttpIterator:
    """
    Iterator over a Pact's synchronous HTTP interactions.
    """

    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new Pact Synchronous HTTP Iterator.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct PactSyncHttpIterator`.
        """
        if ffi.typeof(ptr).cname != "struct PactSyncHttpIterator *":
            msg = (
                "ptr must be a struct PactSyncHttpIterator, got"
                f" {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "PactSyncHttpIterator"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"PactSyncHttpIterator({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the Pact Synchronous HTTP Iterator.
        """
        pact_sync_http_iter_delete(self)

    def __iter__(self) -> Self:
        """
        Return the iterator itself.
        """
        return self

    def __next__(self) -> SynchronousHttp:
        """
        Get the next message from the iterator.
        """
        return pact_sync_http_iter_next(self)


class PactSyncMessageIterator:
    """
    Iterator over a Pact's synchronous messages.
    """

    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new Pact Synchronous Message Iterator.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct PactSyncMessageIterator`.
        """
        if ffi.typeof(ptr).cname != "struct PactSyncMessageIterator *":
            msg = (
                "ptr must be a struct PactSyncMessageIterator, got"
                f" {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "PactSyncMessageIterator"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"PactSyncMessageIterator({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the Pact Synchronous Message Iterator.
        """
        pact_sync_message_iter_delete(self)

    def __iter__(self) -> Self:
        """
        Return the iterator itself.
        """
        return self

    def __next__(self) -> SynchronousMessage:
        """
        Get the next message from the iterator.
        """
        return pact_sync_message_iter_next(self)


class Provider: ...


class ProviderState:
    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new ProviderState.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct ProviderState`.
        """
        if ffi.typeof(ptr).cname != "struct ProviderState *":
            msg = f"ptr must be a struct ProviderState, got {ffi.typeof(ptr).cname}"
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "ProviderState({self.name!r})"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"ProviderState({self._ptr!r})"

    @property
    def name(self) -> str:
        """
        Provider State name.
        """
        return provider_state_get_name(self) or ""

    def parameters(self) -> GeneratorType[tuple[str, str], None, None]:
        """
        Provider State parameters.

        This is a generator that yields key-value pairs.
        """
        for p in provider_state_get_param_iter(self):
            yield p.key, p.value
        return  # Ensures that the parent object outlives the generator


class ProviderStateIterator:
    """
    Iterator over an interactions ProviderStates.
    """

    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new Provider State Iterator.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct ProviderStateIterator`.
        """
        if ffi.typeof(ptr).cname != "struct ProviderStateIterator *":
            msg = (
                "ptr must be a struct ProviderStateIterator, got"
                f" {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "ProviderStateIterator"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"ProviderStateIterator({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the Provider State Iterator.
        """
        provider_state_iter_delete(self)

    def __iter__(self) -> ProviderStateIterator:
        """
        Return the iterator itself.
        """
        return self

    def __next__(self) -> ProviderState:
        """
        Get the next message from the iterator.
        """
        return provider_state_iter_next(self)


class ProviderStateParamIterator:
    """
    Iterator over a Provider States Parameters.
    """

    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new Provider State Param Iterator.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct ProviderStateParamIterator`.
        """
        if ffi.typeof(ptr).cname != "struct ProviderStateParamIterator *":
            msg = (
                "ptr must be a struct ProviderStateParamIterator, got"
                f" {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "ProviderStateParamIterator"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"ProviderStateParamIterator({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the Provider State Param Iterator.
        """
        provider_state_param_iter_delete(self)

    def __iter__(self) -> ProviderStateParamIterator:
        """
        Return the iterator itself.
        """
        return self

    def __next__(self) -> ProviderStateParamPair:
        """
        Get the next message from the iterator.
        """
        return provider_state_param_iter_next(self)


class ProviderStateParamPair:
    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new ProviderStateParamPair.

        Args:
            ptr:
                CFFI data structure.

        Raises:
            TypeError:
                If the `ptr` is not a `struct ProviderStateParamPair`.
        """
        if ffi.typeof(ptr).cname != "struct ProviderStateParamPair *":
            msg = (
                "ptr must be a struct ProviderStateParamPair, got"
                f" {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "ProviderStateParamPair"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"ProviderStateParamPair({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the Provider State Param Pair.
        """
        provider_state_param_pair_delete(self)

    @property
    def key(self) -> str:
        """
        Provider State Param key.
        """
        s = ffi.string(self._ptr.key)  # type: ignore[attr-defined]
        if isinstance(s, bytes):
            s = s.decode("utf-8")
        return s

    @property
    def value(self) -> str:
        """
        Provider State Param value.
        """
        s = ffi.string(self._ptr.value)  # type: ignore[attr-defined]
        if isinstance(s, bytes):
            s = s.decode("utf-8")
        return s


class SynchronousHttp:
    def __init__(self, ptr: cffi.FFI.CData, *, owned: bool = False) -> None:
        """
        Initialise a new Synchronous HTTP Interaction.

        Args:
            ptr:
                CFFI data structure.

            owned:
                Whether the message is owned by something else or not. This
                determines whether the message should be freed when the Python
                object is destroyed.

        Raises:
            TypeError:
                If the `ptr` is not a `struct SynchronousHttp`.
        """
        if ffi.typeof(ptr).cname != "struct SynchronousHttp *":
            msg = f"ptr must be a struct SynchronousHttp, got {ffi.typeof(ptr).cname}"
            raise TypeError(msg)
        self._ptr = ptr
        self._owned = owned

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "SynchronousHttp"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"SynchronousHttp({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the SynchronousHttp.
        """
        if not self._owned:
            sync_http_delete(self)

    @property
    def description(self) -> str:
        """
        Description of this message interaction.

        This needs to be unique in the pact file.
        """
        return sync_http_get_description(self)

    def provider_states(self) -> GeneratorType[ProviderState, None, None]:
        """
        Optional provider state for the interaction.
        """
        yield from sync_http_get_provider_state_iter(self)
        return  # Ensures that the parent object outlives the generator

    @property
    def request_contents(self) -> str | bytes | None:
        """
        The contents of the request.
        """
        return sync_http_get_request_contents(
            self
        ) or sync_http_get_request_contents_bin(self)

    @property
    def response_contents(self) -> str | bytes | None:
        """
        The contents of the response.
        """
        return sync_http_get_response_contents(
            self
        ) or sync_http_get_response_contents_bin(self)


class SynchronousMessage:
    def __init__(self, ptr: cffi.FFI.CData, *, owned: bool = False) -> None:
        """
        Initialise a new Synchronous Message.

        Args:
            ptr:
                CFFI data structure.

            owned:
                Whether the message is owned by something else or not. This
                determines whether the message should be freed when the Python
                object is destroyed.

        Raises:
            TypeError:
                If the `ptr` is not a `struct SynchronousMessage`.
        """
        if ffi.typeof(ptr).cname != "struct SynchronousMessage *":
            msg = (
                f"ptr must be a struct SynchronousMessage, got {ffi.typeof(ptr).cname}"
            )
            raise TypeError(msg)
        self._ptr = ptr
        self._owned = owned

    def __str__(self) -> str:
        """
        Nice string representation.
        """
        return "SynchronousMessage"

    def __repr__(self) -> str:
        """
        Debugging representation.
        """
        return f"SynchronousMessage({self._ptr!r})"

    def __del__(self) -> None:
        """
        Destructor for the SynchronousMessage.
        """
        if not self._owned:
            sync_message_delete(self)

    @property
    def description(self) -> str:
        """
        Description of this message interaction.

        This needs to be unique in the pact file.
        """
        return sync_message_get_description(self)

    def provider_states(self) -> GeneratorType[ProviderState, None, None]:
        """
        Optional provider state for the interaction.
        """
        yield from sync_message_get_provider_state_iter(self)
        return  # Ensures that the parent object outlives the generator

    @property
    def request_contents(self) -> MessageContents:
        """
        The contents of the message.
        """
        return sync_message_generate_request_contents(self)

    @property
    def response_contents(self) -> GeneratorType[MessageContents, None, None]:
        """
        The contents of the responses.
        """
        yield from (
            sync_message_generate_response_contents(self, i)
            for i in range(sync_message_get_number_responses(self))
        )
        return  # Ensures that the parent object outlives the generator


class VerifierHandle:
    """
    Handle to a Verifier.

    [Rust `VerifierHandle`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/verifier/handle/struct.VerifierHandle.html)
    """

    def __init__(self, ref: cffi.FFI.CData) -> None:
        """
        Initialise a new Verifier Handle.

        Args:
            ref:
                Rust library reference to the Verifier Handle.
        """
        self._ref = ref

    def __del__(self) -> None:
        """
        Destructor for the Verifier Handle.
        """
        verifier_shutdown(self)

    def __str__(self) -> str:
        """
        String representation of the Verifier Handle.
        """
        return f"VerifierHandle({hex(id(self._ref))})"

    def __repr__(self) -> str:
        """
        String representation of the Verifier Handle.
        """
        return f"<VerifierHandle: _ref at {hex(id(self._ref))}>"


class ExpressionValueType(Enum):
    """
    Expression Value Type.

    [Rust `ExpressionValueType`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/models/expressions/enum.ExpressionValueType.html)
    """

    UNKNOWN = lib.ExpressionValueType_Unknown
    STRING = lib.ExpressionValueType_String
    NUMBER = lib.ExpressionValueType_Number
    INTEGER = lib.ExpressionValueType_Integer
    DECIMAL = lib.ExpressionValueType_Decimal
    BOOLEAN = lib.ExpressionValueType_Boolean

    def __str__(self) -> str:
        """
        Informal string representation of the Expression Value Type.
        """
        return self.name

    def __repr__(self) -> str:
        """
        Information-rich string representation of the Expression Value Type.
        """
        return f"ExpressionValueType.{self.name}"


class GeneratorCategory(Enum):
    """
    Generator Category.

    [Rust `GeneratorCategory`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/models/generators/enum.GeneratorCategory.html)
    """

    METHOD = lib.GeneratorCategory_METHOD
    PATH = lib.GeneratorCategory_PATH
    HEADER = lib.GeneratorCategory_HEADER
    QUERY = lib.GeneratorCategory_QUERY
    BODY = lib.GeneratorCategory_BODY
    STATUS = lib.GeneratorCategory_STATUS
    METADATA = lib.GeneratorCategory_METADATA

    def __str__(self) -> str:
        """
        Informal string representation of the Generator Category.
        """
        return self.name

    def __repr__(self) -> str:
        """
        Information-rich string representation of the Generator Category.
        """
        return f"GeneratorCategory.{self.name}"


class InteractionPart(Enum):
    """
    Interaction Part.

    [Rust `InteractionPart`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/mock_server/handles/enum.InteractionPart.html)
    """

    REQUEST = lib.InteractionPart_Request
    RESPONSE = lib.InteractionPart_Response

    def __str__(self) -> str:
        """
        Informal string representation of the Interaction Part.
        """
        return self.name

    def __repr__(self) -> str:
        """
        Information-rich string representation of the Interaction Part.
        """
        return f"InteractionPath.{self.name}"


class LevelFilter(Enum):
    """Level Filter."""

    OFF = lib.LevelFilter_Off
    ERROR = lib.LevelFilter_Error
    WARN = lib.LevelFilter_Warn
    INFO = lib.LevelFilter_Info
    DEBUG = lib.LevelFilter_Debug
    TRACE = lib.LevelFilter_Trace

    def __str__(self) -> str:
        """
        Informal string representation of the Level Filter.
        """
        return self.name

    def __repr__(self) -> str:
        """
        Information-rich string representation of the Level Filter.
        """
        return f"LevelFilter.{self.name}"


class MatchingRuleCategory(Enum):
    """
    Matching Rule Category.

    [Rust `MatchingRuleCategory`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/models/matching_rules/enum.MatchingRuleCategory.html)
    """

    METHOD = lib.MatchingRuleCategory_METHOD
    PATH = lib.MatchingRuleCategory_PATH
    HEADER = lib.MatchingRuleCategory_HEADER
    QUERY = lib.MatchingRuleCategory_QUERY
    BODY = lib.MatchingRuleCategory_BODY
    STATUS = lib.MatchingRuleCategory_STATUS
    CONTENTS = lib.MatchingRuleCategory_CONTENTS
    METADATA = lib.MatchingRuleCategory_METADATA

    def __str__(self) -> str:
        """
        Informal string representation of the Matching Rule Category.
        """
        return self.name

    def __repr__(self) -> str:
        """
        Information-rich string representation of the Matching Rule Category.
        """
        return f"MatchingRuleCategory.{self.name}"


class PactSpecification(Enum):
    """
    Pact Specification.

    [Rust `PactSpecification`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/models/pact_specification/enum.PactSpecification.html)
    """

    UNKNOWN = lib.PactSpecification_Unknown
    V1 = lib.PactSpecification_V1
    V1_1 = lib.PactSpecification_V1_1
    V2 = lib.PactSpecification_V2
    V3 = lib.PactSpecification_V3
    V4 = lib.PactSpecification_V4

    @classmethod
    def from_str(cls, version: str) -> PactSpecification:
        """
        Instantiate a Pact Specification from a string.

        This method is case-insensitive, and allows for the version to be
        specified with or without a leading "V", and with either a dot or an
        underscore as the separator.

        Args:
            version:
                The version of the Pact Specification.

        Returns:
            The Pact Specification.
        """
        version = version.upper().replace(".", "_")
        if version.startswith("V"):
            return cls[version]
        return cls["V" + version]

    def __str__(self) -> str:
        """
        Informal string representation of the Pact Specification.
        """
        return self.name

    def __repr__(self) -> str:
        """
        Information-rich string representation of the Pact Specification.
        """
        return f"PactSpecification.{self.name}"


class StringResult:
    """
    String result.
    """

    class _StringResult(Enum):
        """
        Internal enum from Pact FFI.

        [Rust `StringResult`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/mock_server/enum.StringResult.html)
        """

        FAILED = lib.StringResult_Failed
        OK = lib.StringResult_Ok

    class _StringResultCData:
        tag: int
        ok: cffi.FFI.CData
        failed: cffi.FFI.CData

    def __init__(self, cdata: cffi.FFI.CData) -> None:
        """
        Initialise a new String Result.

        Args:
            cdata:
                CFFI data structure.

        Raises:
            TypeError:
                If the `cdata` is not a `struct StringResult`.
        """
        if ffi.typeof(cdata).cname != "struct StringResult":
            msg = f"cdata must be a struct StringResult, got {ffi.typeof(cdata).cname}"
            raise TypeError(msg)
        self._cdata = typing.cast("StringResult._StringResultCData", cdata)

    def __str__(self) -> str:
        """
        String representation of the String Result.
        """
        return self.text

    def __repr__(self) -> str:
        """
        Debugging string representation of the String Result.
        """
        return f"<StringResult: {'OK' if self.is_ok else 'FAILED'}, {self.text!r}>"

    @property
    def is_failed(self) -> bool:
        """
        Whether the result is an error.
        """
        return self._cdata.tag == StringResult._StringResult.FAILED.value

    @property
    def is_ok(self) -> bool:
        """
        Whether the result is ok.
        """
        return self._cdata.tag == StringResult._StringResult.OK.value

    @property
    def text(self) -> str:
        """
        The text of the result.
        """
        # The specific `.ok` or `.failed` does not matter.
        s = ffi.string(self._cdata.ok)
        if isinstance(s, bytes):
            return s.decode("utf-8")
        return s

    def raise_exception(self) -> None:
        """
        Raise an exception with the text of the result.

        Raises:
            RuntimeError:
                If the result is an error.

        Raises:
            RuntimeError:
                If the result is an error.
        """
        if self.is_failed:
            raise RuntimeError(self.text)


class OwnedString(str):
    """
    A string that owns its own memory.

    This is used to ensure that the memory is freed when the string is
    destroyed.

    As this is subclassed from `str`, it can be used in place of a normal string
    in most cases.
    """

    __slots__ = ("_ptr", "_string")

    def __new__(cls, ptr: cffi.FFI.CData) -> Self:
        """
        Create a new Owned String.

        As this is a subclass of the immutable type `str`, we need to override
        the `__new__` method to ensure that the string is initialised correctly.
        """
        s = ffi.string(ptr)
        return super().__new__(cls, s if isinstance(s, str) else s.decode("utf-8"))

    def __init__(self, ptr: cffi.FFI.CData) -> None:
        """
        Initialise a new Owned String.

        Args:
            ptr:
                CFFI data structure.
        """
        self._ptr = ptr
        s = ffi.string(ptr)
        self._string = s if isinstance(s, str) else s.decode("utf-8")

    def __str__(self) -> str:
        """
        String representation of the Owned String.
        """
        return self._string

    def __repr__(self) -> str:
        """
        Debugging string representation of the Owned String.
        """
        return f"<OwnedString: {self._string!r}, ptr={self._ptr!r}>"

    def __del__(self) -> None:
        """
        Destructor for the Owned String.
        """
        string_delete(self)

    def __eq__(self, other: object) -> bool:
        """
        Equality comparison.

        Args:
            other:
                The object to compare to.

        Returns:
            Whether the two objects are equal.
        """
        if isinstance(other, OwnedString):
            return self._ptr == other._ptr
        if isinstance(other, str):
            return self._string == other
        return super().__eq__(other)

    def __hash__(self) -> int:
        """
        Hash the Owned String.

        Returns:
            The hash of the Owned String.
        """
        return hash(self._string)


def version() -> str:
    """
    Return the version of the pact_ffi library.

    [Rust `pactffi_version`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_version)

    Returns:
        The version of the pact_ffi library as a string, in the form of `x.y.z`.
    """
    v = ffi.string(lib.pactffi_version())
    if isinstance(v, bytes):
        return v.decode("utf-8")
    return v


def init(log_env_var: str) -> None:
    """
    Initialise the mock server library.

    This can provide an environment variable name to use to set the log levels.
    This function should only be called once, as it tries to install a global
    tracing subscriber.

    [Rust
    `pactffi_init`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_init)

    # Safety

    log_env_var must be a valid NULL terminated UTF-8 string.
    """
    raise NotImplementedError


def init_with_log_level(level: str = "INFO") -> None:
    """
    Initialises logging, and sets the log level explicitly.

    This function should only be called once, as it tries to install a global
    tracing subscriber.

    [Rust
    `pactffi_init_with_log_level`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_init_with_log_level)

    Args:
        level:
            One of TRACE, DEBUG, INFO, WARN, ERROR, NONE/OFF. Case-insensitive.

    # Safety

    Exported functions are inherently unsafe.
    """
    raise NotImplementedError


def enable_ansi_support() -> None:
    """
    Enable ANSI coloured output on Windows.

    On non-Windows platforms, this function is a no-op.

    [Rust
    `pactffi_enable_ansi_support`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_enable_ansi_support)

    # Safety

    This function is safe.
    """
    raise NotImplementedError


def log_message(
    message: str,
    log_level: LevelFilter | str = LevelFilter.ERROR,
    source: str | None = None,
) -> None:
    """
    Log using the shared core logging facility.

    [Rust
    `pactffi_log_message`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_log_message)

    This is useful for callers to have a single set of logs.

    Args:
        message:
            The contents written to the log

        log_level:
            The verbosity at which this message should be logged.

        source:
            The source of the log, such as the class, module or caller.
    """
    if isinstance(log_level, str):
        log_level = LevelFilter[log_level.upper()]
    if source is None:
        source = inspect.stack()[1].function
    lib.pactffi_log_message(
        source.encode("utf-8"),
        log_level.name.encode("utf-8"),
        message.encode("utf-8"),
    )


def mismatches_get_iter(mismatches: Mismatches) -> MismatchesIterator:
    """
    Get an iterator over mismatches.

    [Rust
    `pactffi_mismatches_get_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_mismatches_get_iter)
    """
    raise NotImplementedError


def mismatches_delete(mismatches: Mismatches) -> None:
    """
    Delete mismatches.

    [Rust `pactffi_mismatches_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_mismatches_delete)
    """
    raise NotImplementedError


def mismatches_iter_next(iter: MismatchesIterator) -> Mismatch:
    """
    Get the next mismatch from a mismatches iterator.

    [Rust `pactffi_mismatches_iter_next`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_mismatches_iter_next)

    Returns a null pointer if no mismatches remain.
    """
    raise NotImplementedError


def mismatches_iter_delete(iter: MismatchesIterator) -> None:
    """
    Delete a mismatches iterator when you're done with it.

    [Rust `pactffi_mismatches_iter_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_mismatches_iter_delete)
    """
    raise NotImplementedError


def mismatch_to_json(mismatch: Mismatch) -> str:
    """
    Get a JSON representation of the mismatch.

    [Rust `pactffi_mismatch_to_json`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_mismatch_to_json)
    """
    raise NotImplementedError


def mismatch_type(mismatch: Mismatch) -> str:
    """
    Get the type of a mismatch.

    [Rust `pactffi_mismatch_type`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_mismatch_type)
    """
    raise NotImplementedError


def mismatch_summary(mismatch: Mismatch) -> str:
    """
    Get a summary of a mismatch.

    [Rust `pactffi_mismatch_summary`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_mismatch_summary)
    """
    raise NotImplementedError


def mismatch_description(mismatch: Mismatch) -> str:
    """
    Get a description of a mismatch.

    [Rust `pactffi_mismatch_description`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_mismatch_description)
    """
    raise NotImplementedError


def mismatch_ansi_description(mismatch: Mismatch) -> str:
    """
    Get an ANSI-compatible description of a mismatch.

    [Rust `pactffi_mismatch_ansi_description`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_mismatch_ansi_description)
    """
    raise NotImplementedError


def get_error_message(length: int = 1024) -> str | None:
    """
    Provide the error message from `LAST_ERROR` to the calling C code.

    [Rust
    `pactffi_get_error_message`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_get_error_message)

    This function should be called after any other function in the pact_matching
    FFI indicates a failure with its own error message, if the caller wants to
    get more context on why the error happened.

    Do note that this error-reporting mechanism only reports the top-level error
    message, not any source information embedded in the original Rust error
    type. If you want more detailed information for debugging purposes, use the
    logging interface.

    Args:
        length:
            The length of the buffer to allocate for the error message. If the
            error message is longer than this, it will be truncated.

    Returns:
        A string containing the error message, or None if there is no error
        message.

    Raises:
        RuntimeError:
            If the error message could not be retrieved.
    """
    buffer = ffi.new("char[]", length)
    ret: int = lib.pactffi_get_error_message(buffer, length)

    if ret >= 0:
        # While the documentation says that the return value is the number of bytes
        # written, the actually return value is always 0 on success.
        if msg := ffi.string(buffer):
            if isinstance(msg, bytes):
                return msg.decode("utf-8")
            return msg
        return None
    if ret == -1:
        msg = "The provided buffer is a null pointer."
    elif ret == -2:  # noqa: PLR2004
        # Instead of returning an error here, we call the function again with a
        # larger buffer.
        return get_error_message(length * 32)
    elif ret == -3:  # noqa: PLR2004
        msg = "The write failed for some other reason."
    elif ret == -4:  # noqa: PLR2004
        msg = "The error message had an interior NULL."
    else:
        msg = "An unknown error occurred."
    raise RuntimeError(msg)


def log_to_stdout(level_filter: LevelFilter) -> int:
    """
    Convenience function to direct all logging to stdout.

    [Rust `pactffi_log_to_stdout`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_log_to_stdout)
    """
    raise NotImplementedError


def log_to_stderr(level_filter: LevelFilter | str = LevelFilter.ERROR) -> None:
    """
    Convenience function to direct all logging to stderr.

    [Rust
    `pactffi_log_to_stderr`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_log_to_stderr)

    Args:
        level_filter:
            The level of logs to filter to. If a string is given, it must match
            one of the [`LevelFilter`][pact.v3.ffi.LevelFilter] values (case
            insensitive).

    Raises:
        RuntimeError:
            If there was an error setting the logger.
    """
    if isinstance(level_filter, str):
        level_filter = LevelFilter[level_filter.upper()]
    ret: int = lib.pactffi_log_to_stderr(level_filter.value)
    if ret != 0:
        msg = "There was an unknown error setting the logger."
        raise RuntimeError(msg)


def log_to_file(file_name: str, level_filter: LevelFilter) -> int:
    """
    Convenience function to direct all logging to a file.

    [Rust
    `pactffi_log_to_file`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_log_to_file)

    # Safety

    This function will fail if the file_name pointer is invalid or does not
    point to a NULL terminated string.
    """
    raise NotImplementedError


def log_to_buffer(level_filter: LevelFilter | str = LevelFilter.ERROR) -> None:
    """
    Convenience function to direct all logging to a task local memory buffer.

    [Rust `pactffi_log_to_buffer`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_log_to_buffer)

    Raises:
        RuntimeError:
            If there was an error setting the logger.
    """
    if isinstance(level_filter, str):
        level_filter = LevelFilter[level_filter.upper()]
    ret: int = lib.pactffi_log_to_buffer(level_filter.value)
    if ret != 0:
        msg = "There was an unknown error setting the logger."
        raise RuntimeError(msg)


def logger_init() -> None:
    """
    Initialize the FFI logger with no sinks.

    [Rust `pactffi_logger_init`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_logger_init)

    This initialized logger does nothing until `pactffi_logger_apply` has been called.

    # Usage

    ```c
    pactffi_logger_init();
    ```

    # Safety

    This function is always safe to call.
    """
    raise NotImplementedError


def logger_attach_sink(sink_specifier: str, level_filter: LevelFilter) -> int:
    """
    Attach an additional sink to the thread-local logger.

    [Rust
    `pactffi_logger_attach_sink`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_logger_attach_sink)

    This logger does nothing until `pactffi_logger_apply` has been called.

    Types of sinks can be specified:

    - stdout (`pactffi_logger_attach_sink("stdout", LevelFilter_Info)`)
    - stderr (`pactffi_logger_attach_sink("stderr", LevelFilter_Debug)`)
    - file w/ file path (`pactffi_logger_attach_sink("file /some/file/path",
      LevelFilter_Trace)`)
    - buffer (`pactffi_logger_attach_sink("buffer", LevelFilter_Debug)`)

    # Usage

    ```c
    int result = pactffi_logger_attach_sink("file /some/file/path", LogLevel_Filter);
    ```

    # Error Handling

    The return error codes are as follows:

    - `-1`: Can't set logger (applying the logger failed, perhaps because one is
      applied already).
    - `-2`: No logger has been initialized (call `pactffi_logger_init` before
      any other log function).
    - `-3`: The sink specifier was not UTF-8 encoded.
    - `-4`: The sink type specified is not a known type (known types: "stdout",
      "stderr", or "file /some/path").
    - `-5`: No file path was specified in a file-type sink specification.
    - `-6`: Opening a sink to the specified file path failed (check
      permissions).

    # Safety

    This function checks the validity of the passed-in sink specifier, and
    errors out if the specifier isn't valid UTF-8. Passing in an invalid or NULL
    pointer will result in undefined behaviour.
    """
    raise NotImplementedError


def logger_apply() -> int:
    """
    Apply the previously configured sinks and levels to the program.

    [Rust
    `pactffi_logger_apply`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_logger_apply)

    If no sinks have been setup, will set the log level to info and the target
    to standard out.

    This function will install a global tracing subscriber. Any attempts to
    modify the logger after the call to `logger_apply` will fail.
    """
    raise NotImplementedError


def fetch_log_buffer(log_id: str) -> str:
    """
    Fetch the in-memory logger buffer contents.

    [Rust
    `pactffi_fetch_log_buffer`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_fetch_log_buffer)

    This will only have any contents if the `buffer` sink has been configured to
    log to. The contents will be allocated on the heap and will need to be freed
    with `pactffi_string_delete`.

    Fetches the logs associated with the provided identifier, or uses the
    "global" one if the identifier is not specified (i.e. NULL).

    Returns a NULL pointer if the buffer can't be fetched. This can occur is
    there is not sufficient memory to make a copy of the contents or the buffer
    contains non-UTF-8 characters.

    # Safety

    This function will fail if the log_id pointer is invalid or does not point
    to a NULL terminated string.
    """
    raise NotImplementedError


def parse_pact_json(json: str) -> Pact:
    """
    Parses the provided JSON into a Pact model.

    [Rust
    `pactffi_parse_pact_json`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_parse_pact_json)

    The returned Pact model must be freed with the `pactffi_pact_model_delete`
    function when no longer needed.

    # Error Handling

    This function will return a NULL pointer if passed a NULL pointer or if an
    error occurs.
    """
    raise NotImplementedError


def pact_model_delete(pact: Pact) -> None:
    """
    Frees the memory used by the Pact model.

    [Rust `pactffi_pact_model_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_model_delete)
    """
    raise NotImplementedError


def pact_model_interaction_iterator(pact: Pact) -> PactInteractionIterator:
    """
    Returns an iterator over all the interactions in the Pact.

    [Rust
    `pactffi_pact_model_interaction_iterator`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_model_interaction_iterator)

    The iterator will have to be deleted using the
    `pactffi_pact_interaction_iter_delete` function. The iterator will contain a
    copy of the interactions, so it will not be affected but mutations to the
    Pact model and will still function if the Pact model is deleted.

    # Safety This function is safe as long as the Pact pointer is a valid
    pointer.

    # Errors On any error, this function will return a NULL pointer.
    """
    raise NotImplementedError


def pact_spec_version(pact: Pact) -> PactSpecification:
    """
    Returns the Pact specification enum that the Pact is for.

    [Rust `pactffi_pact_spec_version`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_spec_version)
    """
    raise NotImplementedError


def pact_interaction_delete(interaction: PactInteraction) -> None:
    """
    Frees the memory used by the Pact interaction model.

    [Rust `pactffi_pact_interaction_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_interaction_delete)
    """
    raise NotImplementedError


def async_message_new() -> AsynchronousMessage:
    """
    Get a mutable pointer to a newly-created default message on the heap.

    [Rust `pactffi_async_message_new`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_new)

    # Safety

    This function is safe.

    # Error Handling

    Returns NULL on error.
    """
    raise NotImplementedError


def async_message_delete(message: AsynchronousMessage) -> None:
    """
    Destroy the `AsynchronousMessage` being pointed to.

    [Rust `pactffi_async_message_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_delete)
    """
    lib.pactffi_async_message_delete(message._ptr)


def async_message_get_contents(message: AsynchronousMessage) -> MessageContents | None:
    """
    Get the message contents of an `AsynchronousMessage` as a `MessageContents` pointer.

    [Rust
    `pactffi_async_message_get_contents`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_get_contents)

    If the message contents are missing, this function will return `None`.
    """
    return MessageContents(lib.pactffi_async_message_get_contents(message._ptr))


def async_message_generate_contents(
    message: AsynchronousMessage,
) -> MessageContents | None:
    """
    Get the message contents of an `AsynchronousMessage` as a `MessageContents` pointer.

    This function differs from `async_message_get_contents` in
    that it will process the message contents for any generators or matchers
    that are present in the message in order to generate the actual message
    contents as would be received by the consumer.

    [Rust
    `pactffi_async_message_generate_contents`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_generate_contents)

    If the message contents are missing, this function will return `None`.
    """
    return MessageContents(
        lib.pactffi_async_message_generate_contents(message._ptr),
        owned=False,
    )


def async_message_get_contents_str(message: AsynchronousMessage) -> str:
    """
    Get the message contents of an `AsynchronousMessage` in string form.

    [Rust `pactffi_async_message_get_contents_str`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_get_contents_str)

    # Safety

    The returned string must be deleted with `pactffi_string_delete`.

    The returned string can outlive the message.

    # Error Handling

    If the message is NULL, returns NULL. If the body of the message
    is missing, then this function also returns NULL. This means there's
    no mechanism to differentiate with this function call alone between
    a NULL message and a missing message body.
    """
    raise NotImplementedError


def async_message_set_contents_str(
    message: AsynchronousMessage,
    contents: str,
    content_type: str,
) -> None:
    """
    Sets the contents of the message as a string.

    [Rust
    `pactffi_async_message_set_contents_str`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_set_contents_str)

    - `message` - the message to set the contents for
    - `contents` - pointer to contents to copy from. Must be a valid
      NULL-terminated UTF-8 string pointer.
    - `content_type` - pointer to the NULL-terminated UTF-8 string containing
      the content type of the data.

    # Safety

    The message contents and content type must either be NULL pointers, or point
    to valid UTF-8 encoded NULL-terminated strings. Otherwise behaviour is
    undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the message contents as null.
    If the content type is a null pointer, or can't be parsed, it will set the
    content type as unknown.
    """
    raise NotImplementedError


def async_message_get_contents_length(message: AsynchronousMessage) -> int:
    """
    Get the length of the contents of a `AsynchronousMessage`.

    [Rust
    `pactffi_async_message_get_contents_length`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_get_contents_length)

    # Safety

    This function is safe.

    # Error Handling

    If the message is NULL, returns 0. If the body of the request is missing,
    then this function also returns 0.
    """
    raise NotImplementedError


def async_message_get_contents_bin(message: AsynchronousMessage) -> str:
    """
    Get the contents of an `AsynchronousMessage` as bytes.

    [Rust
    `pactffi_async_message_get_contents_bin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_get_contents_bin)

    # Safety

    The number of bytes in the buffer will be returned by
    `pactffi_async_message_get_contents_length`. It is safe to use the pointer
    while the message is not deleted or changed. Using the pointer after the
    message is mutated or deleted may lead to undefined behaviour.

    # Error Handling

    If the message is NULL, returns NULL. If the body of the message is missing,
    then this function also returns NULL.
    """
    raise NotImplementedError


def async_message_set_contents_bin(
    message: AsynchronousMessage,
    contents: str,
    len: int,
    content_type: str,
) -> None:
    """
    Sets the contents of the message as an array of bytes.

    [Rust
    `pactffi_async_message_set_contents_bin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_set_contents_bin)

    * `message` - the message to set the contents for
    * `contents` - pointer to contents to copy from
    * `len` - number of bytes to copy from the contents pointer
    * `content_type` - pointer to the NULL-terminated UTF-8 string containing
      the content type of the data.

    # Safety

    The contents pointer must be valid for reads of `len` bytes, and it must be
    properly aligned and consecutive. Otherwise behaviour is undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the message contents as null.
    If the content type is a null pointer, or can't be parsed, it will set the
    content type as unknown.
    """
    raise NotImplementedError


def async_message_get_description(message: AsynchronousMessage) -> str:
    r"""
    Get a copy of the description.

    [Rust
    `pactffi_async_message_get_description`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_get_description)

    Raises:
        RuntimeError:
            If the description cannot be retrieved.
    """
    ptr = lib.pactffi_async_message_get_description(message._ptr)
    if ptr == ffi.NULL:
        msg = "Unable to get the description from the message."
        raise RuntimeError(msg)
    return OwnedString(ptr)


def async_message_set_description(
    message: AsynchronousMessage,
    description: str,
) -> int:
    """
    Write the `description` field on the `AsynchronousMessage`.

    [Rust `pactffi_async_message_set_description`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_set_description)

    # Safety

    `description` must contain valid UTF-8. Invalid UTF-8
    will be replaced with U+FFFD REPLACEMENT CHARACTER.

    This function will only reallocate if the new string
    does not fit in the existing buffer.

    # Error Handling

    Errors will be reported with a non-zero return value.
    """
    raise NotImplementedError


def async_message_get_provider_state(
    message: AsynchronousMessage,
    index: int,
) -> ProviderState:
    r"""
    Get a copy of the provider state at the given index from this message.

    [Rust
    `pactffi_async_message_get_provider_state`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_get_provider_state)

    Raises:
        RuntimeError:
            If the provider state cannot be retrieved.
    """
    ptr = lib.pactffi_async_message_get_provider_state(message._ptr, index)
    if ptr == ffi.NULL:
        msg = "Unable to get the provider state from the message."
        raise RuntimeError(msg)
    return ProviderState(ptr)


def async_message_get_provider_state_iter(
    message: AsynchronousMessage,
) -> ProviderStateIterator:
    """
    Get an iterator over provider states.

    [Rust `pactffi_async_message_get_provider_state_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_async_message_get_provider_state_iter)

    # Safety

    The underlying data must not change during iteration.
    """
    return ProviderStateIterator(
        lib.pactffi_async_message_get_provider_state_iter(message._ptr)
    )


def consumer_get_name(consumer: Consumer) -> str:
    r"""
    Get a copy of this consumer's name.

    [Rust `pactffi_consumer_get_name`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_consumer_get_name)

    The copy must be deleted with `pactffi_string_delete`.

    # Usage

    ```c
    // Assuming `file_name` and `json_str` are already defined.

    MessagePact *message_pact = pactffi_message_pact_new_from_json(file_name, json_str);
    if (message_pact == NULLPTR) {
        // handle error.
    }

    Consumer *consumer = pactffi_message_pact_get_consumer(message_pact);
    if (consumer == NULLPTR) {
        // handle error.
    }

    char *name = pactffi_consumer_get_name(consumer);
    if (name == NULL) {
        // handle error.
    }

    printf("%s\n", name);

    pactffi_string_delete(name);
    ```

    # Errors

    This function will fail if it is passed a NULL pointer,
    or the Rust string contains an embedded NULL byte.
    In the case of error, a NULL pointer will be returned.
    """
    raise NotImplementedError


def pact_get_consumer(pact: Pact) -> Consumer:
    """
    Get the consumer from a Pact.

    This returns a copy of the consumer model, and needs to be cleaned up with
    `pactffi_pact_consumer_delete` when no longer required.

    [Rust
    `pactffi_pact_get_consumer`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_get_consumer)

    # Errors

    This function will fail if it is passed a NULL pointer. In the case of
    error, a NULL pointer will be returned.
    """
    raise NotImplementedError


def pact_consumer_delete(consumer: Consumer) -> None:
    """
    Frees the memory used by the Pact consumer.

    [Rust `pactffi_pact_consumer_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_consumer_delete)
    """
    raise NotImplementedError


def message_contents_delete(contents: MessageContents) -> None:
    """
    Delete the message contents instance.

    This should only be called on a message contents that require deletion.
    The function creating the message contents should document whether it
    requires deletion.

    Deleting a message content which is associated with an interaction
    will result in undefined behaviour.

    [Rust `pactffi_message_contents_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_message_contents_delete)
    """
    lib.pactffi_message_contents_delete(contents._ptr)


def message_contents_get_contents_str(contents: MessageContents) -> str | None:
    """
    Get the message contents in string form.

    [Rust `pactffi_message_contents_get_contents_str`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_message_contents_get_contents_str)

    If the message has no contents or contain invalid UTF-8 characters, this
    function will return `None`.
    """
    ptr = lib.pactffi_message_contents_get_contents_str(contents._ptr)
    if ptr == ffi.NULL:
        return None
    return OwnedString(ptr)


def message_contents_set_contents_str(
    contents: MessageContents,
    contents_str: str,
    content_type: str,
) -> None:
    """
    Sets the contents of the message as a string.

    [Rust
    `pactffi_message_contents_set_contents_str`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_message_contents_set_contents_str)

    * `contents` - the message contents to set the contents for
    * `contents_str` - pointer to contents to copy from. Must be a valid
      NULL-terminated UTF-8 string pointer.
    * `content_type` - pointer to the NULL-terminated UTF-8 string containing
      the content type of the data.

    # Safety

    The message contents and content type must either be NULL pointers, or point
    to valid UTF-8 encoded NULL-terminated strings. Otherwise behaviour is
    undefined.

    # Error Handling

    If the contents string is a NULL pointer, it will set the message contents
    as null. If the content type is a null pointer, or can't be parsed, it will
    set the content type as unknown.
    """
    raise NotImplementedError


def message_contents_get_contents_length(contents: MessageContents) -> int:
    """
    Get the length of the message contents.

    [Rust `pactffi_message_contents_get_contents_length`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_message_contents_get_contents_length)

    If the message has not contents, this function will return 0.
    """
    return lib.pactffi_message_contents_get_contents_length(contents._ptr)


def message_contents_get_contents_bin(contents: MessageContents) -> bytes | None:
    """
    Get the contents of a message as a pointer to an array of bytes.

    [Rust
    `pactffi_message_contents_get_contents_bin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_message_contents_get_contents_bin)

    If the message has no contents, this function will return `None`.
    """
    ptr = lib.pactffi_message_contents_get_contents_bin(contents._ptr)
    if ptr == ffi.NULL:
        return None
    return ffi.buffer(
        ptr,
        lib.pactffi_message_contents_get_contents_length(contents._ptr),
    )[:]


def message_contents_set_contents_bin(
    contents: MessageContents,
    contents_bin: str,
    len: int,
    content_type: str,
) -> None:
    """
    Sets the contents of the message as an array of bytes.

    [Rust
    `pactffi_message_contents_set_contents_bin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_message_contents_set_contents_bin)

    * `message` - the message contents to set the contents for
    * `contents_bin` - pointer to contents to copy from
    * `len` - number of bytes to copy from the contents pointer
    * `content_type` - pointer to the NULL-terminated UTF-8 string containing
      the content type of the data.

    # Safety

    The contents pointer must be valid for reads of `len` bytes, and it must be
    properly aligned and consecutive. Otherwise behaviour is undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the message contents as null.
    If the content type is a null pointer, or can't be parsed, it will set the
    content type as unknown.
    """
    raise NotImplementedError


def message_contents_get_metadata_iter(
    contents: MessageContents,
) -> MessageMetadataIterator:
    r"""
    Get an iterator over the metadata of a message.

    [Rust
    `pactffi_message_contents_get_metadata_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_message_contents_get_metadata_iter)

    # Safety

    This iterator carries a pointer to the message contents, and must not
    outlive the message.

    The message metadata also must not be modified during iteration. If it is,
    the old iterator must be deleted and a new iterator created.

    Raises:
        RuntimeError:
            If the metadata iterator cannot be retrieved.
    """
    ptr = lib.pactffi_message_contents_get_metadata_iter(contents._ptr)
    if ptr == ffi.NULL:
        msg = "Unable to get the metadata iterator from the message contents."
        raise RuntimeError(msg)
    return MessageMetadataIterator(ptr)


def message_contents_get_matching_rule_iter(
    contents: MessageContents,
    category: MatchingRuleCategory,
) -> MatchingRuleCategoryIterator:
    r"""
    Get an iterator over the matching rules for a category of a message.

    [Rust
    `pactffi_message_contents_get_matching_rule_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_message_contents_get_matching_rule_iter)

    The returned pointer must be deleted with
    `pactffi_matching_rules_iter_delete` when done with it.

    Note that there could be multiple matching rules for the same key, so this
    iterator will sequentially return each rule with the same key.

    For sample, given the following rules:

    ```
    "$.a" => Type,
    "$.b" => Regex("\\d+"), Number
    ```

    This iterator will return a sequence of 3 values:

    - `("$.a", Type)`
    - `("$.b", Regex("\d+"))`
    - `("$.b", Number)`

    # Safety

    The iterator contains a copy of the data, so is safe to use when the message
    or message contents has been deleted.

    # Error Handling

    On failure, this function will return a NULL pointer.
    """
    return MatchingRuleCategoryIterator(
        lib.pactffi_message_contents_get_matching_rule_iter(contents._ptr, category)
    )


def request_contents_get_matching_rule_iter(
    request: HttpRequest,
    category: MatchingRuleCategory,
) -> MatchingRuleCategoryIterator:
    r"""
    Get an iterator over the matching rules for a category of an HTTP request.

    [Rust `pactffi_request_contents_get_matching_rule_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_request_contents_get_matching_rule_iter)

    The returned pointer must be deleted with
    `pactffi_matching_rules_iter_delete` when done with it.

    For sample, given the following rules:

    ```
    "$.a" => Type,
    "$.b" => Regex("\d+"), Number
    ```

    This iterator will return a sequence of 3 values:

    - `("$.a", Type)`
    - `("$.b", Regex("\d+"))`
    - `("$.b", Number)`

    # Safety

    The iterator contains a copy of the data, so is safe to use when the
    interaction or request contents has been deleted.

    # Error Handling

    On failure, this function will return a NULL pointer.
    """
    raise NotImplementedError


def response_contents_get_matching_rule_iter(
    response: HttpResponse,
    category: MatchingRuleCategory,
) -> MatchingRuleCategoryIterator:
    r"""
    Get an iterator over the matching rules for a category of an HTTP response.

    [Rust `pactffi_response_contents_get_matching_rule_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_response_contents_get_matching_rule_iter)

    The returned pointer must be deleted with
    `pactffi_matching_rules_iter_delete` when done with it.

    For sample, given the following rules:

    ```
    "$.a" => Type,
    "$.b" => Regex("\d+"), Number
    ```

    This iterator will return a sequence of 3 values:

    - `("$.a", Type)`
    - `("$.b", Regex("\d+"))`
    - `("$.b", Number)`

    # Safety

    The iterator contains a copy of the data, so is safe to use when the
    interaction or response contents has been deleted.

    # Error Handling

    On failure, this function will return a NULL pointer.
    """
    raise NotImplementedError


def message_contents_get_generators_iter(
    contents: MessageContents,
    category: GeneratorCategory,
) -> GeneratorCategoryIterator:
    """
    Get an iterator over the generators for a category of a message.

    [Rust
    `pactffi_message_contents_get_generators_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_message_contents_get_generators_iter)

    # Safety

    The iterator contains a copy of the data, so is safe to use when the message
    or message contents has been deleted.

    Raises:
        RuntimeError:
            If the generators iterator cannot be retrieved.
    """
    ptr = lib.pactffi_message_contents_get_generators_iter(contents._ptr, category)
    if ptr == ffi.NULL:
        msg = "Unable to get the generators iterator from the message contents."
        raise RuntimeError(msg)
    return GeneratorCategoryIterator(ptr)


def request_contents_get_generators_iter(
    request: HttpRequest,
    category: GeneratorCategory,
) -> GeneratorCategoryIterator:
    """
    Get an iterator over the generators for a category of an HTTP request.

    [Rust
    `pactffi_request_contents_get_generators_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_request_contents_get_generators_iter)

    The returned pointer must be deleted with `pactffi_generators_iter_delete`
    when done with it.

    # Safety

    The iterator contains a copy of the data, so is safe to use when the
    interaction or request contents has been deleted.

    # Error Handling

    On failure, this function will return a NULL pointer.
    """
    raise NotImplementedError


def response_contents_get_generators_iter(
    response: HttpResponse,
    category: GeneratorCategory,
) -> GeneratorCategoryIterator:
    """
    Get an iterator over the generators for a category of an HTTP response.

    [Rust
    `pactffi_response_contents_get_generators_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_response_contents_get_generators_iter)

    The returned pointer must be deleted with `pactffi_generators_iter_delete`
    when done with it.

    # Safety

    The iterator contains a copy of the data, so is safe to use when the
    interaction or response contents has been deleted.

    # Error Handling

    On failure, this function will return a NULL pointer.
    """
    raise NotImplementedError


def parse_matcher_definition(expression: str) -> MatchingRuleDefinitionResult:
    """
    Parse a matcher definition string into a MatchingRuleDefinition.

    The MatchingRuleDefinition contains the example value, and matching rules and
    any generator.

    [Rust
    `pactffi_parse_matcher_definition`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_parse_matcher_definition)

    The following are examples of matching rule definitions:

    * `matching(type,'Name')` - type matcher with string value 'Name'
    * `matching(number,100)` - number matcher
    * `matching(datetime, 'yyyy-MM-dd','2000-01-01')` - datetime matcher with
      format string

    See [Matching Rule definition
    expressions](https://docs.rs/pact_models/latest/pact_models/matchingrules/expressions/index.html).

    The returned value needs to be freed up with the
    `pactffi_matcher_definition_delete` function.

    # Errors If the expression is invalid, the MatchingRuleDefinition error will
    be set. You can check for this value with the
    `pactffi_matcher_definition_error` function.

    # Safety

    This function is safe if the expression is a valid NULL terminated string
    pointer.
    """
    raise NotImplementedError


def matcher_definition_error(definition: MatchingRuleDefinitionResult) -> str:
    """
    Returns any error message from parsing a matching definition expression.

    If there is no error, it will return a NULL pointer, otherwise returns the
    error message as a NULL-terminated string. The returned string must be freed
    using the `pactffi_string_delete` function once done with it.

    [Rust
    `pactffi_matcher_definition_error`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matcher_definition_error)
    """
    raise NotImplementedError


def matcher_definition_value(definition: MatchingRuleDefinitionResult) -> str:
    """
    Returns the value from parsing a matching definition expression.

    If there was an error, it will return a NULL pointer, otherwise returns the
    value as a NULL-terminated string. The returned string must be freed using
    the `pactffi_string_delete` function once done with it.

    [Rust
    `pactffi_matcher_definition_value`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matcher_definition_value)

    Note that different expressions values can have types other than a string.
    Use `pactffi_matcher_definition_value_type` to get the actual type of the
    value. This function will always return the string representation of the
    value.
    """
    raise NotImplementedError


def matcher_definition_delete(definition: MatchingRuleDefinitionResult) -> None:
    """
    Frees the memory used by the result of parsing the matching definition expression.

    [Rust `pactffi_matcher_definition_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matcher_definition_delete)
    """
    raise NotImplementedError


def matcher_definition_generator(definition: MatchingRuleDefinitionResult) -> Generator:
    """
    Returns the generator from parsing a matching definition expression.

    If there was an error or there is no associated generator, it will return a
    NULL pointer, otherwise returns the generator as a pointer.

    [Rust
    `pactffi_matcher_definition_generator`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matcher_definition_generator)

    The generator pointer will be a valid pointer as long as
    `pactffi_matcher_definition_delete` has not been called on the definition.
    Using the generator pointer after the definition has been deleted will
    result in undefined behaviour.
    """
    raise NotImplementedError


def matcher_definition_value_type(
    definition: MatchingRuleDefinitionResult,
) -> ExpressionValueType:
    """
    Returns the type of the value from parsing a matching definition expression.

    If there was an error parsing the expression, it will return Unknown.

    [Rust
    `pactffi_matcher_definition_value_type`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matcher_definition_value_type)
    """
    raise NotImplementedError


def matching_rule_iter_delete(iter: MatchingRuleIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust `pactffi_matching_rule_iter_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matching_rule_iter_delete)
    """
    raise NotImplementedError


def matcher_definition_iter(
    definition: MatchingRuleDefinitionResult,
) -> MatchingRuleIterator:
    """
    Returns an iterator over the matching rules from the parsed definition.

    The iterator needs to be deleted with the
    `pactffi_matching_rule_iter_delete` function once done with it.

    [Rust
    `pactffi_matcher_definition_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matcher_definition_iter)

    If there was an error parsing the expression, this function will return a
    NULL pointer.
    """
    raise NotImplementedError


def matching_rule_iter_next(iter: MatchingRuleIterator) -> MatchingRuleResult:
    """
    Get the next matching rule or reference from the iterator.

    As the values returned are owned by the iterator, they do not need to be
    deleted but will be cleaned up when the iterator is deleted.

    [Rust
    `pactffi_matching_rule_iter_next`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matching_rule_iter_next)

    Will return a NULL pointer when the iterator has advanced past the end of
    the list.

    # Safety

    This function is safe.

    # Error Handling

    This function will return a NULL pointer if passed a NULL pointer or if an
    error occurs.
    """
    raise NotImplementedError


def matching_rule_id(rule_result: MatchingRuleResult) -> int:
    """
    Return the ID of the matching rule.

    [Rust
    `pactffi_matching_rule_id`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matching_rule_id)

    The ID corresponds to the following rules:

    | Rule | ID |
    | ---- | -- |
    | Equality | 1 |
    | Regex | 2 |
    | Type | 3 |
    | MinType | 4 |
    | MaxType | 5 |
    | MinMaxType | 6 |
    | Timestamp | 7 |
    | Time | 8 |
    | Date | 9 |
    | Include | 10 |
    | Number | 11 |
    | Integer | 12 |
    | Decimal | 13 |
    | Null | 14 |
    | ContentType | 15 |
    | ArrayContains | 16 |
    | Values | 17 |
    | Boolean | 18 |
    | StatusCode | 19 |
    | NotEmpty | 20 |
    | Semver | 21 |
    | EachKey | 22 |
    | EachValue | 23 |

    # Safety

    This function is safe as long as the MatchingRuleResult pointer is a valid
    pointer and the iterator has not been deleted.
    """
    raise NotImplementedError


def matching_rule_value(rule_result: MatchingRuleResult) -> str:
    """
    Returns the associated value for the matching rule.

    If the matching rule does not have an associated value, will return a NULL
    pointer.

    [Rust
    `pactffi_matching_rule_value`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matching_rule_value)

    The associated values for the rules are:

    | Rule | ID | VALUE |
    | ---- | -- | ----- |
    | Equality | 1 | NULL |
    | Regex | 2 | Regex value |
    | Type | 3 | NULL |
    | MinType | 4 | Minimum value |
    | MaxType | 5 | Maximum value |
    | MinMaxType | 6 | "min:max" |
    | Timestamp | 7 | Format string |
    | Time | 8 | Format string |
    | Date | 9 | Format string |
    | Include | 10 | String value |
    | Number | 11 | NULL |
    | Integer | 12 | NULL |
    | Decimal | 13 | NULL |
    | Null | 14 | NULL |
    | ContentType | 15 | Content type |
    | ArrayContains | 16 | NULL |
    | Values | 17 | NULL |
    | Boolean | 18 | NULL |
    | StatusCode | 19 | NULL |
    | NotEmpty | 20 | NULL |
    | Semver | 21 | NULL |
    | EachKey | 22 | NULL |
    | EachValue | 23 | NULL |

    Will return a NULL pointer if the matching rule was a reference or does not
    have an associated value.

    # Safety

    This function is safe as long as the MatchingRuleResult pointer is a valid
    pointer and the iterator it came from has not been deleted.
    """
    raise NotImplementedError


def matching_rule_pointer(rule_result: MatchingRuleResult) -> MatchingRule:
    """
    Returns the matching rule pointer for the matching rule.

    Will return a NULL pointer if the matching rule result was a reference.

    [Rust
    `pactffi_matching_rule_pointer`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matching_rule_pointer)

    # Safety

    This function is safe as long as the MatchingRuleResult pointer is a valid
    pointer and the iterator it came from has not been deleted.
    """
    raise NotImplementedError


def matching_rule_reference_name(rule_result: MatchingRuleResult) -> str:
    """
    Return any matching rule reference to a attribute by name.

    This is when the matcher should be configured to match the type of a
    structure. I.e.,

    [Rust
    `pactffi_matching_rule_reference_name`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matching_rule_reference_name)

    ```json
    {
      "pact:match": "eachValue(matching($'person'))",
      "person": {
        "name": "Fred",
        "age": 100
      }
    }
    ```

    Will return a NULL pointer if the matching rule was not a reference.

    # Safety

    This function is safe as long as the MatchingRuleResult pointer is a valid
    pointer and the iterator has not been deleted.
    """
    raise NotImplementedError


def validate_datetime(value: str, format: str) -> None:
    """
    Validates the date/time value against the date/time format string.

    [Rust
    `pactffi_validate_datetime`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_validate_datetime)

    Raises:
        ValueError:
            If the value is not a valid date/time for the format string.

        RuntimeError:
            For any other error.
    """
    ret = lib.pactffi_validate_datetime(value.encode(), format.encode())
    if ret == 0:
        return
    if ret == 1:
        msg = f"Invalid datetime value {value!r}' for format {format!r}"
        raise ValueError(msg)
    if ret == 2:  # noqa: PLR2004
        msg = f"Panic while validating datetime value: {get_error_message()}"
    else:
        msg = f"Unknown error while validating datetime value: {ret}"
    raise RuntimeError(msg)


def generator_to_json(generator: Generator) -> str:
    """
    Get the JSON form of the generator.

    [Rust
    `pactffi_generator_to_json`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_generator_to_json)

    The returned string must be deleted with `pactffi_string_delete`.

    # Safety

    This function will fail if it is passed a NULL pointer, or the owner of the
    generator has been deleted.
    """
    return OwnedString(lib.pactffi_generator_to_json(generator._ptr))


def generator_generate_string(generator: Generator, context_json: str) -> str:
    """
    Generate a string value using the provided generator.

    An optional JSON payload containing any generator context ca be given. The
    context value is used for generators like `MockServerURL` (which should
    contain details about the running mock server) and `ProviderStateGenerator`
    (which should be the values returned from the Provider State callback
    function).

    [Rust
    `pactffi_generator_generate_string`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_generator_generate_string)

    If anything goes wrong, it will return a NULL pointer.
    """
    ptr = lib.pactffi_generator_generate_string(
        generator._ptr,
        context_json.encode("utf-8"),
    )
    s = ffi.string(ptr)
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    return s


def generator_generate_integer(generator: Generator, context_json: str) -> int:
    """
    Generate an integer value using the provided generator.

    An optional JSON payload containing any generator context can be given. The
    context value is used for generators like `ProviderStateGenerator` (which
    should be the values returned from the Provider State callback function).

    [Rust
    `pactffi_generator_generate_integer`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_generator_generate_integer)

    If anything goes wrong or the generator is not a type that can generate an
    integer value, it will return a zero value.
    """
    return lib.pactffi_generator_generate_integer(
        generator._ptr,
        context_json.encode("utf-8"),
    )


def generators_iter_delete(iter: GeneratorCategoryIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust
    `pactffi_generators_iter_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_generators_iter_delete)
    """
    lib.pactffi_generators_iter_delete(iter._ptr)


def generators_iter_next(iter: GeneratorCategoryIterator) -> GeneratorKeyValuePair:
    """
    Get the next path and generator out of the iterator, if possible.

    [Rust
    `pactffi_generators_iter_next`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_generators_iter_next)

    The returned pointer must be deleted with
    `pactffi_generator_iter_pair_delete`.

    Raises:
        StopIteration:
            If the iterator has reached the end.
    """
    ptr = lib.pactffi_generators_iter_next(iter._ptr)
    if ptr == ffi.NULL:
        raise StopIteration
    return GeneratorKeyValuePair(ptr)


def generators_iter_pair_delete(pair: GeneratorKeyValuePair) -> None:
    """
    Free a pair of key and value returned from `pactffi_generators_iter_next`.

    [Rust
    `pactffi_generators_iter_pair_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_generators_iter_pair_delete)
    """
    lib.pactffi_generators_iter_pair_delete(pair._ptr)


def sync_http_new() -> SynchronousHttp:
    """
    Get a mutable pointer to a newly-created default interaction on the heap.

    [Rust `pactffi_sync_http_new`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_new)

    # Safety

    This function is safe.

    # Error Handling

    Returns NULL on error.
    """
    raise NotImplementedError


def sync_http_delete(interaction: SynchronousHttp) -> None:
    """
    Destroy the `SynchronousHttp` interaction being pointed to.

    [Rust
    `pactffi_sync_http_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_delete)
    """
    lib.pactffi_sync_http_delete(interaction)


def sync_http_get_request(interaction: SynchronousHttp) -> HttpRequest:
    """
    Get the request of a `SynchronousHttp` interaction.

    [Rust
    `pactffi_sync_http_get_request`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_get_request)

    # Safety

    The data pointed to by the pointer this function returns will be deleted
    when the interaction is deleted. Trying to use if after the interaction is
    deleted will result in undefined behaviour.

    # Error Handling

    If the interaction is NULL, returns NULL.
    """
    raise NotImplementedError


def sync_http_get_request_contents(interaction: SynchronousHttp) -> str | None:
    """
    Get the request contents of a `SynchronousHttp` interaction in string form.

    [Rust
    `pactffi_sync_http_get_request_contents`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_get_request_contents)

    Note that this function will return `None` if either the body is missing or
    is `null`.
    """
    ptr = lib.pactffi_sync_http_get_request_contents(interaction._ptr)
    if ptr == ffi.NULL:
        return None
    return OwnedString(ptr)


def sync_http_set_request_contents(
    interaction: SynchronousHttp,
    contents: str,
    content_type: str,
) -> None:
    """
    Sets the request contents of the interaction.

    [Rust
    `pactffi_sync_http_set_request_contents`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_set_request_contents)

    - `interaction` - the interaction to set the request contents for
    - `contents` - pointer to contents to copy from. Must be a valid
      NULL-terminated UTF-8 string pointer.
    - `content_type` - pointer to the NULL-terminated UTF-8 string containing
      the content type of the data.

    # Safety

    The request contents and content type must either be NULL pointers, or point
    to valid UTF-8 encoded NULL-terminated strings. Otherwise behaviour is
    undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the request contents as null.
    If the content type is a null pointer, or can't be parsed, it will set the
    content type as unknown.
    """
    raise NotImplementedError


def sync_http_get_request_contents_length(interaction: SynchronousHttp) -> int:
    """
    Get the length of the request contents of a `SynchronousHttp` interaction.

    [Rust
    `pactffi_sync_http_get_request_contents_length`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_get_request_contents_length)

    This function will return 0 if the body is missing.
    """
    return lib.pactffi_sync_http_get_request_contents_length(interaction._ptr)


def sync_http_get_request_contents_bin(interaction: SynchronousHttp) -> bytes | None:
    """
    Get the request contents of a `SynchronousHttp` interaction as bytes.

    [Rust
    `pactffi_sync_http_get_request_contents_bin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_get_request_contents_bin)

    Note that this function will return `None` if either the body is missing or
    is `null`.
    """
    ptr = lib.pactffi_sync_http_get_request_contents_bin(interaction._ptr)
    if ptr == ffi.NULL:
        return None
    return ffi.buffer(
        ptr,
        sync_http_get_request_contents_length(interaction),
    )[:]


def sync_http_set_request_contents_bin(
    interaction: SynchronousHttp,
    contents: str,
    len: int,
    content_type: str,
) -> None:
    """
    Sets the request contents of the interaction as an array of bytes.

    [Rust
    `pactffi_sync_http_set_request_contents_bin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_set_request_contents_bin)

    - `interaction` - the interaction to set the request contents for
    - `contents` - pointer to contents to copy from
    - `len` - number of bytes to copy from the contents pointer
    - `content_type` - pointer to the NULL-terminated UTF-8 string containing
      the content type of the data.

    # Safety

    The contents pointer must be valid for reads of `len` bytes, and it must be
    properly aligned and consecutive. Otherwise behaviour is undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the request contents as null.
    If the content type is a null pointer, or can't be parsed, it will set the
    content type as unknown.
    """
    raise NotImplementedError


def sync_http_get_response(interaction: SynchronousHttp) -> HttpResponse:
    """
    Get the response of a `SynchronousHttp` interaction.

    [Rust
    `pactffi_sync_http_get_response`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_get_response)

    # Safety

    The data pointed to by the pointer this function returns will be deleted
    when the interaction is deleted. Trying to use if after the interaction is
    deleted will result in undefined behaviour.

    # Error Handling

    If the interaction is NULL, returns NULL.
    """
    raise NotImplementedError


def sync_http_get_response_contents(interaction: SynchronousHttp) -> str | None:
    """
    Get the response contents of a `SynchronousHttp` interaction in string form.

    [Rust
    `pactffi_sync_http_get_response_contents`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_get_response_contents)

    Note that this function will return `None` if either the body is missing or
    is `null`.
    """
    ptr = lib.pactffi_sync_http_get_response_contents(interaction._ptr)
    if ptr == ffi.NULL:
        return None
    return OwnedString(ptr)


def sync_http_set_response_contents(
    interaction: SynchronousHttp,
    contents: str,
    content_type: str,
) -> None:
    """
    Sets the response contents of the interaction.

    [Rust
    `pactffi_sync_http_set_response_contents`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_set_response_contents)

    - `interaction` - the interaction to set the response contents for
    - `contents` - pointer to contents to copy from. Must be a valid
      NULL-terminated UTF-8 string pointer.
    - `content_type` - pointer to the NULL-terminated UTF-8 string containing
      the content type of the data.

    # Safety

    The response contents and content type must either be NULL pointers, or
    point to valid UTF-8 encoded NULL-terminated strings. Otherwise behaviour is
    undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the response contents as
    null. If the content type is a null pointer, or can't be parsed, it will set
    the content type as unknown.
    """
    raise NotImplementedError


def sync_http_get_response_contents_length(interaction: SynchronousHttp) -> int:
    """
    Get the length of the response contents of a `SynchronousHttp` interaction.

    [Rust
    `pactffi_sync_http_get_response_contents_length`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_get_response_contents_length)

    This function will return 0 if the body is missing.
    """
    return lib.pactffi_sync_http_get_response_contents_length(interaction._ptr)


def sync_http_get_response_contents_bin(interaction: SynchronousHttp) -> bytes | None:
    """
    Get the response contents of a `SynchronousHttp` interaction as bytes.

    [Rust
    `pactffi_sync_http_get_response_contents_bin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_get_response_contents_bin)

    Note that this function will return `None` if either the body is missing or
    is `null`.
    """
    ptr = lib.pactffi_sync_http_get_response_contents_bin(interaction._ptr)
    if ptr == ffi.NULL:
        return None
    return ffi.buffer(
        ptr,
        sync_http_get_response_contents_length(interaction),
    )[:]


def sync_http_set_response_contents_bin(
    interaction: SynchronousHttp,
    contents: str,
    len: int,
    content_type: str,
) -> None:
    """
    Sets the response contents of the `SynchronousHttp` interaction as bytes.

    [Rust
    `pactffi_sync_http_set_response_contents_bin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_set_response_contents_bin)

    - `interaction` - the interaction to set the response contents for
    - `contents` - pointer to contents to copy from
    - `len` - number of bytes to copy
    - `content_type` - pointer to the NULL-terminated UTF-8 string containing
      the content type of the data.

    # Safety

    The contents pointer must be valid for reads of `len` bytes, and it must be
    properly aligned and consecutive. Otherwise behaviour is undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the response contents as
    null. If the content type is a null pointer, or can't be parsed, it will set
    the content type as unknown.
    """
    raise NotImplementedError


def sync_http_get_description(interaction: SynchronousHttp) -> str:
    r"""
    Get a copy of the description.

    [Rust
    `pactffi_sync_http_get_description`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_get_description)

    Raises:
        RuntimeError:
            If the description cannot be retrieved
    """
    ptr = lib.pactffi_sync_http_get_description(interaction._ptr)
    if ptr == ffi.NULL:
        msg = "Failed to get description"
        raise RuntimeError(msg)
    return OwnedString(ptr)


def sync_http_set_description(interaction: SynchronousHttp, description: str) -> int:
    """
    Write the `description` field on the `SynchronousHttp`.

    [Rust
    `pactffi_sync_http_set_description`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_set_description)

    # Safety

    `description` must contain valid UTF-8. Invalid UTF-8 will be replaced with
    U+FFFD REPLACEMENT CHARACTER.

    This function will only reallocate if the new string does not fit in the
    existing buffer.

    # Error Handling

    Errors will be reported with a non-zero return value.
    """
    raise NotImplementedError


def sync_http_get_provider_state(
    interaction: SynchronousHttp,
    index: int,
) -> ProviderState:
    r"""
    Get a copy of the provider state at the given index from this interaction.

    [Rust
    `pactffi_sync_http_get_provider_state`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_get_provider_state)

    # Safety

    The returned structure must be deleted with `provider_state_delete`.

    Since it is a copy, the returned structure may safely outlive the
    `SynchronousHttp`.

    # Error Handling

    On failure, this function will return a variant other than Success.

    This function may fail if the index requested is out of bounds, or if any of
    the Rust strings contain embedded null ('\0') bytes.
    """
    raise NotImplementedError


def sync_http_get_provider_state_iter(
    interaction: SynchronousHttp,
) -> ProviderStateIterator:
    """
    Get an iterator over provider states.

    [Rust
    `pactffi_sync_http_get_provider_state_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_http_get_provider_state_iter)

    # Safety

    The underlying data must not change during iteration.

    Raises:
        RuntimeError:
            If the iterator cannot be retrieved
    """
    ptr = lib.pactffi_sync_http_get_provider_state_iter(interaction._ptr)
    if ptr == ffi.NULL:
        msg = "Failed to get provider state iterator"
        raise RuntimeError(msg)
    return ProviderStateIterator(ptr)


def pact_interaction_as_synchronous_http(
    interaction: PactInteraction,
) -> SynchronousHttp:
    r"""
    Casts this interaction to a `SynchronousHttp` interaction.

    Returns a NULL pointer if the interaction can not be casted to a
    `SynchronousHttp` interaction (for instance, it is a message interaction).
    The returned pointer must be freed with `pactffi_sync_http_delete` when no
    longer required.

    [Rust
    `pactffi_pact_interaction_as_synchronous_http`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_interaction_as_synchronous_http)

    # Safety This function is safe as long as the interaction pointer is a valid
    pointer.

    # Errors On any error, this function will return a NULL pointer.
    """
    raise NotImplementedError


def pact_interaction_as_asynchronous_message(
    interaction: PactInteraction,
) -> AsynchronousMessage:
    """
    Casts this interaction to a `AsynchronousMessage` interaction.

    Returns a NULL pointer if the interaction can not be casted to a
    `AsynchronousMessage` interaction (for instance, it is a http interaction).
    The returned pointer must be freed with `pactffi_async_message_delete` when
    no longer required.

    [Rust
    `pactffi_pact_interaction_as_asynchronous_message`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_interaction_as_asynchronous_message)

    Note that if the interaction is a V3 `Message`, it will be converted to a V4
    `AsynchronousMessage` before being returned.

    # Safety This function is safe as long as the interaction pointer is a valid
    pointer.

    # Errors On any error, this function will return a NULL pointer.
    """
    raise NotImplementedError


def pact_interaction_as_synchronous_message(
    interaction: PactInteraction,
) -> SynchronousMessage:
    """
    Casts this interaction to a `SynchronousMessage` interaction.

    Returns a NULL pointer if the interaction can not be casted to a
    `SynchronousMessage` interaction (for instance, it is a http interaction).
    The returned pointer must be freed with `pactffi_sync_message_delete` when
    no longer required.

    [Rust
    `pactffi_pact_interaction_as_synchronous_message`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_interaction_as_synchronous_message)

    # Safety This function is safe as long as the interaction pointer is a valid
    pointer.

    # Errors On any error, this function will return a NULL pointer.
    """
    raise NotImplementedError


def pact_async_message_iter_next(iter: PactAsyncMessageIterator) -> AsynchronousMessage:
    """
    Get the next asynchronous message from the iterator.

    [Rust
    `pactffi_pact_async_message_iter_next`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_async_message_iter_next)

    Raises:
        StopIteration:
            If the iterator has reached the end.
    """
    ptr = lib.pactffi_pact_async_message_iter_next(iter._ptr)
    if ptr == ffi.NULL:
        raise StopIteration
    return AsynchronousMessage(ptr, owned=True)


def pact_async_message_iter_delete(iter: PactAsyncMessageIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust
    `pactffi_pact_async_message_iter_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_async_message_iter_delete)
    """
    lib.pactffi_pact_async_message_iter_delete(iter._ptr)


def pact_sync_message_iter_next(iter: PactSyncMessageIterator) -> SynchronousMessage:
    """
    Get the next synchronous request/response message from the V4 pact.

    [Rust
    `pactffi_pact_sync_message_iter_next`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_sync_message_iter_next)

    Raises:
        StopIteration:
            If the iterator has reached the end.
    """
    ptr = lib.pactffi_pact_sync_message_iter_next(iter._ptr)
    if ptr == ffi.NULL:
        raise StopIteration
    return SynchronousMessage(ptr, owned=True)


def pact_sync_message_iter_delete(iter: PactSyncMessageIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust
    `pactffi_pact_sync_message_iter_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_sync_message_iter_delete)
    """
    lib.pactffi_pact_sync_message_iter_delete(iter._ptr)


def pact_sync_http_iter_next(iter: PactSyncHttpIterator) -> SynchronousHttp:
    """
    Get the next synchronous HTTP request/response interaction from the V4 pact.

    [Rust
    `pactffi_pact_sync_http_iter_next`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_sync_http_iter_next)

    Raises:
        StopIteration:
            If the iterator has reached the end.
    """
    ptr = lib.pactffi_pact_sync_http_iter_next(iter._ptr)
    if ptr == ffi.NULL:
        raise StopIteration
    return SynchronousHttp(ptr, owned=True)


def pact_sync_http_iter_delete(iter: PactSyncHttpIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust
    `pactffi_pact_sync_http_iter_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_sync_http_iter_delete)
    """
    lib.pactffi_pact_sync_http_iter_delete(iter._ptr)


def pact_interaction_iter_next(iter: PactInteractionIterator) -> PactInteraction:
    """
    Get the next interaction from the pact.

    [Rust
    `pactffi_pact_interaction_iter_next`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_interaction_iter_next)

    Raises:
        StopIteration:
            If the iterator has reached the end.
    """
    ptr = lib.pactffi_pact_interaction_iter_next(iter._ptr)
    if ptr == ffi.NULL:
        raise StopIteration
    raise NotImplementedError
    return PactInteraction(ptr)


def pact_interaction_iter_delete(iter: PactInteractionIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust
    `pactffi_pact_interaction_iter_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_interaction_iter_delete)
    """
    lib.pactffi_pact_interaction_iter_delete(iter._ptr)


def matching_rule_to_json(rule: MatchingRule) -> str:
    """
    Get the JSON form of the matching rule.

    [Rust
    `pactffi_matching_rule_to_json`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matching_rule_to_json)

    The returned string must be deleted with `pactffi_string_delete`.

    # Safety

    This function will fail if it is passed a NULL pointer, or the iterator that
    owns the value of the matching rule has been deleted.
    """
    return OwnedString(lib.pactffi_matching_rule_to_json(rule._ptr))


def matching_rules_iter_delete(iter: MatchingRuleCategoryIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust
    `pactffi_matching_rules_iter_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matching_rules_iter_delete)
    """
    lib.pactffi_matching_rules_iter_delete(iter._ptr)


def matching_rules_iter_next(
    iter: MatchingRuleCategoryIterator,
) -> MatchingRuleKeyValuePair:
    """
    Get the next path and matching rule out of the iterator, if possible.

    [Rust
    `pactffi_matching_rules_iter_next`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matching_rules_iter_next)

    The returned pointer must be deleted with
    `pactffi_matching_rules_iter_pair_delete`.

    # Safety

    The underlying data is owned by the `MatchingRuleKeyValuePair`, so is always
    safe to use.

    # Error Handling

    If no further data is present, returns NULL.
    """
    return MatchingRuleKeyValuePair(lib.pactffi_matching_rules_iter_next(iter._ptr))


def matching_rules_iter_pair_delete(pair: MatchingRuleKeyValuePair) -> None:
    """
    Free a pair of key and value returned from `message_metadata_iter_next`.

    [Rust
    `pactffi_matching_rules_iter_pair_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matching_rules_iter_pair_delete)
    """
    lib.pactffi_matching_rules_iter_pair_delete(pair._ptr)


def provider_state_iter_next(iter: ProviderStateIterator) -> ProviderState:
    """
    Get the next value from the iterator.

    [Rust
    `pactffi_provider_state_iter_next`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_provider_state_iter_next)

    # Safety

    The underlying data must not change during iteration.

    Raises:
        StopIteration:
            If no further data is present, or if an internal error occurs.
    """
    provider_state = lib.pactffi_provider_state_iter_next(iter._ptr)
    if provider_state == ffi.NULL:
        raise StopIteration
    return ProviderState(provider_state)


def provider_state_iter_delete(iter: ProviderStateIterator) -> None:
    """
    Delete the iterator.

    [Rust
    `pactffi_provider_state_iter_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_provider_state_iter_delete)
    """
    lib.pactffi_provider_state_iter_delete(iter._ptr)


def message_metadata_iter_next(iter: MessageMetadataIterator) -> MessageMetadataPair:
    """
    Get the next key and value out of the iterator, if possible.

    [Rust
    `pactffi_message_metadata_iter_next`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_message_metadata_iter_next)

    The returned pointer must be deleted with
    `pactffi_message_metadata_pair_delete`.

    # Safety

    The underlying data must not change during iteration. This function must
    only ever be called from a foreign language. Calling it from a Rust function
    that has a Tokio runtime in its call stack can result in a deadlock.

    Raises:
        StopIteration:
            If no further data is present.
    """
    ptr = lib.pactffi_message_metadata_iter_next(iter._ptr)
    if ptr == ffi.NULL:
        raise StopIteration
    return MessageMetadataPair(ptr)


def message_metadata_iter_delete(iter: MessageMetadataIterator) -> None:
    """
    Free the metadata iterator when you're done using it.

    [Rust
    `pactffi_message_metadata_iter_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_message_metadata_iter_delete)
    """
    lib.pactffi_message_metadata_iter_delete(iter._ptr)


def message_metadata_pair_delete(pair: MessageMetadataPair) -> None:
    """
    Free a pair of key and value returned from `message_metadata_iter_next`.

    [Rust
    `pactffi_message_metadata_pair_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_message_metadata_pair_delete)
    """
    lib.pactffi_message_metadata_pair_delete(pair._ptr)


def provider_get_name(provider: Provider) -> str:
    r"""
    Get a copy of this provider's name.

    [Rust
    `pactffi_provider_get_name`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_provider_get_name)

    The copy must be deleted with `pactffi_string_delete`.

    # Usage

    ```c
    // Assuming `file_name` and `json_str` are already defined.

    MessagePact *message_pact = pactffi_message_pact_new_from_json(file_name, json_str);
    if (message_pact == NULLPTR) {
        // handle error.
    }

    Provider *provider = pactffi_message_pact_get_provider(message_pact);
    if (provider == NULLPTR) {
        // handle error.
    }

    char *name = pactffi_provider_get_name(provider);
    if (name == NULL) {
        // handle error.
    }

    printf("%s\n", name);

    pactffi_string_delete(name);
    ```

    # Errors

    This function will fail if it is passed a NULL pointer, or the Rust string
    contains an embedded NULL byte. In the case of error, a NULL pointer will be
    returned.
    """
    raise NotImplementedError


def pact_get_provider(pact: Pact) -> Provider:
    """
    Get the provider from a Pact.

    This returns a copy of the provider model, and needs to be cleaned up with
    `pactffi_pact_provider_delete` when no longer required.

    [Rust
    `pactffi_pact_get_provider`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_get_provider)

    # Errors

    This function will fail if it is passed a NULL pointer. In the case of
    error, a NULL pointer will be returned.
    """
    raise NotImplementedError


def pact_provider_delete(provider: Provider) -> None:
    """
    Frees the memory used by the Pact provider.

    [Rust
    `pactffi_pact_provider_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_provider_delete)
    """
    raise NotImplementedError


def provider_state_get_name(provider_state: ProviderState) -> str | None:
    """
    Get the name of the provider state as a string.

    [Rust
    `pactffi_provider_state_get_name`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_provider_state_get_name)

    Raises:
        RuntimeError:
            If the name could not be retrieved.
    """
    ptr = lib.pactffi_provider_state_get_name(provider_state._ptr)
    if ptr == ffi.NULL:
        msg = "Failed to get provider state name."
        raise RuntimeError(msg)
    return OwnedString(ptr)


def provider_state_get_param_iter(
    provider_state: ProviderState,
) -> ProviderStateParamIterator:
    r"""
    Get an iterator over the params of a provider state.

    [Rust
    `pactffi_provider_state_get_param_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_provider_state_get_param_iter)

    # Safety

    This iterator carries a pointer to the provider state, and must not outlive
    the provider state.

    The provider state params also must not be modified during iteration. If it
    is, the old iterator must be deleted and a new iterator created.

    Raises:
        RuntimeError:
            If the iterator could not be created.
    """
    ptr = lib.pactffi_provider_state_get_param_iter(provider_state._ptr)
    if ptr == ffi.NULL:
        msg = "Failed to get provider state param iterator."
        raise RuntimeError(msg)
    return ProviderStateParamIterator(ptr)


def provider_state_param_iter_next(
    iter: ProviderStateParamIterator,
) -> ProviderStateParamPair:
    """
    Get the next key and value out of the iterator, if possible.

    [Rust
    `pactffi_provider_state_param_iter_next`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_provider_state_param_iter_next)

    # Safety

    The underlying data must not be modified during iteration.

    Raises:
        StopIteration:
            If no further data is present.
    """
    provider_state_param = lib.pactffi_provider_state_param_iter_next(iter._ptr)
    if provider_state_param == ffi.NULL:
        raise StopIteration
    return ProviderStateParamPair(provider_state_param)


def provider_state_delete(provider_state: ProviderState) -> None:
    """
    Free the provider state when you're done using it.

    [Rust
    `pactffi_provider_state_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_provider_state_delete)
    """
    raise NotImplementedError


def provider_state_param_iter_delete(iter: ProviderStateParamIterator) -> None:
    """
    Free the provider state param iterator when you're done using it.

    [Rust
    `pactffi_provider_state_param_iter_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_provider_state_param_iter_delete)
    """
    lib.pactffi_provider_state_param_iter_delete(iter._ptr)


def provider_state_param_pair_delete(pair: ProviderStateParamPair) -> None:
    """
    Free a pair of key and value.

    [Rust
    `pactffi_provider_state_param_pair_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_provider_state_param_pair_delete)
    """
    lib.pactffi_provider_state_param_pair_delete(pair._ptr)


def sync_message_new() -> SynchronousMessage:
    """
    Get a mutable pointer to a newly-created default message on the heap.

    [Rust
    `pactffi_sync_message_new`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_new)

    # Safety

    This function is safe.

    # Error Handling

    Returns NULL on error.
    """
    raise NotImplementedError


def sync_message_delete(message: SynchronousMessage) -> None:
    """
    Destroy the `Message` being pointed to.

    [Rust
    `pactffi_sync_message_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_delete)
    """
    lib.pactffi_sync_message_delete(message._ptr)


def sync_message_get_request_contents_str(message: SynchronousMessage) -> str:
    """
    Get the request contents of a `SynchronousMessage` in string form.

    [Rust
    `pactffi_sync_message_get_request_contents_str`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_get_request_contents_str)

    # Safety

    The returned string must be deleted with `pactffi_string_delete`.

    The returned string can outlive the message.

    # Error Handling

    If the message is NULL, returns NULL. If the body of the request message is
    missing, then this function also returns NULL. This means there's no
    mechanism to differentiate with this function call alone between a NULL
    message and a missing message body.
    """
    raise NotImplementedError


def sync_message_set_request_contents_str(
    message: SynchronousMessage,
    contents: str,
    content_type: str,
) -> None:
    """
    Sets the request contents of the message.

    [Rust
    `pactffi_sync_message_set_request_contents_str`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_set_request_contents_str)

    - `message` - the message to set the request contents for
    - `contents` - pointer to contents to copy from. Must be a valid
      NULL-terminated UTF-8 string pointer.
    - `content_type` - pointer to the NULL-terminated UTF-8 string containing
      the content type of the data.

    # Safety

    The message contents and content type must either be NULL pointers, or point
    to valid UTF-8 encoded NULL-terminated strings. Otherwise behaviour is
    undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the message contents as null.
    If the content type is a null pointer, or can't be parsed, it will set the
    content type as unknown.
    """
    raise NotImplementedError


def sync_message_get_request_contents_length(message: SynchronousMessage) -> int:
    """
    Get the length of the request contents of a `SynchronousMessage`.

    [Rust
    `pactffi_sync_message_get_request_contents_length`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_get_request_contents_length)

    # Safety

    This function is safe.

    # Error Handling

    If the message is NULL, returns 0. If the body of the request is missing,
    then this function also returns 0.
    """
    raise NotImplementedError


def sync_message_get_request_contents_bin(message: SynchronousMessage) -> bytes:
    """
    Get the request contents of a `SynchronousMessage` as a bytes.

    [Rust
    `pactffi_sync_message_get_request_contents_bin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_get_request_contents_bin)

    # Safety

    The number of bytes in the buffer will be returned by
    `pactffi_sync_message_get_request_contents_length`. It is safe to use the
    pointer while the message is not deleted or changed. Using the pointer after
    the message is mutated or deleted may lead to undefined behaviour.

    # Error Handling

    If the message is NULL, returns NULL. If the body of the message is missing,
    then this function also returns NULL.
    """
    raise NotImplementedError


def sync_message_set_request_contents_bin(
    message: SynchronousMessage,
    contents: str,
    len: int,
    content_type: str,
) -> None:
    """
    Sets the request contents of the message as an array of bytes.

    [Rust
    `pactffi_sync_message_set_request_contents_bin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_set_request_contents_bin)

    * `message` - the message to set the request contents for
    * `contents` - pointer to contents to copy from
    * `len` - number of bytes to copy from the contents pointer
    * `content_type` - pointer to the NULL-terminated UTF-8 string containing
      the content type of the data.

    # Safety

    The contents pointer must be valid for reads of `len` bytes, and it must be
    properly aligned and consecutive. Otherwise behaviour is undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the message contents as null.
    If the content type is a null pointer, or can't be parsed, it will set the
    content type as unknown.
    """
    raise NotImplementedError


def sync_message_get_request_contents(message: SynchronousMessage) -> MessageContents:
    """
    Get the request contents of an `SynchronousMessage` as a `MessageContents`.

    [Rust
    `pactffi_sync_message_get_request_contents`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_get_request_contents)

    # Safety

    The data pointed to by the pointer this function returns will be deleted
    when the message is deleted. Trying to use if after the message is deleted
    will result in undefined behaviour.

    # Error Handling

    If the message is NULL, returns NULL.
    """
    raise NotImplementedError


def sync_message_generate_request_contents(
    message: SynchronousMessage,
) -> MessageContents:
    """
    Get the request contents of an `SynchronousMessage` as a `MessageContents`.

    This function differs from `pactffi_sync_message_get_request_contents` in
    that it will process the message contents for any generators or matchers
    that are present in the message in order to generate the actual message
    contents as would be received by the consumer.

    [Rust
    `pactffi_sync_message_generate_request_contents`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_generate_request_contents)

    Raises:
        RuntimeError:
            If the request contents cannot be generated
    """
    ptr = lib.pactffi_sync_message_generate_request_contents(message._ptr)
    if ptr == ffi.NULL:
        msg = "Failed to generate request contents"
        raise RuntimeError(msg)
    return MessageContents(ptr, owned=False)


def sync_message_get_number_responses(message: SynchronousMessage) -> int:
    """
    Get the number of response messages in the `SynchronousMessage`.

    [Rust
    `pactffi_sync_message_get_number_responses`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_get_number_responses)

    If the message is null, this function will return 0.
    """
    return lib.pactffi_sync_message_get_number_responses(message._ptr)


def sync_message_get_response_contents_str(
    message: SynchronousMessage,
    index: int,
) -> str:
    """
    Get the response contents of a `SynchronousMessage` in string form.

    [Rust
    `pactffi_sync_message_get_response_contents_str`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_get_response_contents_str)

    # Safety

    The returned string must be deleted with `pactffi_string_delete`.

    The returned string can outlive the message.

    # Error Handling

    If the message is NULL or the index is not valid, returns NULL.

    If the body of the response message is missing, then this function also
    returns NULL. This means there's no mechanism to differentiate with this
    function call alone between a NULL message and a missing message body.
    """
    raise NotImplementedError


def sync_message_set_response_contents_str(
    message: SynchronousMessage,
    index: int,
    contents: str,
    content_type: str,
) -> None:
    """
    Sets the response contents of the message as a string.

    If index is greater
    than the number of responses in the message, the responses will be padded
    with default values.

    [Rust
    `pactffi_sync_message_set_response_contents_str`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_set_response_contents_str)

    * `message` - the message to set the response contents for
    * `index` - index of the response to set. 0 is the first response.
    * `contents` - pointer to contents to copy from. Must be a valid
      NULL-terminated UTF-8 string pointer.
    * `content_type` - pointer to the NULL-terminated UTF-8 string containing
      the content type of the data.

    # Safety

    The message contents and content type must either be NULL pointers, or point
    to valid UTF-8 encoded NULL-terminated strings. Otherwise behaviour is
    undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the response contents as
    null. If the content type is a null pointer, or can't be parsed, it will set
    the content type as unknown.
    """
    raise NotImplementedError


def sync_message_get_response_contents_length(
    message: SynchronousMessage,
    index: int,
) -> int:
    """
    Get the length of the response contents of a `SynchronousMessage`.

    [Rust
    `pactffi_sync_message_get_response_contents_length`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_get_response_contents_length)

    # Safety

    This function is safe.

    # Error Handling

    If the message is NULL or the index is not valid, returns 0. If the body of
    the request is missing, then this function also returns 0.
    """
    raise NotImplementedError


def sync_message_get_response_contents_bin(
    message: SynchronousMessage,
    index: int,
) -> bytes:
    """
    Get the response contents of a `SynchronousMessage` as bytes.

    [Rust
    `pactffi_sync_message_get_response_contents_bin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_get_response_contents_bin)

    # Safety

    The number of bytes in the buffer will be returned by
    `pactffi_sync_message_get_response_contents_length`. It is safe to use the
    pointer while the message is not deleted or changed. Using the pointer after
    the message is mutated or deleted may lead to undefined behaviour.

    # Error Handling

    If the message is NULL or the index is not valid, returns NULL. If the body
    of the message is missing, then this function also returns NULL.
    """
    raise NotImplementedError


def sync_message_set_response_contents_bin(
    message: SynchronousMessage,
    index: int,
    contents: str,
    len: int,
    content_type: str,
) -> None:
    """
    Sets the response contents of the message at the given index as bytes.

    If index is greater than the number of responses in the message, the
    responses will be padded with default values.

    [Rust
    `pactffi_sync_message_set_response_contents_bin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_set_response_contents_bin)

    * `message` - the message to set the response contents for
    * `index` - index of the response to set. 0 is the first response
    * `contents` - pointer to contents to copy from
    * `len` - number of bytes to copy
    * `content_type` - pointer to the NULL-terminated UTF-8 string containing
      the content type of the data.

    # Safety

    The contents pointer must be valid for reads of `len` bytes, and it must be
    properly aligned and consecutive. Otherwise behaviour is undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the message contents as null.
    If the content type is a null pointer, or can't be parsed, it will set the
    content type as unknown.
    """
    raise NotImplementedError


def sync_message_get_response_contents(
    message: SynchronousMessage,
    index: int,
) -> MessageContents:
    """
    Get the response contents of an `SynchronousMessage` as a `MessageContents`.

    [Rust
    `pactffi_sync_message_get_response_contents`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_get_response_contents)

    # Safety

    The data pointed to by the pointer this function returns will be deleted
    when the message is deleted. Trying to use if after the message is deleted
    will result in undefined behaviour.

    # Error Handling

    If the message is NULL or the index is not valid, returns NULL.
    """
    raise NotImplementedError


def sync_message_generate_response_contents(
    message: SynchronousMessage,
    index: int,
) -> MessageContents:
    """
    Get the response contents of an `SynchronousMessage` as a `MessageContents`.

    This function differs from
    `sync_message_get_response_contents` in that it will process
    the message contents for any generators or matchers that are present in
    the message in order to generate the actual message contents as would be
    received by the consumer.

    [Rust
    `pactffi_sync_message_generate_response_contents`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_generate_response_contents)

    Raises:
        RuntimeError:
            If the response contents could not be generated.
    """
    ptr = lib.pactffi_sync_message_generate_response_contents(message._ptr, index)
    if ptr == ffi.NULL:
        msg = "Failed to generate response contents."
        raise RuntimeError(msg)
    return MessageContents(ptr, owned=False)


def sync_message_get_description(message: SynchronousMessage) -> str:
    r"""
    Get a copy of the description.

    [Rust
    `pactffi_sync_message_get_description`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_get_description)

    Raises:
        RuntimeError:
            If the description could not be retrieved
    """
    ptr = lib.pactffi_sync_message_get_description(message._ptr)
    if ptr == ffi.NULL:
        msg = "Failed to get description."
        raise RuntimeError(msg)
    return OwnedString(ptr)


def sync_message_set_description(message: SynchronousMessage, description: str) -> int:
    """
    Write the `description` field on the `SynchronousMessage`.

    [Rust
    `pactffi_sync_message_set_description`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_set_description)

    # Safety

    `description` must contain valid UTF-8. Invalid UTF-8 will be replaced with
    U+FFFD REPLACEMENT CHARACTER.

    This function will only reallocate if the new string does not fit in the
    existing buffer.

    # Error Handling

    Errors will be reported with a non-zero return value.
    """
    raise NotImplementedError


def sync_message_get_provider_state(
    message: SynchronousMessage,
    index: int,
) -> ProviderState:
    r"""
    Get a copy of the provider state at the given index from this message.

    [Rust
    `pactffi_sync_message_get_provider_state`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_get_provider_state)

    # Safety

    The returned structure must be deleted with `provider_state_delete`.

    Since it is a copy, the returned structure may safely outlive the
    `SynchronousMessage`.

    # Error Handling

    On failure, this function will return a variant other than Success.

    This function may fail if the index requested is out of bounds, or if any of
    the Rust strings contain embedded null ('\0') bytes.
    """
    raise NotImplementedError


def sync_message_get_provider_state_iter(
    message: SynchronousMessage,
) -> ProviderStateIterator:
    """
    Get an iterator over provider states.

    [Rust
    `pactffi_sync_message_get_provider_state_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_sync_message_get_provider_state_iter)

    # Safety

    The underlying data must not change during iteration.

    Raises:
        RuntimeError:
            If the iterator could not be created.
    """
    ptr = lib.pactffi_sync_message_get_provider_state_iter(message._ptr)
    if ptr == ffi.NULL:
        msg = "Failed to get provider state iterator."
        raise RuntimeError(msg)
    return ProviderStateIterator(ptr)


def string_delete(string: OwnedString) -> None:
    """
    Delete a string previously returned by this FFI.

    [Rust
    `pactffi_string_delete`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_string_delete)
    """
    lib.pactffi_string_delete(string._ptr)


def create_mock_server(pact_str: str, addr_str: str, *, tls: bool) -> int:
    """
    [DEPRECATED] External interface to create a HTTP mock server.

    A pointer to the pact JSON as a NULL-terminated C string is passed in, as
    well as the port for the mock server to run on. A value of 0 for the port
    will result in a port being allocated by the operating system. The port of
    the mock server is returned.

    [Rust
    `pactffi_create_mock_server`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_create_mock_server)

    * `pact_str` - Pact JSON
    * `addr_str` - Address to bind to in the form name:port (i.e. 127.0.0.1:80)
    * `tls` - boolean flag to indicate of the mock server should use TLS (using
      a self-signed certificate)

    This function is deprecated and replaced with
    `pactffi_create_mock_server_for_transport`.

    # Errors

    Errors are returned as negative values.

    | Error | Description |
    |-------|-------------|
    | -1 | A null pointer was received |
    | -2 | The pact JSON could not be parsed |
    | -3 | The mock server could not be started |
    | -4 | The method panicked |
    | -5 | The address is not valid |
    | -6 | Could not create the TLS configuration with the self-signed certificate |
    """
    warnings.warn(
        "This function is deprecated, use create_mock_server_for_transport instead",
        DeprecationWarning,
        stacklevel=2,
    )
    raise NotImplementedError


def get_tls_ca_certificate() -> OwnedString:
    """
    Fetch the CA Certificate used to generate the self-signed certificate.

    [Rust
    `pactffi_get_tls_ca_certificate`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_get_tls_ca_certificate)

    **NOTE:** The string for the result is allocated on the heap, and will have
    to be freed by the caller using pactffi_string_delete.

    # Errors

    An empty string indicates an error reading the pem file.
    """
    return OwnedString(lib.pactffi_get_tls_ca_certificate())


def create_mock_server_for_pact(pact: PactHandle, addr_str: str, *, tls: bool) -> int:
    """
    [DEPRECATED] External interface to create a HTTP mock server.

    A Pact handle is passed in, as well as the port for the mock server to run
    on. A value of 0 for the port will result in a port being allocated by the
    operating system. The port of the mock server is returned.

    [Rust
    `pactffi_create_mock_server_for_pact`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_create_mock_server_for_pact)

    * `pact` - Handle to a Pact model created with created with
      `pactffi_new_pact`.
    * `addr_str` - Address to bind to in the form name:port (i.e. 127.0.0.1:0).
      Must be a valid UTF-8 NULL-terminated string.
    * `tls` - boolean flag to indicate of the mock server should use TLS (using
      a self-signed certificate)

    This function is deprecated and replaced with
    `pactffi_create_mock_server_for_transport`.

    # Errors

    Errors are returned as negative values.

    | Error | Description |
    |-------|-------------|
    | -1 | An invalid handle was received. Handles should be created with `pactffi_new_pact` |
    | -3 | The mock server could not be started |
    | -4 | The method panicked |
    | -5 | The address is not valid |
    | -6 | Could not create the TLS configuration with the self-signed certificate |
    """  # noqa: E501
    warnings.warn(
        "This function is deprecated, use create_mock_server_for_transport instead",
        DeprecationWarning,
        stacklevel=2,
    )
    raise NotImplementedError


def create_mock_server_for_transport(
    pact: PactHandle,
    addr: str,
    port: int,
    transport: str,
    transport_config: str | None,
) -> PactServerHandle:
    """
    Create a mock server for the provided Pact handle and transport.

    [Rust
    `pactffi_create_mock_server_for_transport`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_create_mock_server_for_transport)

    Args:
        pact:
            Handle to the Pact model.

        addr:
            The address to bind to.

        port:
            The port number to bind to. A value of zero will result in the
            operating system allocating an available port.

        transport:
            The transport to use (i.e. http, https, grpc). The underlying Pact
            library will interpret this, typically in a case-sensitive way.

        transport_config:
            Configuration to be passed to the transport. This must be a valid
            JSON string, or `None` if not required.

    Returns:
        A handle to the mock server.

    Raises:
        RuntimeError:
            If the mock server could not be created. The error message will
            contain details of the error.
    """
    ret: int = lib.pactffi_create_mock_server_for_transport(
        pact._ref,
        addr.encode("utf-8"),
        port,
        transport.encode("utf-8"),
        (transport_config.encode("utf-8") if transport_config else ffi.NULL),
    )
    if ret > 0:
        return PactServerHandle(ret)

    if ret == -1:
        msg = f"An invalid Pact handle was received: {pact}."
    elif ret == -2:  # noqa: PLR2004
        msg = "Invalid transport_config JSON."
    elif ret == -3:  # noqa: PLR2004
        msg = f"Pact mock server could not be started for {pact}."
    elif ret == -4:  # noqa: PLR2004
        msg = f"Panick during Pact mock server creation for {pact}."
    elif ret == -5:  # noqa: PLR2004
        msg = f"Address is invalid: {addr}."
    else:
        msg = f"An unknown error occurred during Pact mock server creation for {pact}."
    raise RuntimeError(msg)


def mock_server_matched(mock_server_handle: PactServerHandle) -> bool:
    """
    External interface to check if a mock server has matched all its requests.

    If all requests have been matched, `true` is returned. `false` is returned
    if any request has not been successfully matched, or the method panics.

    [Rust
    `pactffi_mock_server_matched`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_mock_server_matched)
    """
    return lib.pactffi_mock_server_matched(mock_server_handle._ref)


def mock_server_mismatches(
    mock_server_handle: PactServerHandle,
) -> list[dict[str, Any]]:
    """
    External interface to get all the mismatches from a mock server.

    [Rust
    `pactffi_mock_server_mismatches`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_mock_server_mismatches)

    # Errors

    Raises:
        RuntimeError:
            If there is no mock server with the provided port number, or the
            function panics.
    """
    ptr = lib.pactffi_mock_server_mismatches(mock_server_handle._ref)
    if ptr == ffi.NULL:
        msg = f"No mock server found with port {mock_server_handle}."
        raise RuntimeError(msg)
    string = ffi.string(ptr)
    if isinstance(string, bytes):
        string = string.decode("utf-8")
    return json.loads(string)


def cleanup_mock_server(mock_server_handle: PactServerHandle) -> None:
    """
    External interface to cleanup a mock server.

    This function will try terminate the mock server with the given port number
    and cleanup any memory allocated for it.

    [Rust
    `pactffi_cleanup_mock_server`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_cleanup_mock_server)

    Args:
        mock_server_handle:
            Handle to the mock server to cleanup.

    Raises:
        RuntimeError:
            If the mock server could not be cleaned up.
    """
    success: bool = lib.pactffi_cleanup_mock_server(mock_server_handle._ref)
    if not success:
        msg = f"Could not cleanup mock server with port {mock_server_handle._ref}"
        raise RuntimeError(msg)


def write_pact_file(
    mock_server_handle: PactServerHandle,
    directory: str | Path,
    *,
    overwrite: bool,
) -> None:
    """
    External interface to trigger a mock server to write out its pact file.

    This function should be called if all the consumer tests have passed. The
    directory to write the file to is passed as the second parameter.

    [Rust
    `pactffi_write_pact_file`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_write_pact_file)

    Args:
        mock_server_handle:
            Handle to the mock server to write the pact file for.

        directory:
            Directory to write the pact file to.

        overwrite:
            Whether to overwrite any existing pact files. If this is false, the
            pact file will be merged with any existing pact file.

    Raises:
        RuntimeError:
            If there was an error writing the pact file.
    """
    ret: int = lib.pactffi_write_pact_file(
        mock_server_handle._ref,
        str(directory).encode("utf-8"),
        overwrite,
    )
    if ret == 0:
        return
    if ret == 1:
        msg = (
            f"The function panicked while writing the Pact for {mock_server_handle} in"
            f" {directory}."
        )
    elif ret == 2:  # noqa: PLR2004
        msg = (
            f"The Pact file for {mock_server_handle} could not be written in"
            f" {directory}."
        )
    elif ret == 3:  # noqa: PLR2004
        msg = f"The Pact for the {mock_server_handle} was not found."
    else:
        msg = (
            "An unknown error occurred while writing the Pact for"
            f" {mock_server_handle} in {directory}."
        )
    raise RuntimeError(msg)


def mock_server_logs(mock_server_handle: PactServerHandle) -> str:
    """
    Fetch the logs for the mock server.

    This needs the memory buffer log sink to be setup before the mock server is
    started.

    [Rust
    `pactffi_mock_server_logs`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_mock_server_logs)

    Raises:
        RuntimeError:
            If the logs for the mock server can not be retrieved.
    """
    ptr = lib.pactffi_mock_server_logs(mock_server_handle._ref)
    if ptr == ffi.NULL:
        msg = f"Unable to obtain logs from {mock_server_handle!r}"
        raise RuntimeError(msg)
    string = ffi.string(ptr)
    if isinstance(string, bytes):
        string = string.decode("utf-8")
    return string


def generate_datetime_string(format: str) -> StringResult:
    """
    Generates a datetime value from the provided format string.

    This uses the current system date and time NOTE: The memory for the returned
    string needs to be freed with the `pactffi_string_delete` function

    [Rust
    `pactffi_generate_datetime_string`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_generate_datetime_string)

    # Safety

    If the format string pointer is NULL or has invalid UTF-8 characters, an
    error result will be returned. If the format string pointer is not a valid
    pointer or is not a NULL-terminated string, this will lead to undefined
    behaviour.
    """
    raise NotImplementedError


def check_regex(regex: str, example: str) -> bool:
    """
    Checks that the example string matches the given regex.

    [Rust
    `pactffi_check_regex`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_check_regex)

    # Safety

    Both the regex and example pointers must be valid pointers to
    NULL-terminated strings. Invalid pointers will result in undefined
    behaviour.
    """
    raise NotImplementedError


def generate_regex_value(regex: str) -> StringResult:
    """
    Generates an example string based on the provided regex.

    NOTE: The memory for the returned string needs to be freed with the
    `pactffi_string_delete` function.

    [Rust
    `pactffi_generate_regex_value`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_generate_regex_value)

    # Safety

    The regex pointer must be a valid pointer to a NULL-terminated string.
    Invalid pointers will result in undefined behaviour.
    """
    raise NotImplementedError


def free_string(s: str) -> None:
    """
    [DEPRECATED] Frees the memory allocated to a string by another function.

    [Rust
    `pactffi_free_string`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_free_string)

    This function is deprecated. Use `pactffi_string_delete` instead.

    # Safety

    The string pointer can be NULL (which is a no-op), but if it is not a valid
    pointer the call will result in undefined behaviour.
    """
    warnings.warn(
        "This function is deprecated, use string_delete instead",
        DeprecationWarning,
        stacklevel=2,
    )
    raise NotImplementedError


def new_pact(consumer_name: str, provider_name: str) -> PactHandle:
    """
    Creates a new Pact model and returns a handle to it.

    [Rust
    `pactffi_new_pact`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_new_pact)

    Args:
        consumer_name:
            The name of the consumer for the pact.

        provider_name:
            The name of the provider for the pact.

    Returns:
        Handle to the new Pact model.
    """
    return PactHandle(
        lib.pactffi_new_pact(
            consumer_name.encode("utf-8"),
            provider_name.encode("utf-8"),
        ),
    )


def pact_handle_to_pointer(pact: PactHandle) -> Pact:
    """
    Unwraps a Pact handle to the underlying Pact.

    The Pact model which has been cloned from the Pact handle's inner Pact
    model.

    The returned Pact model must be freed with the `pactffi_pact_model_delete`
    function when no longer needed.
    """
    raise NotImplementedError


def new_interaction(pact: PactHandle, description: str) -> InteractionHandle:
    """
    Creates a new HTTP Interaction and returns a handle to it.

    Calling this function with the same description as an existing interaction
    will result in that interaction being replaced with the new one.

    [Rust
    `pactffi_new_interaction`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_new_interaction)

    Args:
        pact:
            Handle to the Pact model.

        description:
            The interaction description. It needs to be unique for each Pact.

    Returns:
        Handle to the new Interaction.
    """
    return InteractionHandle(
        lib.pactffi_new_interaction(
            pact._ref,
            description.encode("utf-8"),
        ),
    )


def new_message_interaction(pact: PactHandle, description: str) -> InteractionHandle:
    """
    Creates a new message interaction and returns a handle to it.

    Calling this function with the same description as an existing interaction
    will result in that interaction being replaced with the new one.

    [Rust
    `pactffi_new_message_interaction`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_new_message_interaction)

    Args:
        pact:
            Handle to the Pact model.

        description:
            The interaction description. It needs to be unique for each Pact.

    Returns:
        Handle to the new Interaction
    """
    return InteractionHandle(
        lib.pactffi_new_message_interaction(
            pact._ref,
            description.encode("utf-8"),
        ),
    )


def new_sync_message_interaction(
    pact: PactHandle,
    description: str,
) -> InteractionHandle:
    """
    Creates a new synchronous message interaction and returns a handle to it.

    Calling this function with the same description as an existing interaction
    will result in that interaction being replaced with the new one.

    [Rust
    `pactffi_new_sync_message_interaction`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_new_sync_message_interaction)

    Args:
        pact:
            Handle to the Pact model.

        description:
            The interaction description. It needs to be unique for each Pact.

    Returns:
        Handle to the new Interaction
    """
    return InteractionHandle(
        lib.pactffi_new_sync_message_interaction(
            pact._ref,
            description.encode("utf-8"),
        ),
    )


def upon_receiving(interaction: InteractionHandle, description: str) -> None:
    """
    Sets the description for the Interaction.

    [Rust
    `pactffi_upon_receiving`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_upon_receiving)

    This function

    Args:
        interaction:
            Handle to the Interaction.

        description:
            The interaction description. It needs to be unique for each Pact.

    Raises:
        NotImplementedError:
            This function has intentionally been left unimplemented.

        RuntimeError:
            If the interaction description could not be set.
    """
    # This function has intentionally been left unimplemented. The rationale is
    # to avoid code of the form:
    #
    # ```python
    #     .with_request("GET", "/")
    #     .upon_receiving("some new description")
    # ```
    raise NotImplementedError

    success: bool = lib.pactffi_upon_receiving(
        interaction._ref,
        description.encode("utf-8"),
    )
    if not success:
        msg = "The interaction description could not be set."
        raise RuntimeError(msg)


def given(interaction: InteractionHandle, description: str) -> None:
    """
    Adds a provider state to the Interaction.

    [Rust
    `pactffi_given`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_given)

    Args:
        interaction:
            Handle to the Interaction.

        description:
            The provider state description. It needs to be unique.

    Raises:
        RuntimeError:
            If the provider state could not be specified.
    """
    success: bool = lib.pactffi_given(interaction._ref, description.encode("utf-8"))
    if not success:
        msg = "The provider state could not be specified."
        raise RuntimeError(msg)


def interaction_test_name(interaction: InteractionHandle, test_name: str) -> None:
    """
    Sets the test name annotation for the interaction.

    This allows capturing the name of the test as metadata. This can only be
    used with V4 interactions.

    [Rust
    `pactffi_interaction_test_name`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_interaction_test_name)

    Args:
        interaction:
            Handle to the Interaction.

        test_name:
            The test name to set.

    Raises:
        RuntimeError:
            If the test name can not be set.

    """
    ret: int = lib.pactffi_interaction_test_name(
        interaction._ref,
        test_name.encode("utf-8"),
    )
    if ret == 0:
        return
    if ret == 1:
        msg = f"Function panicked: {get_error_message()}"
    elif ret == 2:  # noqa: PLR2004
        msg = f"Invalid handle: {interaction}."
    elif ret == 3:  # noqa: PLR2004
        msg = f"Mock server for {interaction} has already started."
    elif ret == 4:  # noqa: PLR2004
        msg = f"Interaction {interaction} is not a V4 interaction."
    else:
        msg = f"Unknown error setting test name for {interaction}."
    raise RuntimeError(msg)


def given_with_param(
    interaction: InteractionHandle,
    description: str,
    name: str,
    value: str,
) -> None:
    """
    Adds a parameter key and value to a provider state to the Interaction.

    If the provider state does not exist, a new one will be created, otherwise
    the parameter will be merged into the existing one. The parameter value will
    be parsed as JSON.

    [Rust
    `pactffi_given_with_param`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_given_with_param)

    Args:
        interaction:
            Handle to the Interaction.

        description:
            The provider state description.

        name:
            Parameter name.

        value:
            Parameter value as JSON.

    Raises:
        RuntimeError:
            If the interaction state could not be updated.
    """
    success: bool = lib.pactffi_given_with_param(
        interaction._ref,
        description.encode("utf-8"),
        name.encode("utf-8"),
        value.encode("utf-8"),
    )
    if not success:
        msg = "The interaction state could not be updated."
        raise RuntimeError(msg)


def given_with_params(
    interaction: InteractionHandle,
    description: str,
    params: str,
) -> None:
    """
    Adds a provider state to the Interaction.

    If the params is not an JSON object, it will add it as a single parameter
    with a `value` key.

    [Rust
    `pactffi_given_with_params`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_given_with_params)

    Args:
        interaction:
            Handle to the Interaction.

        description:
            The provider state description.

        params:
            Parameter values as a JSON fragment.

    Raises:
        RuntimeError:
            If the interaction state could not be updated.
    """
    ret: int = lib.pactffi_given_with_params(
        interaction._ref,
        description.encode("utf-8"),
        params.encode("utf-8"),
    )
    if ret == 0:
        return
    if ret == 1:
        msg = "The interaction state could not be updated."
    elif ret == 2:  # noqa: PLR2004
        msg = f"Internal error: {get_error_message()}"
    elif ret == 3:  # noqa: PLR2004
        msg = "Invalid C string."
    else:
        msg = "Unknown error."
    raise RuntimeError(msg)


def with_request(interaction: InteractionHandle, method: str, path: str) -> None:
    r"""
    Configures the request for the Interaction.

    [Rust
    `pactffi_with_request`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_with_request)

    Args:
        interaction:
            Handle to the Interaction.

        method:
            The request HTTP method.

        path:
            The request path.

            This may be a simple string in which case it will be used as-is, or
            it may be a [JSON matching
            rule](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.22/rust/pact_ffi/IntegrationJson.md)
            which allows regex patterns. For examples:

            ```json
            {
                "value": "/path/to/100",
                "pact:matcher:type": "regex",
                "regex": "/path/to/\\d+"
            }
            ```

    Raises:
        RuntimeError:
            If the request could not be specified.
    """
    success: bool = lib.pactffi_with_request(
        interaction._ref,
        method.encode("utf-8"),
        path.encode("utf-8"),
    )
    if not success:
        msg = f"The request '{method} {path}' could not be specified for {interaction}."
        raise RuntimeError(msg)


def with_query_parameter_v2(
    interaction: InteractionHandle,
    name: str,
    index: int,
    value: str,
) -> None:
    r"""
    Configures a query parameter for the Interaction.

    [Rust
    `pactffi_with_query_parameter_v2`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_with_query_parameter_v2)

    To setup a query parameter with multiple values, you can either call this
    function multiple times with a different index value:

    ```python
    with_query_parameter_v2(handle, "version", 0, "2")
    with_query_parameter_v2(handle, "version", 0, "3")
    ```

    Or you can call it once with a JSON value that contains multiple values:

    ```python
    with_query_parameter_v2(
        handle,
        "version",
        0,
        json.dumps({"value": ["2", "3"]}),
    )
    ```

    The JSON value can also contain a matcher, which will be used to match the
    query parameter value. For example, a semver matcher might look like this:

    ```python
    with_query_parameter_v2(
        handle,
        "version",
        0,
        json.dumps({
            "value": "1.2.3",
            "pact:matcher:type": "regex",
            "regex": r"\d+\.\d+\.\d+",
        }),
    )
    ```

    See [IntegrationJson.md](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.22/rust/pact_ffi/IntegrationJson.md)

    If you want the matching rules to apply to all values (and not just the one
    with the given index), make sure to set the value to be an array.

    ```python
    with_query_parameter_v2(
        handle,
        "id",
        0,
        json.dumps({
            "value": ["2"],
            "pact:matcher:type": "regex",
            "regex": r"\d+",
        }),
    )
    ```

    For query parameters with no value, two distinct formats are provided:

    1.  Parameters with blank values, as specified by `?foo=&bar=`, require an
        empty string:

        ```python
        with_query_parameter_v2(handle, "foo", 0, "")
        with_query_parameter_v2(handle, "bar", 0, "")
        ```

    2.  Parameters with no associated value, as specified by `?foo&bar`, require
        a NULL pointer:

        ```python
        with_query_parameter_v2(handle, "foo", 0, None)
        with_query_parameter_v2(handle, "bar", 0, None)
        ```

    Args:
        interaction:
            Handle to the Interaction.

        name:
            The query parameter name.

        index:
            The index of the value (starts at 0). You can use this to create a
            query parameter with multiple values.

        value:
            The query parameter value.

            This may be a simple string in which case it will be used as-is, or
            it may be a [JSON matching
            rule](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.22/rust/pact_ffi/IntegrationJson.md).

    Raises:
        RuntimeError:
            If there was an error setting the query parameter.
    """
    success: bool = lib.pactffi_with_query_parameter_v2(
        interaction._ref,
        name.encode("utf-8"),
        index,
        value.encode("utf-8"),
    )
    if not success:
        msg = f"Failed to add query parameter {name} to request {interaction}."
        raise RuntimeError(msg)


def with_specification(pact: PactHandle, version: PactSpecification) -> None:
    """
    Sets the specification version for a given Pact model.

    [Rust
    `pactffi_with_specification`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_with_specification)

    Args:
        pact:
            Handle to a Pact model.

        version:
            The spec version to use.

    Raises:
        RuntimeError:
            If the Pact specification could not be set.
    """
    success: bool = lib.pactffi_with_specification(pact._ref, version.value)
    if not success:
        msg = f"Failed to set Pact specification for {pact}"
        raise RuntimeError(msg)


def handle_get_pact_spec_version(handle: PactHandle) -> PactSpecification:
    """
    Fetches the Pact specification version for the given Pact model.

    [Rust
    `pactffi_handle_get_pact_spec_version`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_handle_get_pact_spec_version)

    Args:
        handle:
            Handle to a Pact model.

    Returns:
        The spec version for the Pact model.
    """
    return PactSpecification(lib.pactffi_handle_get_pact_spec_version(handle._ref))


def with_pact_metadata(
    pact: PactHandle,
    namespace: str,
    name: str,
    value: str,
) -> None:
    """
    Sets the additional metadata on the Pact file.

    Common uses are to add the client library details such as the name and
    version Returns false if the interaction or Pact can't be modified (i.e. the
    mock server for it has already started)

    [Rust
    `pactffi_with_pact_metadata`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_with_pact_metadata)

    Args:
        pact:
            Handle to a Pact model

        namespace:
            The top level metadat key to set any key values on

        name:
            The key to set

        value:
            The value to set

    Raises:
        RuntimeError:
            If the metadata could not be set.
    """
    success: bool = lib.pactffi_with_pact_metadata(
        pact._ref,
        namespace.encode("utf-8"),
        name.encode("utf-8"),
        value.encode("utf-8"),
    )
    if not success:
        msg = f"Failed to set Pact metadata for {pact} with {namespace}.{name}={value}"
        raise RuntimeError(msg)


def with_metadata(
    interaction: InteractionHandle,
    key: str,
    value: str,
    part: InteractionPart,
) -> None:
    r"""
    Adds metadata to the interaction.

    Metadata is only relevant for message interactions to provide additional
    information about the message, such as the queue name, message type, tags,
    timestamps, etc.

    * `key` - metadata key
    * `value` - metadata value, supports JSON structures with matchers and
      generators. Passing a `NULL` point will remove the metadata key instead.
    * `part` - the part of the interaction to add the metadata to (only
     relevant for synchronous message interactions).

    Returns `true` if the metadata was added successfully, `false` otherwise.

    To include matching rules for the value, include the matching rule JSON
    format with the value as a single JSON document. I.e.

    ```python with_metadata(
        handle, "TagData", json.dumps({
            "value": {"ID": "sjhdjkshsdjh", "weight": 100.5},
            "pact:matcher:type": "type",
        }),
    )
    ```

    See
    [IntegrationJson.md](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.22/rust/pact_ffi/IntegrationJson.md)

    # Note

    For HTTP interactions, use [`with_header_v2`][pact.v3.ffi.with_header_v2]
    instead. This function will not have any effect on HTTP interactions and
    returns `false`.

    For synchronous message interactions, the `part` parameter is required to
    specify whether the metadata should be added to the request or response
    part. For responses which can have multiple messages, the metadata will be
    set on all response messages. This also requires for responses to have been
    defined in the interaction.

    The [`with_body`][pact.v3.ffi.with_body] will also contribute to the
    metadata of the message (both sync and async) by setting the key
    `contentType` with the content type of the message.

    # Safety

    The key and value parameters must be valid pointers to NULL terminated
    strings, or `NULL` for the value parameter if the metadata key should be
    removed.

    Raises:
        RuntimeError:
            If the metadata could not be set.
    """
    success: bool = lib.pactffi_with_metadata(
        interaction._ref,
        key.encode("utf-8"),
        value.encode("utf-8"),
        part.value,
    )
    if not success:
        msg = f"Failed to set metadata for {interaction} with {key}={value}"
        raise RuntimeError(msg)


def with_header_v2(
    interaction: InteractionHandle,
    part: InteractionPart,
    name: str,
    index: int,
    value: str,
) -> None:
    r"""
    Configures a header for the Interaction.

    [Rust `pactffi_with_header_v2`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_with_header_v2)

    To setup a header with multiple values, you can either call this
    function multiple times with a different index value:

    ```python
    with_header_v2(handle, part, "Accept-Version", 0, "2")
    with_header_v2(handle, part, "Accept-Version", 0, "3")
    ```

    Or you can call it once with a JSON value that contains multiple values:

    ```python
    with_header_v2(
        handle,
        part,
        "Accept-Version",
        0,
        json.dumps({"value": ["2", "3"]}),
    )
    ```

    The JSON value can also contain a matcher, which will be used to match the
    query parameter value. For example, a semver matcher might look like this:

    ```python
    with_query_parameter_v2(
        handle,
        "Accept-Version",
        0,
        json.dumps({
            "value": "1.2.3",
            "pact:matcher:type": "regex",
            "regex": r"\d+\.\d+\.\d+",
        }),
    )
    ```

    See [IntegrationJson.md](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.22/rust/pact_ffi/IntegrationJson.md)

    Args:
        interaction:
            Handle to the Interaction.

        part:
            The part of the interaction to add the header to (Request or
            Response).

        name:
            The header name. This is case insensitive.

        index:
            The index of the value (starts at 0). You can use this to create a
            header with multiple values.

        value:
            The header value.

            This may be a simple string in which case it will be used as-is, or
            it may be a [JSON matching
            rule](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.22/rust/pact_ffi/IntegrationJson.md).

    Raises:
        RuntimeError:
            If there was an error setting the header.
    """
    success: bool = lib.pactffi_with_header_v2(
        interaction._ref,
        part.value,
        name.encode("utf-8"),
        index,
        value.encode("utf-8"),
    )
    if not success:
        msg = f"The header {name!r} could not be specified for {interaction}."
        raise RuntimeError(msg)


def set_header(
    interaction: InteractionHandle,
    part: InteractionPart,
    name: str,
    value: str,
) -> None:
    """
    Sets a header for the Interaction.

    Note that this function will overwrite any previously set header values.
    Also, this function will not process the value in any way, so matching rules
    and generators can not be configured with it.

    [Rust
    `pactffi_set_header`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_set_header)

    If matching rules are required to be set, use `pactffi_with_header_v2`.

    Args:
        interaction:
            Handle to the Interaction.

        part:
            The part of the interaction to add the header to (Request or
            Response).

        name:
            The header name. This is case insensitive.

        value:
            The header value. This is handled as-is, with no processing.

    Raises:
        RuntimeError:
            If the header could not be set.
    """
    success: bool = lib.pactffi_set_header(
        interaction._ref,
        part.value,
        name.encode("utf-8"),
        value.encode("utf-8"),
    )
    if not success:
        msg = f"The header {name!r} could not be set for {interaction}."
        raise RuntimeError(msg)


def response_status(interaction: InteractionHandle, status: int) -> None:
    """
    Configures the response for the Interaction.

    [Rust
    `pactffi_response_status`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_response_status)

    Args:
        interaction:
            Handle to the Interaction.

        status:
            The response status. Defaults to 200.

    Raises:
        RuntimeError:
            If the response status could not be set.
    """
    success: bool = lib.pactffi_response_status(interaction._ref, status)
    if not success:
        msg = f"The response status {status} could not be set for {interaction}."
        raise RuntimeError(msg)


def response_status_v2(interaction: InteractionHandle, status: str) -> None:
    """
    Configures the response for the Interaction.

    [Rust
    `pactffi_response_status_v2`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_response_status_v2)

    To include matching rules for the status (only statusCode or integer really
    makes sense to use), include the matching rule JSON format with the value as
    a single JSON document. I.e.

    ```python
    response_status_v2(
        handle,
        json.dumps({
            "pact:generator:type": "RandomInt",
            "min": 100,
            "max": 399,
            "pact:matcher:type": "statusCode",
            "status": "nonError",
        }),
    )
    ```

    See [IntegrationJson.md](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.22/rust/pact_ffi/IntegrationJson.md)

    Args:
        interaction:
            Handle to the Interaction.

        status:
            The response status. Defaults to 200.

            This may be a simple string in which case it will be used as-is, or
            it may be a [JSON matching
            rule](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.22/rust/pact_ffi/IntegrationJson.md).

    Raises:
        RuntimeError:
            If the response status could not be set.
    """
    success: bool = lib.pactffi_response_status_v2(
        interaction._ref, status.encode("utf-8")
    )
    if not success:
        msg = f"The response status {status} could not be set for {interaction}."
        raise RuntimeError(msg)


def with_body(
    interaction: InteractionHandle,
    part: InteractionPart,
    content_type: str | None,
    body: str | None,
) -> None:
    """
    Adds the body for the interaction.

    [Rust
    `pactffi_with_body`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_with_body)

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started)

    If the `content_type` is determined as follows, whichever is first:

    - The `content_type` argument to this function
    - The `Content-Type` header for HTTP interaction, or `contentType` metadata
      entry for message interactions.
    - From automatic detection of the body contents.
    - Defaults to `text/plain` as a last resort.

    Furthermore, the `Content-Type` header or `contentType` metadata entry will
    be updated with the above determined content type, _unless_ it is already
    set.

    This function will overwrite the body contents if they exist, with the
    exception of the response part of synchronous message interactions, where a
    new response will be appended.

    Args:
        interaction:
            Handle to the Interaction.

        part:
            The part of the interaction to add the body to (Request or
            Response). This is ignored for asynchronous message interactions.

        content_type:
            The content type of the body, or `None` to use the internal logic.

        body:
            The body contents. For JSON payloads, matching rules can be embedded
            in the body. See
            [IntegrationJson.md](https://github.com/pact-foundation/pact-reference/blob/libpact_ffi-v0.4.22/rust/pact_ffi/IntegrationJson.md).

    Raises:
        RuntimeError:
            If the body could not be specified.
    """
    success: bool = lib.pactffi_with_body(
        interaction._ref,
        part.value,
        content_type.encode("utf-8") if content_type else ffi.NULL,
        body.encode("utf-8") if body else None,
    )
    if not success:
        msg = f"Unable to set body for {interaction}."
        raise RuntimeError(msg)


def with_binary_body(
    interaction: InteractionHandle,
    part: InteractionPart,
    content_type: str | None,
    body: bytes | None,
) -> None:
    """
    Adds the body for the interaction.

    [Rust
    `pactffi_with_binary_body`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_with_binary_body)

    For HTTP and async message interactions, this will overwrite the body. With
    asynchronous messages, the part parameter will be ignored. With synchronous
    messages, the request contents will be overwritten, while a new response
    will be appended to the message.

    Args:
        interaction:
            Handle to the Interaction.

        part:
            The part of the interaction to add the body to (Request or
            Response).

        content_type:
            The content type of the body. Will be ignored if a content type
            header is already set. If `None`, the content type will be set to
            `application/octet-stream`.

        body:
            The body contents. If `None`, the body will be set to null.

    Raises:
        RuntimeError:
            If the body could not be modified.
    """
    if len(gc.get_referrers(body)) == 0:
        warnings.warn(
            "Make sure to assign the body to a variable to avoid having the byte array"
            " modified.",
            UserWarning,
            stacklevel=3,
        )
    success: bool = lib.pactffi_with_binary_body(
        interaction._ref,
        part.value,
        content_type.encode("utf-8") if content_type else ffi.NULL,
        body if body else ffi.NULL,
        len(body) if body else 0,
    )
    if not success:
        msg = f"Unable to set body for {interaction}."
        raise RuntimeError(msg)


def with_binary_file(
    interaction: InteractionHandle,
    part: InteractionPart,
    content_type: str | None,
    body: bytes | None,
) -> None:
    """
    Adds a binary file as the body with the expected content type and contents.

    !!! warning

        This function is deprecated. Use
        [`with_binary_body`][pact.v3.ffi.with_binary_body] in order to set the
        binary body, and use
        [`with_matching_rules`][pact.v3.ffi.with_matching_rules] to set the
        matching rules to ensure that only the content type is being matched.

    Will use a mime type matcher to match the body. Returns false if the
    interaction or Pact can't be modified (i.e. the mock server for it has
    already started)

    [Rust
    `pactffi_with_binary_file`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_with_binary_file)

    For HTTP and async message interactions, this will overwrite the body. With
    asynchronous messages, the part parameter will be ignored. With synchronous
    messages, the request contents will be overwritten, while a new response
    will be appended to the message.

    Args:
        interaction:
            Handle to the Interaction.

        part:
            The part of the interaction to add the body to (Request or
            Response).

        content_type:
            The content type of the body. Will be ignored if a content type
            header is already set.

        body:
            The body contents. If `None`, the body will be set to null.

    Raises:
        RuntimeError:
            If the body could not be set.
    """
    if len(gc.get_referrers(body)) == 0:
        warnings.warn(
            "Make sure to assign the body to a variable to avoid having the byte array"
            " modified.",
            UserWarning,
            stacklevel=3,
        )
    success: bool = lib.pactffi_with_binary_file(
        interaction._ref,
        part.value,
        content_type.encode("utf-8") if content_type else ffi.NULL,
        body if body else ffi.NULL,
        len(body) if body else 0,
    )
    if not success:
        msg = f"Unable to set body for {interaction}."
        raise RuntimeError(msg)


def with_matching_rules(
    interaction: InteractionHandle,
    part: InteractionPart,
    rules: str,
) -> None:
    """
    Add matching rules to the interaction.

    [Rust
    `pactffi_with_matching_rules`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_with_matching_rules)

    This function can be called multiple times, in which case the matching
    rules will be merged.

    Args:
        interaction:
            Handle to the Interaction.

        part:
            Request or response part (if applicable).

        rules:
            JSON string of the matching rules to add to the interaction.

    Raises:
        RuntimeError:
            If the rules could not be added.
    """
    success: bool = lib.pactffi_with_matching_rules(
        interaction._ref,
        part.value,
        rules.encode("utf-8"),
    )
    if not success:
        msg = f"Unable to set matching rules for {interaction}."
        raise RuntimeError(msg)


def with_generators(
    interaction: InteractionHandle,
    part: InteractionPart,
    generators: str,
) -> None:
    """
    Add generators to the interaction.

    [Rust
    `pactffi_with_generators`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_with_generators)

    This function can be called multiple times, in which case the generators
    will be combined (provide they don't clash).

    For synchronous messages which allow multiple responses, the generators will
    be added to all the responses.

    Args:
        interaction:
            Handle to the Interaction.

        part:
            Request or response part (if applicable).

        generators:
            JSON string of the generators to add to the interaction.

    Raises:
        RuntimeError:
            If the generators could not be added.
    """
    success: bool = lib.pactffi_with_generators(
        interaction._ref,
        part.value,
        generators.encode("utf-8"),
    )
    if not success:
        msg = f"Unable to set generators for {interaction}."
        raise RuntimeError(msg)


def with_multipart_file_v2(  # noqa: PLR0913
    interaction: InteractionHandle,
    part: InteractionPart,
    content_type: str | None,
    file: Path | None,
    part_name: str,
    boundary: str | None,
) -> None:
    """
    Adds a binary file as the body as a MIME multipart.

    Will use a mime type matcher to match the body. Returns an error if the
    interaction or Pact can't be modified (i.e. the mock server for it has
    already started) or an error occurs.

    [Rust
    `pactffi_with_multipart_file_v2`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_with_multipart_file_v2)

    This function can be called multiple times. In that case, each subsequent
    call will be appended to the existing multipart body as a new part.

    Args:
        interaction:
            Handle to the Interaction.

        part:
            The part of the interaction to add the body to (Request or
            Response).

        content_type:
            The content type of the body.

        file:
            Path to the file to add. If `None`, the body will be set to null.

        part_name:
            Name for the mime part.

        boundary:
            Boundary for the multipart separation. If `None`, a random string
            will be used.
    """
    result = StringResult(
        lib.pactffi_with_multipart_file_v2(
            interaction._ref,
            part.value,
            content_type.encode("utf-8") if content_type else ffi.NULL,
            str(file).encode("utf-8") if file else ffi.NULL,
            part_name.encode("utf-8"),
            boundary.encode("utf-8") if boundary else ffi.NULL,
        ),
    )
    result.raise_exception()


def with_multipart_file(
    interaction: InteractionHandle,
    part: InteractionPart,
    content_type: str,
    file: str,
    part_name: str,
) -> StringResult:
    """
    Adds a binary file as the body as a MIME multipart.

    Will use a mime type matcher to match the body. Returns an error if the
    interaction or Pact can't be modified (i.e. the mock server for it has
    already started) or an error occurs.

    [Rust
    `pactffi_with_multipart_file`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_with_multipart_file)

    * `interaction` - Interaction handle to set the body for.
    * `part` - Request or response part.
    * `content_type` - Expected content type of the file.
    * `file` - path to the example file
    * `part_name` - name for the mime part

    This function can be called multiple times. In that case, each subsequent
    call will be appended to the existing multipart body as a new part.

    # Safety

    The content type, file path and part name must be valid pointers to UTF-8
    encoded NULL-terminated strings. Passing invalid pointers or pointers to
    strings that are not NULL terminated will lead to undefined behaviour.

    # Error Handling

    If the file path is a NULL pointer, it will set the body contents as as an
    empty mime-part. If the file path does not point to a valid file, or is not
    able to be read, it will return an error result. If the content type is a
    null pointer, or can't be parsed, it will return an error result. Returns an
    error if the interaction or Pact can't be modified (i.e. the mock server for
    it has already started), the interaction is not an HTTP interaction or some
    other error occurs.
    """
    # This function is intentionally left unimplemented. The
    # `with_multipart_file_v2` function should be used instead.
    raise NotImplementedError


def set_key(interaction: InteractionHandle, key: str | None) -> None:
    """
    Sets the key attribute for the interaction.

    [Rust
    `pactffi_set_key`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_set_key)

    Args:
        interaction:
            Interaction handle to modify.

        key:
            Key value. This must be a valid UTF-8 null-terminated string, or
            `None` to clear the key.

    Raises:
        RuntimeError:
            If the key could not be set.
    """
    success: bool = lib.pactffi_set_key(
        interaction._ref,
        key.encode("utf-8") if key else ffi.NULL,
    )
    if not success:
        msg = f"Failed to set key for {interaction}."
        raise RuntimeError(msg)


def set_pending(interaction: InteractionHandle, *, pending: bool) -> None:
    """
    Mark the interaction as pending.

    [Rust
    `pactffi_set_pending`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_set_pending)

    Args:
        interaction:
            Interaction handle to modify.

        pending:
            Boolean value to toggle the pending state of the interaction.

    Raises:
        RuntimeError:
            If the pending status could not be updated.
    """
    success: bool = lib.pactffi_set_pending(interaction._ref, pending)
    if not success:
        msg = f"Failed to update pending status for {interaction}."
        raise RuntimeError(msg)


def set_comment(interaction: InteractionHandle, key: str, value: str | None) -> None:
    """
    Add a comment to the interaction.

    [Rust
    `pactffi_set_comment`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_set_comment)

    Args:
        interaction:
            Interaction handle to set the comments for.

        key:
            Key value

        value:
            Comment value. This may be any valid JSON value, or a `None` to
            clear the comment. Note that a value that deserialize to a JSON null
            will result in a comment being added, with the value being the JSON
            null.

    Raises:
        RuntimeError:
            If the comments could not be updated.
    """
    success: bool = lib.pactffi_set_comment(
        interaction._ref,
        key.encode("utf-8"),
        value.encode("utf-8") if value else ffi.NULL,
    )
    if not success:
        msg = f"Failed to set comment for {interaction}."
        raise RuntimeError(msg)


def add_text_comment(interaction: InteractionHandle, comment: str) -> None:
    """
    Add a text comment to the interaction.

    [Rust
    `pactffi_add_text_comment`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_add_text_comment)

    Args:
        interaction:
            Interaction handle to set the comments for.

        comment:
            Comment value. This is a regular string value.

    Raises:
        RuntimeError:
            If the comment could not be added.
    """
    success: bool = lib.pactffi_add_text_comment(
        interaction._ref,
        comment.encode("utf-8"),
    )
    if not success:
        msg = f"Failed to add text comment for {interaction}."
        raise RuntimeError(msg)


def pact_handle_get_async_message_iter(pact: PactHandle) -> PactAsyncMessageIterator:
    r"""
    Get an iterator over all the asynchronous messages of the Pact.

    The returned iterator needs to be freed with
    `pactffi_pact_sync_message_iter_delete`.

    [Rust
    `pactffi_pact_handle_get_sync_message_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_handle_get_sync_message_iter)

    # Safety

    The iterator contains a copy of the Pact, so it is always safe to use.

    # Error Handling

    On failure, this function will return a NULL pointer.

    This function may fail if any of the Rust strings contain embedded null
    ('\0') bytes.
    """
    return PactAsyncMessageIterator(
        lib.pactffi_pact_handle_get_async_message_iter(pact._ref),
    )


def pact_handle_get_sync_message_iter(pact: PactHandle) -> PactSyncMessageIterator:
    r"""
    Get an iterator over all the synchronous messages of the Pact.

    The returned iterator needs to be freed with
    `pactffi_pact_sync_message_iter_delete`.

    [Rust
    `pactffi_pact_handle_get_sync_message_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_handle_get_sync_message_iter)

    # Safety

    The iterator contains a copy of the Pact, so it is always safe to use.

    # Error Handling

    On failure, this function will return a NULL pointer.

    This function may fail if any of the Rust strings contain embedded null
    ('\0') bytes.
    """
    return PactSyncMessageIterator(
        lib.pactffi_pact_handle_get_sync_message_iter(pact._ref),
    )


def pact_handle_get_sync_http_iter(pact: PactHandle) -> PactSyncHttpIterator:
    r"""
    Get an iterator over all the synchronous HTTP request/response interactions.

    The returned iterator needs to be freed with
    `pactffi_pact_sync_http_iter_delete`.

    [Rust
    `pactffi_pact_handle_get_sync_http_iter`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_handle_get_sync_http_iter)

    # Safety

    The iterator contains a copy of the Pact, so it is always safe to use.

    # Error Handling

    On failure, this function will return a NULL pointer.

    This function may fail if any of the Rust strings contain embedded null
    ('\0') bytes.
    """
    return PactSyncHttpIterator(lib.pactffi_pact_handle_get_sync_http_iter(pact._ref))


def pact_handle_write_file(
    pact: PactHandle,
    directory: Path | str | None,
    *,
    overwrite: bool,
) -> None:
    """
    External interface to write out the pact file.

    [Rust
    `pactffi_pact_handle_write_file`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_pact_handle_write_file)

    This function should be called if all the consumer tests have passed.

    Args:
        pact:
            Handle to a Pact model.

        directory:
            The directory to write the file to. If `None`, the current working
            directory is used.

        overwrite:
            If `True`, the file will be overwritten with the contents of the
            current pact. Otherwise, it will be merged with any existing pact
            file.

    Raises:
        RuntimeError:
            If there was an error writing the pact file.
    """
    ret: int = lib.pactffi_pact_handle_write_file(
        pact._ref,
        str(directory).encode("utf-8") if directory else ffi.NULL,
        overwrite,
    )
    if ret == 0:
        return
    if ret == 1:
        msg = f"The function panicked while writing {pact} to {directory}."
    elif ret == 2:  # noqa: PLR2004
        msg = f"The pact file was not able to be written for {pact}."
    elif ret == 3:  # noqa: PLR2004
        msg = f"The pact for {pact} was not found."
    else:
        msg = f"Unknown error writing {pact} to {directory}."
    raise RuntimeError(msg)


def free_pact_handle(pact: PactHandle) -> None:
    """
    Delete a Pact handle and free the resources used by it.

    [Rust
    `pactffi_free_pact_handle`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_free_pact_handle)

    Raises:
        RuntimeError:
            If the handle could not be freed.
    """
    ret: int = lib.pactffi_free_pact_handle(pact._ref)
    if ret == 0:
        return
    if ret == 1:
        msg = f"{pact} is not valid or does not refer to a valid Pact."
    else:
        msg = f"There was an unknown error freeing {pact}."
    raise RuntimeError(msg)


def verify(args: str) -> int:
    """
    External interface to verifier a provider.

    [Rust `pactffi_verify`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verify)

    * `args` - the same as the CLI interface, except newline delimited

    # Errors

    Errors are returned as non-zero numeric values.

    | Error | Description |
    |-------|-------------|
    | 1 | The verification process failed, see output for errors |
    | 2 | A null pointer was received |
    | 3 | The method panicked |
    | 4 | Invalid arguments were provided to the verification process |

    # Safety

    Exported functions are inherently unsafe. Deal.
    """
    raise NotImplementedError


def verifier_new_for_application() -> VerifierHandle:
    """
    Get a Handle to a newly created verifier.

    By default, verification results will not be published. To enable
    publishing, use
    [`pactffi_verifier_set_publish_options`][pact.v3.ffi.verifier_set_publish_options]
    to set the required values and enable it.

    [Rust
    `pactffi_verifier_new_for_application`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_new_for_application)
    """
    result: cffi.FFI.CData = lib.pactffi_verifier_new_for_application(
        b"pact-python",
        __version__.encode("utf-8"),
    )
    return VerifierHandle(result)


def verifier_shutdown(handle: VerifierHandle) -> None:
    """
    Shutdown the verifier and release all resources.

    [Rust `pactffi_verifier_shutdown`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_shutdown)
    """
    lib.pactffi_verifier_shutdown(handle._ref)


def verifier_set_provider_info(  # noqa: PLR0913
    handle: VerifierHandle,
    name: str | None,
    scheme: str | None,
    host: str | None,
    port: int | None,
    path: str | None,
) -> None:
    """
    Set the provider details for the Pact verifier.

    [Rust
    `pactffi_verifier_set_provider_info`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_set_provider_info)

    Args:
        handle:
            The verifier handle to update.

        name:
            A user-friendly name to describe the provider.

        scheme:
            Determine the scheme to use, typically one of `HTTP` or `HTTPS`.

        host:
            The host of the provider. This may be either a hostname to resolve,
            or an IP address.

        port:
            The port of the provider.

        path:
            The path of the provider.

    If any value is `None`, the default value as determined by the underlying
    FFI library will be used.
    """
    lib.pactffi_verifier_set_provider_info(
        handle._ref,
        name.encode("utf-8") if name else ffi.NULL,
        scheme.encode("utf-8") if scheme else ffi.NULL,
        host.encode("utf-8") if host else ffi.NULL,
        port,
        path.encode("utf-8") if path else ffi.NULL,
    )


def verifier_add_provider_transport(
    handle: VerifierHandle,
    protocol: str | None,
    port: int,
    path: str | None,
    scheme: str | None,
) -> None:
    """
    Adds a new transport for the given provider.

    [Rust
    `pactffi_verifier_add_provider_transport`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_add_provider_transport)

    Args:
        handle:
            The verifier handle to update.

        protocol:
            In this context, the kind of

        port:
            The port of the provider.

        path:
            The path of the provider.

        scheme:
            The scheme to use, typically one of `HTTP` or `HTTPS`.

    If any value is `None`, the default value as determined by the underlying
    FFI library will be used.
    """
    lib.pactffi_verifier_add_provider_transport(
        handle._ref,
        protocol.encode("utf-8") if protocol else ffi.NULL,
        port,
        path.encode("utf-8") if path else ffi.NULL,
        scheme.encode("utf-8") if scheme else ffi.NULL,
    )


def verifier_set_filter_info(
    handle: VerifierHandle,
    filter_description: str | None,
    filter_state: str | None,
    *,
    filter_no_state: bool,
) -> None:
    """
    Set the filters for the Pact verifier.

    [Rust
    `pactffi_verifier_set_filter_info`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_set_filter_info)

    Set filters to narrow down the interactions to verify.

    Args:
        handle:
            The verifier handle to update.

        filter_description:
            A regular expression to filter the interactions by description.

        filter_state:
            A regular expression to filter the interactions by state.

        filter_no_state:
            If `True`, the option to filter by state will be turned on.
    """
    lib.pactffi_verifier_set_filter_info(
        handle._ref,
        filter_description.encode("utf-8") if filter_description else ffi.NULL,
        filter_state.encode("utf-8") if filter_state else ffi.NULL,
        filter_no_state,
    )


def verifier_set_provider_state(
    handle: VerifierHandle,
    url: str,
    *,
    teardown: bool,
    body: bool,
) -> None:
    """
    Set the provider state URL for the Pact verifier.

    [Rust
    `pactffi_verifier_set_provider_state`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_set_provider_state)

    Args:
        handle:
            The verifier handle to update.

        url:
            The URL to use for the provider state.

        teardown:
            If teardown state change requests should be made after an
            interaction is validated.

        body:
            If state change request data should be sent in the body or the
            query.
    """
    lib.pactffi_verifier_set_provider_state(
        handle._ref,
        url.encode("utf-8"),
        teardown,
        body,
    )


def verifier_set_verification_options(
    handle: VerifierHandle,
    *,
    disable_ssl_verification: bool,
    request_timeout: int,
) -> None:
    """
    Set the options used by the verifier when calling the provider.

    [Rust
    `pactffi_verifier_set_verification_options`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_set_verification_options)

    Args:
        handle:
            The verifier handle to update.

        disable_ssl_verification:
            If SSL verification should be disabled.

        request_timeout:
            The timeout for the request in milliseconds.

    Raises:
        RuntimeError:
            If the options could not be set.
    """
    retval: int = lib.pactffi_verifier_set_verification_options(
        handle._ref,
        disable_ssl_verification,
        request_timeout,
    )
    if retval != 0:
        msg = f"Failed to set verification options for {handle}."
        raise RuntimeError(msg)


def verifier_set_coloured_output(
    handle: VerifierHandle,
    *,
    enabled: bool,
) -> None:
    """
    Enables or disables coloured output using ANSI escape codes.

    [Rust
    `pactffi_verifier_set_coloured_output`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_set_coloured_output)

    By default, coloured output is enabled.

    Args:
        handle:
            The verifier handle to update.

        enabled:
            A boolean value to enable or disable coloured output.

    Raises:
        RuntimeError:
            If the coloured output could not be set.
    """
    retval: int = lib.pactffi_verifier_set_coloured_output(
        handle._ref,
        enabled,
    )
    if retval != 0:
        msg = f"Failed to set coloured output for {handle}."
        raise RuntimeError(msg)


def verifier_set_no_pacts_is_error(handle: VerifierHandle, *, enabled: bool) -> None:
    """
    Enables or disables if no pacts are found to verify results in an error.

    [Rust
    `pactffi_verifier_set_no_pacts_is_error`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_set_no_pacts_is_error)

    Args:
        handle:
            The verifier handle to update.

        enabled:
            If `True`, an error will be raised when no pacts are found to verify.

    Raises:
        RuntimeError:
            If the no pacts is error setting could not be set.
    """
    retval: int = lib.pactffi_verifier_set_no_pacts_is_error(
        handle._ref,
        enabled,
    )
    if retval != 0:
        msg = f"Failed to set no pacts is error for {handle}."
        raise RuntimeError(msg)


def verifier_set_publish_options(
    handle: VerifierHandle,
    provider_version: str,
    build_url: str | None,
    provider_tags: list[str] | None,
    provider_branch: str | None,
) -> None:
    """
    Set the options used when publishing verification results to the Broker.

    [Rust
    `pactffi_verifier_set_publish_options`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_set_publish_options)

    Args:
        handle:
            The verifier handle to update.

        provider_version:
            Version of the provider to publish.

        build_url:
            URL to the build which ran the verification.

        provider_tags:
            Collection of tags for the provider.

        provider_branch:
            Name of the branch used for verification.

    Raises:
        RuntimeError:
            If the publish options could not be set.
    """
    retval: int = lib.pactffi_verifier_set_publish_options(
        handle._ref,
        provider_version.encode("utf-8"),
        build_url.encode("utf-8") if build_url else ffi.NULL,
        [ffi.new("char[]", t.encode("utf-8")) for t in provider_tags or []],
        len(provider_tags or []),
        provider_branch.encode("utf-8") if provider_branch else ffi.NULL,
    )
    if retval != 0:
        msg = f"Failed to set publish options for {handle}."
        raise RuntimeError(msg)


def verifier_set_consumer_filters(
    handle: VerifierHandle,
    consumer_filters: Collection[str],
) -> None:
    """
    Set the consumer filters for the Pact verifier.

    [Rust
    `pactffi_verifier_set_consumer_filters`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_set_consumer_filters)
    """
    lib.pactffi_verifier_set_consumer_filters(
        handle._ref,
        [ffi.new("char[]", f.encode("utf-8")) for f in consumer_filters],
        len(consumer_filters),
    )


def verifier_add_custom_header(
    handle: VerifierHandle,
    header_name: str,
    header_value: str,
) -> None:
    """
    Adds a custom header to be added to the requests made to the provider.

    [Rust
    `pactffi_verifier_add_custom_header`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_add_custom_header)
    """
    lib.pactffi_verifier_add_custom_header(
        handle._ref,
        header_name.encode("utf-8"),
        header_value.encode("utf-8"),
    )


def verifier_add_file_source(handle: VerifierHandle, file: str) -> None:
    """
    Adds a Pact file as a source to verify.

    [Rust
    `pactffi_verifier_add_file_source`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_add_file_source)
    """
    lib.pactffi_verifier_add_file_source(handle._ref, file.encode("utf-8"))


def verifier_add_directory_source(handle: VerifierHandle, directory: str) -> None:
    """
    Adds a Pact directory as a source to verify.

    All pacts from the directory that match the provider name will be verified.

    [Rust
    `pactffi_verifier_add_directory_source`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_add_directory_source)

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.

    """
    lib.pactffi_verifier_add_directory_source(handle._ref, directory.encode("utf-8"))


def verifier_url_source(
    handle: VerifierHandle,
    url: str,
    username: str | None,
    password: str | None,
    token: str | None,
) -> None:
    """
    Adds a URL as a source to verify.

    [Rust
    `pactffi_verifier_url_source`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_url_source)

    Args:
        handle:
            The verifier handle to update.

        url:
            The URL to use as a source for the verifier.

        username:
            The username to use when fetching pacts from the URL.

        password:
            The password to use when fetching pacts from the URL.

        token:
            The token to use when fetching pacts from the URL. This will be used
            as a bearer token. It is mutually exclusive with the username and
            password.
    """
    lib.pactffi_verifier_url_source(
        handle._ref,
        url.encode("utf-8"),
        username.encode("utf-8") if username else ffi.NULL,
        password.encode("utf-8") if password else ffi.NULL,
        token.encode("utf-8") if token else ffi.NULL,
    )


def verifier_broker_source(
    handle: VerifierHandle,
    url: str,
    username: str | None,
    password: str | None,
    token: str | None,
) -> None:
    """
    Adds a Pact broker as a source to verify.

    [Rust
    `pactffi_verifier_broker_source`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_broker_source)

    This will fetch all the pact files from the broker that match the provider
    name.

    Args:
        handle:
            The verifier handle to update.

        url:
            The URL to use as a source for the verifier.

        username:
            The username to use when fetching pacts from the broker.

        password:
            The password to use when fetching pacts from the broker.

        token:
            The token to use when fetching pacts from the broker. This will be
            used as a bearer token.
    """
    lib.pactffi_verifier_broker_source(
        handle._ref,
        url.encode("utf-8"),
        username.encode("utf-8") if username else ffi.NULL,
        password.encode("utf-8") if password else ffi.NULL,
        token.encode("utf-8") if token else ffi.NULL,
    )


def verifier_broker_source_with_selectors(  # noqa: PLR0913
    handle: VerifierHandle,
    url: str,
    username: str | None,
    password: str | None,
    token: str | None,
    enable_pending: int,
    include_wip_pacts_since: datetime.date | None,
    provider_tags: list[str],
    provider_branch: str | None,
    consumer_version_selectors: list[str],
    consumer_version_tags: list[str],
) -> None:
    """
    Adds a Pact broker as a source to verify.

    [Rust
    `pactffi_verifier_broker_source_with_selectors`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_broker_source_with_selectors)

    This will fetch all the pact files from the broker that match the provider
    name and the consumer version selectors (See [Consumer Version
    Selectors](https://docs.pact.io/pact_broker/advanced_topics/consumer_version_selectors/)).

    If a username and password is given, then basic authentication will be used
    when fetching the pact file. If a token is provided, then bearer token
    authentication will be used.

    Args:
        handle:
            The verifier handle to update.

        url:
            The URL to use as a source for the verifier.

        username:
            The username to use when fetching pacts from the broker.

        password:
            The password to use when fetching pacts from the broker.

        token:
            The token to use when fetching pacts from the broker. This will be
            used as a bearer token.

        enable_pending:
            If pending pacts should be included in the verification process.

        include_wip_pacts_since:
            The date to use to filter out WIP pacts.

        provider_tags:
            The tags to use to filter the provider pacts.

        provider_branch:
            The branch to use to filter the provider pacts.

        consumer_version_selectors:
            The consumer version selectors to use to filter the consumer pacts.
            This must be passed in as a JSON string.

        consumer_version_tags:
            The tags to use to filter the consumer pacts.
    """
    ret: int = lib.pactffi_verifier_broker_source_with_selectors(
        handle._ref,
        url.encode("utf-8"),
        username.encode("utf-8") if username else ffi.NULL,
        password.encode("utf-8") if password else ffi.NULL,
        token.encode("utf-8") if token else ffi.NULL,
        enable_pending,
        (
            include_wip_pacts_since.isoformat().encode("utf-8")
            if include_wip_pacts_since
            else ffi.NULL
        ),
        [ffi.new("char[]", t.encode("utf-8")) for t in provider_tags],
        len(provider_tags),
        provider_branch.encode("utf-8") if provider_branch else ffi.NULL,
        [ffi.new("char[]", s.encode("utf-8")) for s in consumer_version_selectors],
        len(consumer_version_selectors),
        [ffi.new("char[]", t.encode("utf-8")) for t in consumer_version_tags],
        len(consumer_version_tags),
    )
    if ret == 0:
        return
    if ret == -1:
        msg = "Invalid version selector JSON."
        raise ValueError(msg)
    msg = "Unknown error adding broker source with selectors."
    raise RuntimeError(msg)


def verifier_execute(handle: VerifierHandle) -> None:
    """
    Runs the verification.

    (https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_execute)

    Raises:
        RuntimeError:
            If the verifier could not be executed.
    """
    success: int = lib.pactffi_verifier_execute(handle._ref)
    if success != 0:
        msg = f"Failed to execute verifier for {handle}."
        raise RuntimeError(msg)


def verifier_cli_args() -> str:
    """
    External interface to retrieve the CLI options and arguments.

    This available when calling the CLI interface, returning them as a JSON
    string.

    [Rust
    `pactffi_verifier_cli_args`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_cli_args)

    The purpose is to then be able to use in other languages which wrap the FFI
    library, to implement the same CLI functionality automatically without
    manual maintenance of arguments, help descriptions etc.

    # Example structure

    ```json
    {
      "options": [
        {
          "long": "scheme",
          "help": "Provider URI scheme (defaults to http)",
          "possible_values": [
            "http",
            "https"
          ],
          "default_value": "http"
          "multiple": false,
        },
        {
          "long": "file",
          "short": "f",
          "help": "Pact file to verify (can be repeated)",
          "multiple": true
        },
        {
          "long": "user",
          "help": "Username to use when fetching pacts from URLS",
          "multiple": false,
          "env": "PACT_BROKER_USERNAME"
        }
      ],
      "flags": [
        {
          "long": "disable-ssl-verification",
          "help": "Disables validation of SSL certificates",
          "multiple": false
        }
      ]
    }
    ```

    # Safety

    Exported functions are inherently unsafe.
    """
    raise NotImplementedError


def verifier_logs(handle: VerifierHandle) -> OwnedString:
    """
    Extracts the logs for the verification run.

    [Rust
    `pactffi_verifier_logs`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_logs)

    This needs the memory buffer log sink to be setup before the verification is
    executed. The returned string will need to be freed with the `free_string`
    function call to avoid leaking memory.

    Raises:
        RuntimeError:
            If the logs could not be extracted.
    """
    ptr = lib.pactffi_verifier_logs(handle._ref)
    if ptr == ffi.NULL:
        msg = f"Failed to get logs for {handle}."
        raise RuntimeError(msg)
    return OwnedString(ptr)


def verifier_logs_for_provider(provider_name: str) -> OwnedString:
    """
    Extracts the logs for the verification run for the provider name.

    [Rust
    `pactffi_verifier_logs_for_provider`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_logs_for_provider)

    This needs the memory buffer log sink to be setup before the verification is
    executed. The returned string will need to be freed with the `free_string`
    function call to avoid leaking memory.

    Raises:
        RuntimeError:
            If the logs could not be extracted.
    """
    ptr = lib.pactffi_verifier_logs_for_provider(provider_name.encode("utf-8"))
    if ptr == ffi.NULL:
        msg = f"Failed to get logs for {provider_name}."
        raise RuntimeError(msg)
    return OwnedString(ptr)


def verifier_output(handle: VerifierHandle, strip_ansi: int) -> OwnedString:
    """
    Extracts the standard output for the verification run.

    [Rust
    `pactffi_verifier_output`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_output)

    Args:
        handle:
            The verifier handle to update.

        strip_ansi:
            This parameter controls ANSI escape codes. Setting it to a non-zero
            value will cause the ANSI control codes to be stripped from the
            output.

    Raises:
        RuntimeError:
            If the output could not be extracted.
    """
    ptr = lib.pactffi_verifier_output(handle._ref, strip_ansi)
    if ptr == ffi.NULL:
        msg = f"Failed to get output for {handle}."
        raise RuntimeError(msg)
    return OwnedString(ptr)


def verifier_json(handle: VerifierHandle) -> OwnedString:
    """
    Extracts the verification result as a JSON document.

    [Rust
    `pactffi_verifier_json`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_verifier_json)

    Raises:
        RuntimeError:
            If the JSON could not be extracted.
    """
    ptr = lib.pactffi_verifier_json(handle._ref)
    if ptr == ffi.NULL:
        msg = f"Failed to get JSON for {handle}."
        raise RuntimeError(msg)
    return OwnedString(ptr)


def using_plugin(
    pact: PactHandle,
    plugin_name: str,
    plugin_version: str | None,
) -> None:
    """
    Add a plugin to be used by the test.

    The plugin needs to be installed correctly for this function to work.

    Note that plugins run as separate processes, so will need to be cleaned up
    afterwards by calling [`cleanup_plugins`][pact.v3.ffi.cleanup_plugins]
    otherwise you will have plugin processes left running.

    [Rust
    `pactffi_using_plugin`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_using_plugin)

    Args:
        pact:
            Handle to a Pact model.

        plugin_name:
            Name of the plugin to use.

        plugin_version:
            Version of the plugin to use. If `None`, the latest version will be
            used.

    Raises:
        RuntimeError:
            If the plugin could not be loaded.
    """
    ret: int = lib.pactffi_using_plugin(
        pact._ref,
        plugin_name.encode("utf-8"),
        plugin_version.encode("utf-8") if plugin_version else ffi.NULL,
    )
    if ret == 0:
        return
    if ret == 1:
        msg = f"A general panic was caught: {get_error_message()}"
    elif ret == 2:  # noqa: PLR2004
        msg = f"Failed to load the plugin {plugin_name}."
    elif ret == 3:  # noqa: PLR2004
        msg = f"The Pact handle {pact} is invalid."
    else:
        msg = f"There was an unknown error loading the plugin {plugin_name}."
    raise RuntimeError(msg)


def cleanup_plugins(pact: PactHandle) -> None:
    """
    Decrement the access count on any plugins that are loaded for the Pact.

    This will shutdown any plugins that are no longer required (access count is
    zero).

    [Rust
    `pactffi_cleanup_plugins`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_cleanup_plugins)
    """
    lib.pactffi_cleanup_plugins(pact._ref)


def interaction_contents(
    interaction: InteractionHandle,
    part: InteractionPart,
    content_type: str,
    contents: str,
) -> None:
    """
    Setup the interaction part using a plugin.

    The contents is a JSON string that will be passed on to the plugin to
    configure the interaction part. Refer to the plugin documentation on the
    format of the JSON contents.

    [Rust
    `pactffi_interaction_contents`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_interaction_contents)

    Args:
        interaction:
            Handle to the interaction to configure.

        part:
            The part of the interaction to configure (request or response). It
            is ignored for messages.

        content_type:
            Mime type of the contents.

        contents:
            JSON contents that gets passed to the plugin.

    Raises:
        RuntimeError:
            If the interaction could not be configured
    """
    ret: int = lib.pactffi_interaction_contents(
        interaction._ref,
        part.value,
        content_type.encode("utf-8"),
        contents.encode("utf-8"),
    )
    if ret == 0:
        return
    if ret == 1:
        msg = f"A general panic was caught: {get_error_message()}"
    if ret == 2:  # noqa: PLR2004
        msg = "The mock server has already been started."
    if ret == 3:  # noqa: PLR2004
        msg = f"The interaction handle {interaction} is invalid."
    if ret == 4:  # noqa: PLR2004
        msg = f"The content type {content_type} is not valid."
    if ret == 5:  # noqa: PLR2004
        msg = "The content is not valid JSON."
    if ret == 6:  # noqa: PLR2004
        msg = f"The plugin returned an error: {get_error_message()}"
    else:
        msg = f"There was an unknown error configuring the interaction: {ret}"
    raise RuntimeError(msg)


def matches_string_value(
    matching_rule: MatchingRule,
    expected_value: str,
    actual_value: str,
    cascaded: int,
) -> OwnedString:
    """
    Determines if the string value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_string_value`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matches_string_value)

    * matching_rule - pointer to a matching rule
    * expected_value - value we expect to get as a NULL terminated string
    * actual_value - value to match as a NULL terminated string
    * cascaded - if the matching rule has been cascaded from a parent. 0 ==
      false, 1 == true

    # Safety

    The matching rule pointer must be a valid pointer, and the value parameters
    must be valid pointers to a NULL terminated strings.
    """
    raise NotImplementedError


def matches_u64_value(
    matching_rule: MatchingRule,
    expected_value: int,
    actual_value: int,
    cascaded: int,
) -> OwnedString:
    """
    Determines if the unsigned integer value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_u64_value`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matches_u64_value)

    * matching_rule - pointer to a matching rule
    * expected_value - value we expect to get
    * actual_value - value to match
    * cascaded - if the matching rule has been cascaded from a parent. 0 ==
      false, 1 == true

    # Safety

    The matching rule pointer must be a valid pointer.
    """
    raise NotImplementedError


def matches_i64_value(
    matching_rule: MatchingRule,
    expected_value: int,
    actual_value: int,
    cascaded: int,
) -> OwnedString:
    """
    Determines if the signed integer value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_i64_value`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matches_i64_value)

    * matching_rule - pointer to a matching rule
    * expected_value - value we expect to get
    * actual_value - value to match
    * cascaded - if the matching rule has been cascaded from a parent. 0 ==
      false, 1 == true

    # Safety

    The matching rule pointer must be a valid pointer.
    """
    raise NotImplementedError


def matches_f64_value(
    matching_rule: MatchingRule,
    expected_value: float,
    actual_value: float,
    cascaded: int,
) -> OwnedString:
    """
    Determines if the floating point value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_f64_value`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matches_f64_value)

    * matching_rule - pointer to a matching rule
    * expected_value - value we expect to get
    * actual_value - value to match
    * cascaded - if the matching rule has been cascaded from a parent. 0 ==
      false, 1 == true

    # Safety

    The matching rule pointer must be a valid pointer.
    """
    raise NotImplementedError


def matches_bool_value(
    matching_rule: MatchingRule,
    expected_value: int,
    actual_value: int,
    cascaded: int,
) -> OwnedString:
    """
    Determines if the boolean value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_bool_value`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matches_bool_value)

    * matching_rule - pointer to a matching rule
    * expected_value - value we expect to get, 0 == false and 1 == true
    * actual_value - value to match, 0 == false and 1 == true
    * cascaded - if the matching rule has been cascaded from a parent. 0 ==
      false, 1 == true

    # Safety

    The matching rule pointer must be a valid pointer.
    """
    raise NotImplementedError


def matches_binary_value(  # noqa: PLR0913
    matching_rule: MatchingRule,
    expected_value: str,
    expected_value_len: int,
    actual_value: str,
    actual_value_len: int,
    cascaded: int,
) -> OwnedString:
    """
    Determines if the binary value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_binary_value`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matches_binary_value)

    * matching_rule - pointer to a matching rule
    * expected_value - value we expect to get
    * expected_value_len - length of the expected value bytes
    * actual_value - value to match
    * actual_value_len - length of the actual value bytes
    * cascaded - if the matching rule has been cascaded from a parent. 0 ==
      false, 1 == true

    # Safety

    The matching rule, expected value and actual value pointers must be a valid
    pointers. expected_value_len and actual_value_len must contain the number of
    bytes that the value pointers point to. Passing invalid lengths can lead to
    undefined behaviour.
    """
    raise NotImplementedError


def matches_json_value(
    matching_rule: MatchingRule,
    expected_value: str,
    actual_value: str,
    cascaded: int,
) -> OwnedString:
    """
    Determines if the JSON value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_json_value`](https://docs.rs/pact_ffi/0.4.22/pact_ffi/?search=pactffi_matches_json_value)

    * matching_rule - pointer to a matching rule
    * expected_value - value we expect to get as a NULL terminated string
    * actual_value - value to match as a NULL terminated string
    * cascaded - if the matching rule has been cascaded from a parent. 0 ==
      false, 1 == true

    # Safety

    The matching rule pointer must be a valid pointer, and the value parameters
    must be valid pointers to a NULL terminated strings.
    """
    raise NotImplementedError
