"""
Python bindings for the Pact FFI.

This module provides a Python interface to the Pact FFI. It is a thin wrapper
around the C API, and is intended to be used by the Pact Python client library
to provide a Pythonic interface to Pact.

This module is not intended to be used directly by Pact users. Pact users should
use the Pact Python client library instead. No guarantees are made about the
stability of this module's API.

## Developer Notes

This modules should provide the following only:

-   Basic Enum classes
-   Simple wrappers around functions, including the casting of input and output
    values between the high level Python types and the low level C types.

These low-level functions may then be combined into higher level classes and
modules.

During initial implementation, a lot of these functions will simply raise a
`NotImplementedError`.

For those unfamiliar with CFFI, please make sure to read the [CFFI
documentation](https://cffi.readthedocs.io/en/latest/using.html).
"""
# ruff: noqa: ARG001 (unused-function-argument)
# ruff: noqa: A002 (builtin-argument-shadowing)
# ruff: noqa: D101 (undocumented-public-class)

import warnings
from enum import Enum
from typing import List

from ._ffi import ffi, lib  # type: ignore[import]

# The follow types are classes defined in the Rust code. Ultimately, a Python
# alternative should be implemented, but for now, the follow lines only serve
# to inform the type checker of the existence of these types.


class AsynchronousMessage:
    ...


class Consumer:
    ...


class Generator:
    ...


class GeneratorCategoryIterator:
    ...


class GeneratorKeyValuePair:
    ...


class HttpRequest:
    ...


class HttpResponse:
    ...


class InteractionHandle:
    ...


class MatchingRule:
    ...


class MatchingRuleCategoryIterator:
    ...


class MatchingRuleDefinitionResult:
    ...


class MatchingRuleIterator:
    ...


class MatchingRuleKeyValuePair:
    ...


class MatchingRuleResult:
    ...


class Message:
    ...


class MessageContents:
    ...


class MessageHandle:
    ...


class MessageMetadataIterator:
    ...


class MessageMetadataPair:
    ...


class MessagePact:
    ...


class MessagePactHandle:
    ...


class MessagePactMessageIterator:
    ...


class MessagePactMetadataIterator:
    ...


class MessagePactMetadataTriple:
    ...


class Mismatch:
    ...


class Mismatches:
    ...


class MismatchesIterator:
    ...


class Pact:
    ...


class PactHandle:
    ...


class PactInteraction:
    ...


class PactInteractionIterator:
    ...


class PactMessageIterator:
    ...


class PactSyncHttpIterator:
    ...


class PactSyncMessageIterator:
    ...


class Provider:
    ...


class ProviderState:
    ...


class ProviderStateIterator:
    ...


class ProviderStateParamIterator:
    ...


class ProviderStateParamPair:
    ...


class SynchronousHttp:
    ...


class SynchronousMessage:
    ...


class VerifierHandle:
    ...


class ExpressionValueType(Enum):
    """
    Expression Value Type.

    [Rust `ExpressionValueType`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/models/expressions/enum.ExpressionValueType.html)
    """

    UNKNOWN = lib.ExpressionValueType_Unknown
    STRING = lib.ExpressionValueType_String
    NUMBER = lib.ExpressionValueType_Number
    INTEGER = lib.ExpressionValueType_Integer
    DECIMAL = lib.ExpressionValueType_Decimal
    BOOLEAN = lib.ExpressionValueType_Boolean


class GeneratorCategory(Enum):
    """
    Generator Category.

    [Rust `GeneratorCategory`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/models/generators/enum.GeneratorCategory.html)
    """

    METHOD = lib.GeneratorCategory_METHOD
    PATH = lib.GeneratorCategory_PATH
    HEADER = lib.GeneratorCategory_HEADER
    QUERY = lib.GeneratorCategory_QUERY
    BODY = lib.GeneratorCategory_BODY
    STATUS = lib.GeneratorCategory_STATUS
    METADATA = lib.GeneratorCategory_METADATA


class InteractionPart(Enum):
    """
    Interaction Part.

    [Rust `InteractionPart`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/mock_server/handles/enum.InteractionPart.html)
    """

    REQUEST = lib.InteractionPart_Request
    RESPONSE = lib.InteractionPart_Response


class LevelFilter(Enum):
    """Level Filter."""

    OFF = lib.LevelFilter_Off
    ERROR = lib.LevelFilter_Error
    WARN = lib.LevelFilter_Warn
    INFO = lib.LevelFilter_Info
    DEBUG = lib.LevelFilter_Debug
    TRACE = lib.LevelFilter_Trace


class MatchingRuleCategory(Enum):
    """
    Matching Rule Category.

    [Rust `MatchingRuleCategory`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/models/matching_rules/enum.MatchingRuleCategory.html)
    """

    METHOD = lib.MatchingRuleCategory_METHOD
    PATH = lib.MatchingRuleCategory_PATH
    HEADER = lib.MatchingRuleCategory_HEADER
    QUERY = lib.MatchingRuleCategory_QUERY
    BODY = lib.MatchingRuleCategory_BODY
    STATUS = lib.MatchingRuleCategory_STATUS
    CONTENST = lib.MatchingRuleCategory_CONTENTS
    METADATA = lib.MatchingRuleCategory_METADATA


class PactSpecification(Enum):
    """
    Pact Specification.

    [Rust `PactSpecification`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/models/pact_specification/enum.PactSpecification.html)
    """

    UNKNOWN = lib.PactSpecification_Unknown
    V1 = lib.PactSpecification_V1
    V1_1 = lib.PactSpecification_V1_1
    V2 = lib.PactSpecification_V2
    V3 = lib.PactSpecification_V3
    V4 = lib.PactSpecification_V4


class StringResult(Enum):
    """
    String Result.

    [Rust `StringResult`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/mock_server/enum.StringResult.html)
    """

    FAILED = lib.StringResult_Failed
    Ok = lib.StringResult_Ok


def version() -> str:
    """
    Wraps a Pact model struct.

    [Rust `pactffi_version`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_version)
    """
    return ffi.string(lib.pactffi_version()).decode("utf-8")


def init(log_env_var: str) -> None:
    """
    Initialise the mock server library.

    This can provide an environment variable name to use to set the log levels.
    This function should only be called once, as it tries to install a global
    tracing subscriber.

    [Rust
    `pactffi_init`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_init)

    # Safety

    log_env_var must be a valid NULL terminated UTF-8 string.
    """
    raise NotImplementedError


def init_with_log_level(level: str) -> None:
    """
    Initialises logging, and sets the log level explicitly.

    This function should only be called once, as it tries to install a global
    tracing subscriber.

    [Rust
    `pactffi_init_with_log_level`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_init_with_log_level)

    # Safety

    Exported functions are inherently unsafe.
    """
    raise NotImplementedError


def enable_ansi_support() -> None:
    """
    Enable ANSI coloured output on Windows.

    On non-Windows platforms, this function is a no-op.

    [Rust
    `pactffi_enable_ansi_support`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_enable_ansi_support)

    # Safety

    This function is safe.
    """
    raise NotImplementedError


def log_message(source: str, log_level: str, message: str) -> None:
    """
    Log using the shared core logging facility.

    [Rust
    `pactffi_log_message`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_log_message)

    This is useful for callers to have a single set of logs.

    - `source`: String. The source of the log, such as the class or caller
      framework to disambiguate log lines from the rust logging (e.g.  pact_go)
    - `log_level`: String. One of TRACE, DEBUG, INFO, WARN, ERROR
    - `message`: Message to log

    # Safety

    This function will fail if any of the pointers passed to it are invalid.
    """
    raise NotImplementedError


def match_message(msg_1: Message, msg_2: Message) -> Mismatches:
    """
    Match a pair of messages, producing a collection of mismatches.

    If the messages match, the returned collection will be empty.

    [Rust
    `pactffi_match_message`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_match_message)
    """
    raise NotImplementedError


def mismatches_get_iter(mismatches: Mismatches) -> MismatchesIterator:
    """
    Get an iterator over mismatches.

    [Rust
    `pactffi_mismatches_get_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_mismatches_get_iter)
    """
    raise NotImplementedError


def mismatches_delete(mismatches: Mismatches) -> None:
    """
    Delete mismatches.

    [Rust `pactffi_mismatches_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_mismatches_delete)
    """
    raise NotImplementedError


def mismatches_iter_next(iter: MismatchesIterator) -> Mismatch:
    """
    Get the next mismatch from a mismatches iterator.

    [Rust `pactffi_mismatches_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_mismatches_iter_next)

    Returns a null pointer if no mismatches remain.
    """
    raise NotImplementedError


def mismatches_iter_delete(iter: MismatchesIterator) -> None:
    """
    Delete a mismatches iterator when you're done with it.

    [Rust `pactffi_mismatches_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_mismatches_iter_delete)
    """
    raise NotImplementedError


def mismatch_to_json(mismatch: Mismatch) -> str:
    """
    Get a JSON representation of the mismatch.

    [Rust `pactffi_mismatch_to_json`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_mismatch_to_json)
    """
    raise NotImplementedError


def mismatch_type(mismatch: Mismatch) -> str:
    """
    Get the type of a mismatch.

    [Rust `pactffi_mismatch_type`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_mismatch_type)
    """
    raise NotImplementedError


def mismatch_summary(mismatch: Mismatch) -> str:
    """
    Get a summary of a mismatch.

    [Rust `pactffi_mismatch_summary`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_mismatch_summary)
    """
    raise NotImplementedError


def mismatch_description(mismatch: Mismatch) -> str:
    """
    Get a description of a mismatch.

    [Rust `pactffi_mismatch_description`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_mismatch_description)
    """
    raise NotImplementedError


def mismatch_ansi_description(mismatch: Mismatch) -> str:
    """
    Get an ANSI-compatible description of a mismatch.

    [Rust `pactffi_mismatch_ansi_description`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_mismatch_ansi_description)
    """
    raise NotImplementedError


def get_error_message(buffer: str, length: int) -> int:
    """
    Provide the error message from `LAST_ERROR` to the calling C code.

    [Rust
    `pactffi_get_error_message`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_get_error_message)

    This function should be called after any other function in the pact_matching
    FFI indicates a failure with its own error message, if the caller wants to
    get more context on why the error happened.

    Do note that this error-reporting mechanism only reports the top-level error
    message, not any source information embedded in the original Rust error
    type. If you want more detailed information for debugging purposes, use the
    logging interface.

    # Params

    - `buffer`: a pointer to an array of `char` of sufficient length to hold the
      error message.
    - `length`: an int providing the length of the `buffer`.

    # Return Codes

    - The number of bytes written to the provided buffer, which may be zero if
      there is no last error.
    - `-1` if the provided buffer is a null pointer.
    - `-2` if the provided buffer length is too small for the error message.
    - `-3` if the write failed for some other reason.
    - `-4` if the error message had an interior NULL

    # Notes

    Note that this function zeroes out any excess in the provided buffer.

    # Error Handling

    The return code must be checked for one of the negative number error codes
    before the buffer is used. If an error code is present, the buffer may not
    be in a usable state.

    If the buffer is longer than needed for the error message, the excess space
    will be zeroed as a safety mechanism. This is slightly less efficient than
    leaving the contents of the buffer alone, but the difference is expected to
    be negligible in practice.
    """
    raise NotImplementedError


def log_to_stdout(level_filter: LevelFilter) -> int:
    """
    Convenience function to direct all logging to stdout.

    [Rust `pactffi_log_to_stdout`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_log_to_stdout)
    """
    raise NotImplementedError


def log_to_stderr(level_filter: LevelFilter) -> int:
    """
    Convenience function to direct all logging to stderr.

    [Rust `pactffi_log_to_stderr`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_log_to_stderr)
    """
    raise NotImplementedError


def log_to_file(file_name: str, level_filter: LevelFilter) -> int:
    """
    Convenience function to direct all logging to a file.

    [Rust
    `pactffi_log_to_file`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_log_to_file)

    # Safety

    This function will fail if the file_name pointer is invalid or does not
    point to a NULL terminated string.
    """
    raise NotImplementedError


def log_to_buffer(level_filter: LevelFilter) -> int:
    """
    Convenience function to direct all logging to a task local memory buffer.

    [Rust `pactffi_log_to_buffer`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_log_to_buffer)
    """
    raise NotImplementedError


def logger_init() -> None:
    """
    Initialize the FFI logger with no sinks.

    [Rust `pactffi_logger_init`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_logger_init)

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
    `pactffi_logger_attach_sink`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_logger_attach_sink)

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
    `pactffi_logger_apply`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_logger_apply)

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
    `pactffi_fetch_log_buffer`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_fetch_log_buffer)

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
    `pactffi_parse_pact_json`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_parse_pact_json)

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

    [Rust `pactffi_pact_model_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_model_delete)
    """
    raise NotImplementedError


def pact_model_interaction_iterator(pact: Pact) -> PactInteractionIterator:
    """
    Returns an iterator over all the interactions in the Pact.

    [Rust
    `pactffi_pact_model_interaction_iterator`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_model_interaction_iterator)

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

    [Rust `pactffi_pact_spec_version`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_spec_version)
    """
    raise NotImplementedError


def pact_interaction_delete(interaction: PactInteraction) -> None:
    """
    Frees the memory used by the Pact interaction model.

    [Rust `pactffi_pact_interaction_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_interaction_delete)
    """
    raise NotImplementedError


def async_message_new() -> AsynchronousMessage:
    """
    Get a mutable pointer to a newly-created default message on the heap.

    [Rust `pactffi_async_message_new`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_async_message_new)

    # Safety

    This function is safe.

    # Error Handling

    Returns NULL on error.
    """
    raise NotImplementedError


def async_message_delete(message: AsynchronousMessage) -> None:
    """
    Destroy the `AsynchronousMessage` being pointed to.

    [Rust `pactffi_async_message_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_async_message_delete)
    """
    raise NotImplementedError


def async_message_get_contents(message: AsynchronousMessage) -> MessageContents:
    """
    Get the message contents of an `AsynchronousMessage` as a `MessageContents` pointer.

    [Rust
    `pactffi_async_message_get_contents`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_async_message_get_contents)

    # Safety

    The data pointed to by the pointer this function returns will be deleted
    when the message is deleted. Trying to use if after the message is deleted
    will result in undefined behaviour.

    # Error Handling

    If the message is NULL, returns NULL.
    """
    raise NotImplementedError


def async_message_get_contents_str(message: AsynchronousMessage) -> str:
    """
    Get the message contents of an `AsynchronousMessage` in string form.

    [Rust `pactffi_async_message_get_contents_str`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_async_message_get_contents_str)

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
    `pactffi_async_message_set_contents_str`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_async_message_set_contents_str)

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
    `pactffi_async_message_get_contents_length`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_async_message_get_contents_length)

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
    `pactffi_async_message_get_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_async_message_get_contents_bin)

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
    `pactffi_async_message_set_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_async_message_set_contents_bin)

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
    `pactffi_async_message_get_description`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_async_message_get_description)

    # Safety

    The returned string must be deleted with `pactffi_string_delete`.

    Since it is a copy, the returned string may safely outlive the
    `AsynchronousMessage`.

    # Errors

    On failure, this function will return a NULL pointer.

    This function may fail if the Rust string contains embedded null ('\0')
    bytes.
    """
    raise NotImplementedError


def async_message_set_description(
    message: AsynchronousMessage,
    description: str,
) -> int:
    """
    Write the `description` field on the `AsynchronousMessage`.

    [Rust `pactffi_async_message_set_description`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_async_message_set_description)

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
    `pactffi_async_message_get_provider_state`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_async_message_get_provider_state)

    # Safety

    The returned structure must be deleted with `provider_state_delete`.

    Since it is a copy, the returned structure may safely outlive the
    `AsynchronousMessage`.

    # Error Handling

    On failure, this function will return a variant other than Success.

    This function may fail if the index requested is out of bounds, or if any of
    the Rust strings contain embedded null ('\0') bytes.
    """
    raise NotImplementedError


def async_message_get_provider_state_iter(
    message: AsynchronousMessage,
) -> ProviderStateIterator:
    """
    Get an iterator over provider states.

    [Rust `pactffi_async_message_get_provider_state_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_async_message_get_provider_state_iter)

    # Safety

    The underlying data must not change during iteration.

    # Error Handling

    Returns NULL if an error occurs.
    """
    raise NotImplementedError


def consumer_get_name(consumer: Consumer) -> str:
    r"""
    Get a copy of this consumer's name.

    [Rust `pactffi_consumer_get_name`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_consumer_get_name)

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
    `pactffi_pact_get_consumer`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_get_consumer)

    # Errors

    This function will fail if it is passed a NULL pointer. In the case of
    error, a NULL pointer will be returned.
    """
    raise NotImplementedError


def pact_consumer_delete(consumer: Consumer) -> None:
    """
    Frees the memory used by the Pact consumer.

    [Rust `pactffi_pact_consumer_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_consumer_delete)
    """
    raise NotImplementedError


def message_contents_get_contents_str(contents: MessageContents) -> str:
    """
    Get the message contents in string form.

    [Rust `pactffi_message_contents_get_contents_str`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_contents_get_contents_str)

    # Safety

    The returned string must be deleted with `pactffi_string_delete`.

    The returned string can outlive the message.

    # Error Handling

    If the message contents is NULL, returns NULL. If the body of the message
    is missing, then this function also returns NULL. This means there's
    no mechanism to differentiate with this function call alone between
    a NULL message and a missing message body.
    """
    raise NotImplementedError


def message_contents_set_contents_str(
    contents: MessageContents,
    contents_str: str,
    content_type: str,
) -> None:
    """
    Sets the contents of the message as a string.

    [Rust
    `pactffi_message_contents_set_contents_str`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_contents_set_contents_str)

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

    [Rust `pactffi_message_contents_get_contents_length`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_contents_get_contents_length)

    # Safety

    This function is safe.

    # Error Handling

    If the message is NULL, returns 0. If the body of the message
    is missing, then this function also returns 0.
    """
    raise NotImplementedError


def message_contents_get_contents_bin(contents: MessageContents) -> str:
    """
    Get the contents of a message as a pointer to an array of bytes.

    [Rust
    `pactffi_message_contents_get_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_contents_get_contents_bin)

    # Safety

    The number of bytes in the buffer will be returned by
    `pactffi_message_contents_get_contents_length`. It is safe to use the
    pointer while the message is not deleted or changed. Using the pointer after
    the message is mutated or deleted may lead to undefined behaviour.

    # Error Handling

    If the message is NULL, returns NULL. If the body of the message is missing,
    then this function also returns NULL.
    """
    raise NotImplementedError


def message_contents_set_contents_bin(
    contents: MessageContents,
    contents_bin: str,
    len: int,
    content_type: str,
) -> None:
    """
    Sets the contents of the message as an array of bytes.

    [Rust
    `pactffi_message_contents_set_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_contents_set_contents_bin)

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
    `pactffi_message_contents_get_metadata_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_contents_get_metadata_iter)

    The returned pointer must be deleted with
    `pactffi_message_metadata_iter_delete` when done with it.

    # Safety

    This iterator carries a pointer to the message contents, and must not
    outlive the message.

    The message metadata also must not be modified during iteration. If it is,
    the old iterator must be deleted and a new iterator created.

    # Error Handling

    On failure, this function will return a NULL pointer.

    This function may fail if any of the Rust strings contain embedded null
    ('\0') bytes.
    """
    raise NotImplementedError


def message_contents_get_matching_rule_iter(
    contents: MessageContents,
    category: MatchingRuleCategory,
) -> MatchingRuleCategoryIterator:
    r"""
    Get an iterator over the matching rules for a category of a message.

    [Rust
    `pactffi_message_contents_get_matching_rule_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_contents_get_matching_rule_iter)

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
    raise NotImplementedError


def request_contents_get_matching_rule_iter(
    request: HttpRequest,
    category: MatchingRuleCategory,
) -> MatchingRuleCategoryIterator:
    r"""
    Get an iterator over the matching rules for a category of an HTTP request.

    [Rust `pactffi_request_contents_get_matching_rule_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_request_contents_get_matching_rule_iter)

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

    [Rust `pactffi_response_contents_get_matching_rule_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_response_contents_get_matching_rule_iter)

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
    `pactffi_message_contents_get_generators_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_contents_get_generators_iter)

    The returned pointer must be deleted with `pactffi_generators_iter_delete`
    when done with it.

    # Safety

    The iterator contains a copy of the data, so is safe to use when the message
    or message contents has been deleted.

    # Error Handling

    On failure, this function will return a NULL pointer.
    """
    raise NotImplementedError


def request_contents_get_generators_iter(
    request: HttpRequest,
    category: GeneratorCategory,
) -> GeneratorCategoryIterator:
    """
    Get an iterator over the generators for a category of an HTTP request.

    [Rust
    `pactffi_request_contents_get_generators_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_request_contents_get_generators_iter)

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
    `pactffi_response_contents_get_generators_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_response_contents_get_generators_iter)

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

    The MatchingRuleDefition contains the example value, and matching rules and
    any generator.

    [Rust
    `pactffi_parse_matcher_definition`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_parse_matcher_definition)

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
    `pactffi_matcher_definition_error`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matcher_definition_error)
    """
    raise NotImplementedError


def matcher_definition_value(definition: MatchingRuleDefinitionResult) -> str:
    """
    Returns the value from parsing a matching definition expression.

    If there was an error, it will return a NULL pointer, otherwise returns the
    value as a NULL-terminated string. The returned string must be freed using
    the `pactffi_string_delete` function once done with it.

    [Rust
    `pactffi_matcher_definition_value`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matcher_definition_value)

    Note that different expressions values can have types other than a string.
    Use `pactffi_matcher_definition_value_type` to get the actual type of the
    value. This function will always return the string representation of the
    value.
    """
    raise NotImplementedError


def matcher_definition_delete(definition: MatchingRuleDefinitionResult) -> None:
    """
    Frees the memory used by the result of parsing the matching definition expression.

    [Rust `pactffi_matcher_definition_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matcher_definition_delete)
    """
    raise NotImplementedError


def matcher_definition_generator(definition: MatchingRuleDefinitionResult) -> Generator:
    """
    Returns the generator from parsing a matching definition expression.

    If there was an error or there is no associated generator, it will return a
    NULL pointer, otherwise returns the generator as a pointer.

    [Rust
    `pactffi_matcher_definition_generator`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matcher_definition_generator)

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
    `pactffi_matcher_definition_value_type`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matcher_definition_value_type)
    """
    raise NotImplementedError


def matching_rule_iter_delete(iter: MatchingRuleIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust `pactffi_matching_rule_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matching_rule_iter_delete)
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
    `pactffi_matcher_definition_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matcher_definition_iter)

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
    `pactffi_matching_rule_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matching_rule_iter_next)

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
    `pactffi_matching_rule_id`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matching_rule_id)

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
    `pactffi_matching_rule_value`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matching_rule_value)

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
    `pactffi_matching_rule_pointer`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matching_rule_pointer)

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
    `pactffi_matching_rule_reference_name`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matching_rule_reference_name)

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


def validate_datetime(value: str, format: str) -> int:
    """
    Validates the date/time value against the date/time format string.

    If the value is valid, this function will return a zero status code
    (EXIT_SUCCESS). If the value is not valid, will return a value of 1
    (EXIT_FAILURE) and set the error message which can be retrieved with
    `pactffi_get_error_message`.

    [Rust
    `pactffi_validate_datetime`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_validate_datetime)

    # Errors If the function receives a panic, it will return 2 and the message
    associated with the panic can be retrieved with `pactffi_get_error_message`.

    # Safety

    This function is safe as long as the value and format parameters point to
    valid NULL-terminated strings.
    """
    raise NotImplementedError


def generator_to_json(generator: Generator) -> str:
    """
    Get the JSON form of the generator.

    [Rust
    `pactffi_generator_to_json`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_generator_to_json)

    The returned string must be deleted with `pactffi_string_delete`.

    # Safety

    This function will fail if it is passed a NULL pointer, or the owner of the
    generator has been deleted.
    """
    raise NotImplementedError


def generator_generate_string(generator: Generator, context_json: str) -> str:
    """
    Generate a string value using the provided generator.

    An optional JSON payload containing any generator context ca be given. The
    context value is used for generators like `MockServerURL` (which should
    contain details about the running mock server) and `ProviderStateGenerator`
    (which should be the values returned from the Provider State callback
    function).

    [Rust
    `pactffi_generator_generate_string`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_generator_generate_string)

    If anything goes wrong, it will return a NULL pointer.
    """
    raise NotImplementedError


def generator_generate_integer(generator: Generator, context_json: str) -> int:
    """
    Generate an integer value using the provided generator.

    An optional JSON payload containing any generator context can be given. The
    context value is used for generators like `ProviderStateGenerator` (which
    should be the values returned from the Provider State callback function).

    [Rust
    `pactffi_generator_generate_integer`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_generator_generate_integer)

    If anything goes wrong or the generator is not a type that can generate an
    integer value, it will return a zero value.
    """
    raise NotImplementedError


def generators_iter_delete(iter: GeneratorCategoryIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust
    `pactffi_generators_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_generators_iter_delete)
    """
    raise NotImplementedError


def generators_iter_next(iter: GeneratorCategoryIterator) -> GeneratorKeyValuePair:
    """
    Get the next path and generator out of the iterator, if possible.

    [Rust
    `pactffi_generators_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_generators_iter_next)

    The returned pointer must be deleted with
    `pactffi_generator_iter_pair_delete`.

    # Safety

    The underlying data is owned by the `GeneratorKeyValuePair`, so is always
    safe to use.

    # Error Handling

    If no further data is present, returns NULL.
    """
    raise NotImplementedError


def generators_iter_pair_delete(pair: GeneratorKeyValuePair) -> None:
    """
    Free a pair of key and value returned from `pactffi_generators_iter_next`.

    [Rust
    `pactffi_generators_iter_pair_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_generators_iter_pair_delete)
    """
    raise NotImplementedError


def sync_http_new() -> SynchronousHttp:
    """
    Get a mutable pointer to a newly-created default interaction on the heap.

    [Rust `pactffi_sync_http_new`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_new)

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
    `pactffi_sync_http_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_delete)
    """
    raise NotImplementedError


def sync_http_get_request(interaction: SynchronousHttp) -> HttpRequest:
    """
    Get the request of a `SynchronousHttp` interaction.

    [Rust
    `pactffi_sync_http_get_request`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_get_request)

    # Safety

    The data pointed to by the pointer this function returns will be deleted
    when the interaction is deleted. Trying to use if after the interaction is
    deleted will result in undefined behaviour.

    # Error Handling

    If the interaction is NULL, returns NULL.
    """
    raise NotImplementedError


def sync_http_get_request_contents(interaction: SynchronousHttp) -> str:
    """
    Get the request contents of a `SynchronousHttp` interaction in string form.

    [Rust
    `pactffi_sync_http_get_request_contents`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_get_request_contents)

    # Safety

    The returned string must be deleted with `pactffi_string_delete`.

    The returned string can outlive the interaction.

    # Error Handling

    If the interaction is NULL, returns NULL. If the body of the request is
    missing, then this function also returns NULL. This means there's no
    mechanism to differentiate with this function call alone between a NULL body
    and a missing body.
    """
    raise NotImplementedError


def sync_http_set_request_contents(
    interaction: SynchronousHttp,
    contents: str,
    content_type: str,
) -> None:
    """
    Sets the request contents of the interaction.

    [Rust
    `pactffi_sync_http_set_request_contents`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_set_request_contents)

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
    `pactffi_sync_http_get_request_contents_length`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_get_request_contents_length)

    # Safety

    This function is safe.

    # Error Handling

    If the interaction is NULL, returns 0. If the body of the request is
    missing, then this function also returns 0.
    """
    raise NotImplementedError


def sync_http_get_request_contents_bin(interaction: SynchronousHttp) -> bytes:
    """
    Get the request contents of a `SynchronousHttp` interaction as bytes.

    [Rust
    `pactffi_sync_http_get_request_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_get_request_contents_bin)

    # Safety

    The number of bytes in the buffer will be returned by
    `pactffi_sync_http_get_request_contents_length`. It is safe to use the
    pointer while the interaction is not deleted or changed. Using the pointer
    after the interaction is mutated or deleted may lead to undefined behaviour.

    # Error Handling

    If the interaction is NULL, returns NULL. If the body of the request is
    missing, then this function also returns NULL.
    """
    raise NotImplementedError


def sync_http_set_request_contents_bin(
    interaction: SynchronousHttp,
    contents: str,
    len: int,
    content_type: str,
) -> None:
    """
    Sets the request contents of the interaction as an array of bytes.

    [Rust
    `pactffi_sync_http_set_request_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_set_request_contents_bin)

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
    `pactffi_sync_http_get_response`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_get_response)

    # Safety

    The data pointed to by the pointer this function returns will be deleted
    when the interaction is deleted. Trying to use if after the interaction is
    deleted will result in undefined behaviour.

    # Error Handling

    If the interaction is NULL, returns NULL.
    """
    raise NotImplementedError


def sync_http_get_response_contents(interaction: SynchronousHttp) -> str:
    """
    Get the response contents of a `SynchronousHttp` interaction in string form.

    [Rust
    `pactffi_sync_http_get_response_contents`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_get_response_contents)

    # Safety

    The returned string must be deleted with `pactffi_string_delete`.

    The returned string can outlive the interaction.

    # Error Handling

    If the interaction is NULL, returns NULL.

    If the body of the response is missing, then this function also returns
    NULL. This means there's no mechanism to differentiate with this function
    call alone between a NULL body and a missing body.
    """
    raise NotImplementedError


def sync_http_set_response_contents(
    interaction: SynchronousHttp,
    contents: str,
    content_type: str,
) -> None:
    """
    Sets the response contents of the interaction.

    [Rust
    `pactffi_sync_http_set_response_contents`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_set_response_contents)

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
    `pactffi_sync_http_get_response_contents_length`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_get_response_contents_length)

    # Safety

    This function is safe.

    # Error Handling

    If the interaction is NULL or the index is not valid, returns 0. If the body
    of the response is missing, then this function also returns 0.
    """
    raise NotImplementedError


def sync_http_get_response_contents_bin(interaction: SynchronousHttp) -> bytes:
    """
    Get the response contents of a `SynchronousHttp` interaction as bytes.

    [Rust
    `pactffi_sync_http_get_response_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_get_response_contents_bin)

    # Safety

    The number of bytes in the buffer will be returned by
    `pactffi_sync_http_get_response_contents_length`. It is safe to use the
    pointer while the interaction is not deleted or changed. Using the pointer
    after the interaction is mutated or deleted may lead to undefined behaviour.

    # Error Handling

    If the interaction is NULL, returns NULL. If the body of the response is
    missing, then this function also returns NULL.
    """
    raise NotImplementedError


def sync_http_set_response_contents_bin(
    interaction: SynchronousHttp,
    contents: str,
    len: int,
    content_type: str,
) -> None:
    """
    Sets the response contents of the `SynchronousHttp` interaction as bytes.

    [Rust
    `pactffi_sync_http_set_response_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_set_response_contents_bin)

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
    `pactffi_sync_http_get_description`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_get_description)

    # Safety

    The returned string must be deleted with `pactffi_string_delete`.

    Since it is a copy, the returned string may safely outlive the
    `SynchronousHttp` interaction.

    # Errors

    On failure, this function will return a NULL pointer.

    This function may fail if the Rust string contains embedded null ('\0')
    bytes.
    """
    raise NotImplementedError


def sync_http_set_description(interaction: SynchronousHttp, description: str) -> int:
    """
    Write the `description` field on the `SynchronousHttp`.

    [Rust
    `pactffi_sync_http_set_description`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_set_description)

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
    `pactffi_sync_http_get_provider_state`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_get_provider_state)

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
    `pactffi_sync_http_get_provider_state_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_http_get_provider_state_iter)

    # Safety

    The underlying data must not change during iteration.

    # Error Handling

    Returns NULL if an error occurs.
    """
    raise NotImplementedError


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
    `pactffi_pact_interaction_as_synchronous_http`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_interaction_as_synchronous_http)

    # Safety This function is safe as long as the interaction pointer is a valid
    pointer.

    # Errors On any error, this function will return a NULL pointer.
    """
    raise NotImplementedError


def pact_interaction_as_message(interaction: PactInteraction) -> Message:
    """
    Casts this interaction to a `Message` interaction.

    Returns a NULL pointer if the interaction can not be casted to a `Message`
    interaction (for instance, it is a http interaction). The returned pointer
    must be freed with `pactffi_message_delete` when no longer required.

    [Rust
    `pactffi_pact_interaction_as_message`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_interaction_as_message)

    Note that if the interaction is a V4 `AsynchronousMessage`, it will be
    converted to a V3 `Message` before being returned.

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
    `pactffi_pact_interaction_as_asynchronous_message`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_interaction_as_asynchronous_message)

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
    `pactffi_pact_interaction_as_synchronous_message`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_interaction_as_synchronous_message)

    # Safety This function is safe as long as the interaction pointer is a valid
    pointer.

    # Errors On any error, this function will return a NULL pointer.
    """
    raise NotImplementedError


def pact_message_iter_delete(iter: PactMessageIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust
    `pactffi_pact_message_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_message_iter_delete)
    """
    raise NotImplementedError


def pact_message_iter_next(iter: PactMessageIterator) -> Message:
    """
    Get the next message from the message pact.

    As the messages returned are owned by the iterator, they do not need to be
    deleted but will be cleaned up when the iterator is deleted.

    [Rust
    `pactffi_pact_message_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_message_iter_next)

    Will return a NULL pointer when the iterator has advanced past the end of
    the list.

    # Safety

    This function is safe.

    Deleting a message returned by the iterator can lead to undefined behaviour.

    # Error Handling

    This function will return a NULL pointer if passed a NULL pointer or if an
    error occurs.
    """
    raise NotImplementedError


def pact_sync_message_iter_next(iter: PactSyncMessageIterator) -> SynchronousMessage:
    """
    Get the next synchronous request/response message from the V4 pact.

    As the messages returned are owned by the iterator, they do not need to be
    deleted but will be cleaned up when the iterator is deleted.

    [Rust
    `pactffi_pact_sync_message_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_sync_message_iter_next)

    Will return a NULL pointer when the iterator has advanced past the end of
    the list.

    # Safety

    This function is safe.

    Deleting a message returned by the iterator can lead to undefined behaviour.

    # Error Handling

    This function will return a NULL pointer if passed a NULL pointer or if an
    error occurs.
    """
    raise NotImplementedError


def pact_sync_message_iter_delete(iter: PactSyncMessageIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust
    `pactffi_pact_sync_message_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_sync_message_iter_delete)
    """
    raise NotImplementedError


def pact_sync_http_iter_next(iter: PactSyncHttpIterator) -> SynchronousHttp:
    """
    Get the next synchronous HTTP request/response interaction from the V4 pact.

    As the interactions returned are owned by the iterator, they do not need to
    be deleted but will be cleaned up when the iterator is deleted.

    [Rust
    `pactffi_pact_sync_http_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_sync_http_iter_next)

    Will return a NULL pointer when the iterator has advanced past the end of
    the list.

    # Safety

    This function is safe.

    Deleting an interaction returned by the iterator can lead to undefined
    behaviour.

    # Error Handling

    This function will return a NULL pointer if passed a NULL pointer or if an
    error occurs.
    """
    raise NotImplementedError


def pact_sync_http_iter_delete(iter: PactSyncHttpIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust
    `pactffi_pact_sync_http_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_sync_http_iter_delete)
    """
    raise NotImplementedError


def pact_interaction_iter_next(iter: PactInteractionIterator) -> PactInteraction:
    """
    Get the next interaction from the pact.

    As the interactions returned are owned by the iterator, they do not need to
    be deleted but will be cleaned up when the iterator is deleted.

    [Rust
    `pactffi_pact_interaction_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_interaction_iter_next)

    Will return a NULL pointer when the iterator has advanced past the end of
    the list.

    # Safety

    This function is safe.

    Deleting an interaction returned by the iterator can lead to undefined
    behaviour.

    # Error Handling

    This function will return a NULL pointer if passed a NULL pointer or if an
    error occurs.
    """
    raise NotImplementedError


def pact_interaction_iter_delete(iter: PactInteractionIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust
    `pactffi_pact_interaction_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_interaction_iter_delete)
    """
    raise NotImplementedError


def matching_rule_to_json(rule: MatchingRule) -> str:
    """
    Get the JSON form of the matching rule.

    [Rust
    `pactffi_matching_rule_to_json`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matching_rule_to_json)

    The returned string must be deleted with `pactffi_string_delete`.

    # Safety

    This function will fail if it is passed a NULL pointer, or the iterator that
    owns the value of the matching rule has been deleted.
    """
    raise NotImplementedError


def matching_rules_iter_delete(iter: MatchingRuleCategoryIterator) -> None:
    """
    Free the iterator when you're done using it.

    [Rust
    `pactffi_matching_rules_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matching_rules_iter_delete)
    """
    raise NotImplementedError


def matching_rules_iter_next(
    iter: MatchingRuleCategoryIterator,
) -> MatchingRuleKeyValuePair:
    """
    Get the next path and matching rule out of the iterator, if possible.

    [Rust
    `pactffi_matching_rules_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matching_rules_iter_next)

    The returned pointer must be deleted with
    `pactffi_matching_rules_iter_pair_delete`.

    # Safety

    The underlying data is owned by the `MatchingRuleKeyValuePair`, so is always
    safe to use.

    # Error Handling

    If no further data is present, returns NULL.
    """
    raise NotImplementedError


def matching_rules_iter_pair_delete(pair: MatchingRuleKeyValuePair) -> None:
    """
    Free a pair of key and value returned from `message_metadata_iter_next`.

    [Rust
    `pactffi_matching_rules_iter_pair_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matching_rules_iter_pair_delete)
    """
    raise NotImplementedError


def message_new() -> Message:
    """
    Get a mutable pointer to a newly-created default message on the heap.

    [Rust
    `pactffi_message_new`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_new)

    # Safety

    This function is safe.

    # Error Handling

    Returns NULL on error.
    """
    raise NotImplementedError


def message_new_from_json(
    index: int,
    json_str: str,
    spec_version: PactSpecification,
) -> Message:
    """
    Constructs a `Message` from the JSON string.

    [Rust
    `pactffi_message_new_from_json`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_new_from_json)

    # Safety

    This function is safe.

    # Error Handling

    If the JSON string is invalid or not UTF-8 encoded, returns a NULL.
    """
    raise NotImplementedError


def message_new_from_body(body: str, content_type: str) -> Message:
    """
    Constructs a `Message` from a body with a given content-type.

    [Rust
    `pactffi_message_new_from_body`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_new_from_body)

    # Safety

    This function is safe.

    # Error Handling

    If the body or content type are invalid or not UTF-8 encoded, returns NULL.
    """
    raise NotImplementedError


def message_delete(message: Message) -> None:
    """
    Destroy the `Message` being pointed to.

    [Rust
    `pactffi_message_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_delete)
    """
    raise NotImplementedError


def message_get_contents(message: Message) -> str:
    """
    Get the contents of a `Message` in string form.

    [Rust
    `pactffi_message_get_contents`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_get_contents)

    # Safety

    The returned string must be deleted with `pactffi_string_delete`.

    The returned string can outlive the message.

    # Error Handling

    If the message is NULL, returns NULL. If the body of the message is missing,
    then this function also returns NULL. This means there's no mechanism to
    differentiate with this function call alone between a NULL message and a
    missing message body.
    """
    raise NotImplementedError


def message_set_contents(message: Message, contents: str, content_type: str) -> None:
    """
    Sets the contents of the message.

    [Rust
    `pactffi_message_set_contents`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_set_contents)

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


def message_get_contents_length(message: Message) -> int:
    """
    Get the length of the contents of a `Message`.

    [Rust
    `pactffi_message_get_contents_length`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_get_contents_length)

    # Safety

    This function is safe.

    # Error Handling

    If the message is NULL, returns 0. If the body of the message is missing,
    then this function also returns 0.
    """
    raise NotImplementedError


def message_get_contents_bin(message: Message) -> str:
    """
    Get the contents of a `Message` as a pointer to an array of bytes.

    [Rust
    `pactffi_message_get_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_get_contents_bin)

    # Safety

    The number of bytes in the buffer will be returned by
    `pactffi_message_get_contents_length`. It is safe to use the pointer while
    the message is not deleted or changed. Using the pointer after the message
    is mutated or deleted may lead to undefined behaviour.

    # Error Handling

    If the message is NULL, returns NULL. If the body of the message is missing,
    then this function also returns NULL.
    """
    raise NotImplementedError


def message_set_contents_bin(
    message: Message,
    contents: str,
    len: int,
    content_type: str,
) -> None:
    """
    Sets the contents of the message as an array of bytes.

    [Rust
    `pactffi_message_set_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_set_contents_bin)

    # Safety

    The contents pointer must be valid for reads of `len` bytes, and it must be
    properly aligned and consecutive. Otherwise behaviour is undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the message contents as null.
    If the content type is a null pointer, or can't be parsed, it will set the
    content type as unknown.
    """
    raise NotImplementedError


def message_get_description(message: Message) -> str:
    r"""
    Get a copy of the description.

    [Rust
    `pactffi_message_get_description`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_get_description)

    # Safety

    The returned string must be deleted with `pactffi_string_delete`.

    Since it is a copy, the returned string may safely outlive the `Message`.

    # Errors

    On failure, this function will return a NULL pointer.

    This function may fail if the Rust string contains embedded null ('\0')
    bytes.
    """
    raise NotImplementedError


def message_set_description(message: Message, description: str) -> int:
    """
    Write the `description` field on the `Message`.

    [Rust
    `pactffi_message_set_description`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_set_description)

    # Safety

    `description` must contain valid UTF-8. Invalid UTF-8 will be replaced with
    U+FFFD REPLACEMENT CHARACTER.

    This function will only reallocate if the new string does not fit in the
    existing buffer.

    # Error Handling

    Errors will be reported with a non-zero return value.
    """
    raise NotImplementedError


def message_get_provider_state(message: Message, index: int) -> ProviderState:
    r"""
    Get a copy of the provider state at the given index from this message.

    [Rust
    `pactffi_message_get_provider_state`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_get_provider_state)

    # Safety

    The returned structure must be deleted with `provider_state_delete`.

    Since it is a copy, the returned structure may safely outlive the `Message`.

    # Error Handling

    On failure, this function will return a variant other than Success.

    This function may fail if the index requested is out of bounds, or if any of
    the Rust strings contain embedded null ('\0') bytes.
    """
    raise NotImplementedError


def message_get_provider_state_iter(message: Message) -> ProviderStateIterator:
    """
    Get an iterator over provider states.

    [Rust
    `pactffi_message_get_provider_state_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_get_provider_state_iter)

    # Safety

    The underlying data must not change during iteration.

    # Error Handling

    Returns NULL if an error occurs.
    """
    raise NotImplementedError


def provider_state_iter_next(iter: ProviderStateIterator) -> ProviderState:
    """
    Get the next value from the iterator.

    [Rust
    `pactffi_provider_state_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_provider_state_iter_next)

    # Safety

    The underlying data must not change during iteration.

    If a previous call panicked, then the internal mutex will have been poisoned
    and this function will return NULL.

    # Error Handling

    Returns NULL if an error occurs.
    """
    raise NotImplementedError


def provider_state_iter_delete(iter: ProviderStateIterator) -> None:
    """
    Delete the iterator.

    [Rust
    `pactffi_provider_state_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_provider_state_iter_delete)
    """
    raise NotImplementedError


def message_find_metadata(message: Message, key: str) -> str:
    r"""
    Get a copy of the metadata value indexed by `key`.

    [Rust
    `pactffi_message_find_metadata`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_find_metadata)

    # Safety

    The returned string must be deleted with `pactffi_string_delete`.

    Since it is a copy, the returned string may safely outlive the `Message`.

    The returned pointer will be NULL if the metadata does not contain the given
    key, or if an error occurred.

    # Error Handling

    On failure, this function will return a NULL pointer.

    This function may fail if the provided `key` string contains invalid UTF-8,
    or if the Rust string contains embedded null ('\0') bytes.
    """
    raise NotImplementedError


def message_insert_metadata(message: Message, key: str, value: str) -> int:
    r"""
    Insert the (`key`, `value`) pair into this Message's `metadata` HashMap.

    [Rust
    `pactffi_message_insert_metadata`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_insert_metadata)

    # Safety

    This function returns an enum indicating the result; see the comments on
    HashMapInsertStatus for details.

    # Error Handling

    This function may fail if the provided `key` or `value` strings contain
    invalid UTF-8.
    """
    raise NotImplementedError


def message_metadata_iter_next(iter: MessageMetadataIterator) -> MessageMetadataPair:
    """
    Get the next key and value out of the iterator, if possible.

    [Rust
    `pactffi_message_metadata_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_metadata_iter_next)

    The returned pointer must be deleted with
    `pactffi_message_metadata_pair_delete`.

    # Safety

    The underlying data must not change during iteration.

    # Error Handling

    If no further data is present, returns NULL.
    """
    raise NotImplementedError


def message_get_metadata_iter(message: Message) -> MessageMetadataIterator:
    r"""
    Get an iterator over the metadata of a message.

    [Rust
    `pactffi_message_get_metadata_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_get_metadata_iter)

    # Safety

    This iterator carries a pointer to the message, and must not outlive the
    message.

    The message metadata also must not be modified during iteration. If it is,
    the old iterator must be deleted and a new iterator created.

    # Error Handling

    On failure, this function will return a NULL pointer.

    This function may fail if any of the Rust strings contain embedded null
    ('\0') bytes.
    """
    raise NotImplementedError


def message_metadata_iter_delete(iter: MessageMetadataIterator) -> None:
    """
    Free the metadata iterator when you're done using it.

    [Rust
    `pactffi_message_metadata_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_metadata_iter_delete)
    """
    raise NotImplementedError


def message_metadata_pair_delete(pair: MessageMetadataPair) -> None:
    """
    Free a pair of key and value returned from `message_metadata_iter_next`.

    [Rust
    `pactffi_message_metadata_pair_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_metadata_pair_delete)
    """
    raise NotImplementedError


def message_pact_new_from_json(file_name: str, json_str: str) -> MessagePact:
    """
    Construct a new `MessagePact` from the JSON string.

    The provided file name is used when generating error messages.

    [Rust
    `pactffi_message_pact_new_from_json`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_pact_new_from_json)

    # Safety

    The `file_name` and `json_str` parameters must both be valid UTF-8 encoded
    strings.

    # Error Handling

    On error, this function will return a null pointer.
    """
    raise NotImplementedError


def message_pact_delete(message_pact: MessagePact) -> None:
    """
    Delete the `MessagePact` being pointed to.

    [Rust
    `pactffi_message_pact_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_pact_delete)
    """
    raise NotImplementedError


def message_pact_get_consumer(message_pact: MessagePact) -> Consumer:
    """
    Get a pointer to the Consumer struct inside the MessagePact.

    This is a mutable borrow: The caller may mutate the Consumer through this
    pointer.

    [Rust
    `pactffi_message_pact_get_consumer`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_pact_get_consumer)

    # Safety

    This function is safe.

    # Error Handling

    This function will only fail if it is passed a NULL pointer. In the case of
    error, a NULL pointer will be returned.
    """
    raise NotImplementedError


def message_pact_get_provider(message_pact: MessagePact) -> Provider:
    """
    Get a pointer to the Provider struct inside the MessagePact.

    This is a mutable borrow: The caller may mutate the Provider through this
    pointer.

    [Rust
    `pactffi_message_pact_get_provider`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_pact_get_provider)

    # Safety

    This function is safe.

    # Error Handling

    This function will only fail if it is passed a NULL pointer. In the case of
    error, a NULL pointer will be returned.
    """
    raise NotImplementedError


def message_pact_get_message_iter(
    message_pact: MessagePact,
) -> MessagePactMessageIterator:
    r"""
    Get an iterator over the messages of a message pact.

    [Rust
    `pactffi_message_pact_get_message_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_pact_get_message_iter)

    # Safety

    This iterator carries a pointer to the message pact, and must not outlive
    the message pact.

    The message pact messages also must not be modified during iteration. If
    they are, the old iterator must be deleted and a new iterator created.

    # Error Handling

    On failure, this function will return a NULL pointer.

    This function may fail if any of the Rust strings contain embedded null
    ('\0') bytes.
    """
    raise NotImplementedError


def message_pact_message_iter_next(iter: MessagePactMessageIterator) -> Message:
    """
    Get the next message from the message pact.

    [Rust
    `pactffi_message_pact_message_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_pact_message_iter_next)

    # Safety

    This function is safe.

    # Error Handling

    This function will return a NULL pointer if passed a NULL pointer or if an
    error occurs.
    """
    raise NotImplementedError


def message_pact_message_iter_delete(iter: MessagePactMessageIterator) -> None:
    """
    Delete the iterator.

    [Rust
    `pactffi_message_pact_message_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_pact_message_iter_delete)
    """
    raise NotImplementedError


def message_pact_find_metadata(message_pact: MessagePact, key1: str, key2: str) -> str:
    r"""
    Get a copy of the metadata value indexed by `key1` and `key2`.

    [Rust
    `pactffi_message_pact_find_metadata`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_pact_find_metadata)

    # Safety

    Since it is a copy, the returned string may safely outlive the `Message`.

    The returned string must be deleted with `pactffi_string_delete`.

    The returned pointer will be NULL if the metadata does not contain the given
    key, or if an error occurred.

    # Error Handling

    On failure, this function will return a NULL pointer.

    This function may fail if the provided `key1` or `key2` strings contains
    invalid UTF-8, or if the Rust string contains embedded null ('\0') bytes.
    """
    raise NotImplementedError


def message_pact_get_metadata_iter(
    message_pact: MessagePact,
) -> MessagePactMetadataIterator:
    r"""
    Get an iterator over the metadata of a message pact.

    [Rust
    `pactffi_message_pact_get_metadata_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_pact_get_metadata_iter)

    # Safety

    This iterator carries a pointer to the message pact, and must not outlive
    the message pact.

    The message pact metadata also must not be modified during iteration. If it
    is, the old iterator must be deleted and a new iterator created.

    # Error Handling

    On failure, this function will return a NULL pointer.

    This function may fail if any of the Rust strings contain embedded null
    ('\0') bytes.
    """
    raise NotImplementedError


def message_pact_metadata_iter_next(
    iter: MessagePactMetadataIterator,
) -> MessagePactMetadataTriple:
    """
    Get the next triple out of the iterator, if possible.

    [Rust
    `pactffi_message_pact_metadata_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_pact_metadata_iter_next)

    # Safety

    This operation is invalid if the underlying data has been changed during
    iteration.

    # Error Handling

    Returns null if no next element is present.
    """
    raise NotImplementedError


def message_pact_metadata_iter_delete(iter: MessagePactMetadataIterator) -> None:
    """
    Free the metadata iterator when you're done using it.

    [Rust `pactffi_message_pact_metadata_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_pact_metadata_iter_delete)
    """
    raise NotImplementedError


def message_pact_metadata_triple_delete(triple: MessagePactMetadataTriple) -> None:
    """
    Free a triple returned from `pactffi_message_pact_metadata_iter_next`.

    [Rust `pactffi_message_pact_metadata_triple_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_pact_metadata_triple_delete)
    """
    raise NotImplementedError


def provider_get_name(provider: Provider) -> str:
    r"""
    Get a copy of this provider's name.

    [Rust
    `pactffi_provider_get_name`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_provider_get_name)

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
    `pactffi_pact_get_provider`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_get_provider)

    # Errors

    This function will fail if it is passed a NULL pointer. In the case of
    error, a NULL pointer will be returned.
    """
    raise NotImplementedError


def pact_provider_delete(provider: Provider) -> None:
    """
    Frees the memory used by the Pact provider.

    [Rust
    `pactffi_pact_provider_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_provider_delete)
    """
    raise NotImplementedError


def provider_state_get_name(provider_state: ProviderState) -> str:
    """
    Get the name of the provider state as a string.

    This needs to be deleted with `pactffi_string_delete`.

    [Rust
    `pactffi_provider_state_get_name`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_provider_state_get_name)

    # Safety

    This function is safe.

    # Error Handling

    If the provider_state param is NULL, this returns NULL.
    """
    raise NotImplementedError


def provider_state_get_param_iter(
    provider_state: ProviderState,
) -> ProviderStateParamIterator:
    r"""
    Get an iterator over the params of a provider state.

    [Rust
    `pactffi_provider_state_get_param_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_provider_state_get_param_iter)

    # Safety

    This iterator carries a pointer to the provider state, and must not outlive
    the provider state.

    The provider state params also must not be modified during iteration. If it
    is, the old iterator must be deleted and a new iterator created.

    # Errors

    On failure, this function will return a NULL pointer.

    This function may fail if any of the Rust strings contain embedded null
    ('\0') bytes.
    """
    raise NotImplementedError


def provider_state_param_iter_next(
    iter: ProviderStateParamIterator,
) -> ProviderStateParamPair:
    """
    Get the next key and value out of the iterator, if possible.

    [Rust
    `pactffi_provider_state_param_iter_next`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_provider_state_param_iter_next)

    Returns a pointer to a heap allocated array of 2 elements, the pointer to
    the key string on the heap, and the pointer to the value string on the heap.

    # Safety

    The underlying data must not be modified during iteration.

    The user needs to free both the contained strings and the array.

    # Error Handling

    Returns NULL if there's no further elements or the iterator is NULL.
    """
    raise NotImplementedError


def provider_state_delete(provider_state: ProviderState) -> None:
    """
    Free the provider state when you're done using it.

    [Rust
    `pactffi_provider_state_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_provider_state_delete)
    """
    raise NotImplementedError


def provider_state_param_iter_delete(iter: ProviderStateParamIterator) -> None:
    """
    Free the provider state param iterator when you're done using it.

    [Rust
    `pactffi_provider_state_param_iter_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_provider_state_param_iter_delete)
    """
    raise NotImplementedError


def provider_state_param_pair_delete(pair: ProviderStateParamPair) -> None:
    """
    Free a pair of key and value.

    [Rust
    `pactffi_provider_state_param_pair_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_provider_state_param_pair_delete)
    """
    raise NotImplementedError


def sync_message_new() -> SynchronousMessage:
    """
    Get a mutable pointer to a newly-created default message on the heap.

    [Rust
    `pactffi_sync_message_new`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_new)

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
    `pactffi_sync_message_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_delete)
    """
    raise NotImplementedError


def sync_message_get_request_contents_str(message: SynchronousMessage) -> str:
    """
    Get the request contents of a `SynchronousMessage` in string form.

    [Rust
    `pactffi_sync_message_get_request_contents_str`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_get_request_contents_str)

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
    `pactffi_sync_message_set_request_contents_str`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_set_request_contents_str)

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
    `pactffi_sync_message_get_request_contents_length`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_get_request_contents_length)

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
    `pactffi_sync_message_get_request_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_get_request_contents_bin)

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
    `pactffi_sync_message_set_request_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_set_request_contents_bin)

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
    `pactffi_sync_message_get_request_contents`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_get_request_contents)

    # Safety

    The data pointed to by the pointer this function returns will be deleted
    when the message is deleted. Trying to use if after the message is deleted
    will result in undefined behaviour.

    # Error Handling

    If the message is NULL, returns NULL.
    """
    raise NotImplementedError


def sync_message_get_number_responses(message: SynchronousMessage) -> int:
    """
    Get the number of response messages in the `SynchronousMessage`.

    [Rust
    `pactffi_sync_message_get_number_responses`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_get_number_responses)

    # Safety

    The message pointer must point to a valid SynchronousMessage.

    # Error Handling

    If the message is NULL, returns 0.
    """
    raise NotImplementedError


def sync_message_get_response_contents_str(
    message: SynchronousMessage,
    index: int,
) -> str:
    """
    Get the response contents of a `SynchronousMessage` in string form.

    [Rust
    `pactffi_sync_message_get_response_contents_str`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_get_response_contents_str)

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
    `pactffi_sync_message_set_response_contents_str`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_set_response_contents_str)

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
    `pactffi_sync_message_get_response_contents_length`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_get_response_contents_length)

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
    `pactffi_sync_message_get_response_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_get_response_contents_bin)

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
    `pactffi_sync_message_set_response_contents_bin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_set_response_contents_bin)

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
    `pactffi_sync_message_get_response_contents`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_get_response_contents)

    # Safety

    The data pointed to by the pointer this function returns will be deleted
    when the message is deleted. Trying to use if after the message is deleted
    will result in undefined behaviour.

    # Error Handling

    If the message is NULL or the index is not valid, returns NULL.
    """
    raise NotImplementedError


def sync_message_get_description(message: SynchronousMessage) -> str:
    r"""
    Get a copy of the description.

    [Rust
    `pactffi_sync_message_get_description`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_get_description)

    # Safety

    The returned string must be deleted with `pactffi_string_delete`.

    Since it is a copy, the returned string may safely outlive the
    `SynchronousMessage`.

    # Errors

    On failure, this function will return a NULL pointer.

    This function may fail if the Rust string contains embedded null ('\0')
    bytes.
    """
    raise NotImplementedError


def sync_message_set_description(message: SynchronousMessage, description: str) -> int:
    """
    Write the `description` field on the `SynchronousMessage`.

    [Rust
    `pactffi_sync_message_set_description`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_set_description)

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
    `pactffi_sync_message_get_provider_state`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_get_provider_state)

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
    `pactffi_sync_message_get_provider_state_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_sync_message_get_provider_state_iter)

    # Safety

    The underlying data must not change during iteration.

    # Error Handling

    Returns NULL if an error occurs.
    """
    raise NotImplementedError


def string_delete(string: str) -> None:
    """
    Delete a string previously returned by this FFI.

    [Rust
    `pactffi_string_delete`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_string_delete)

    It is explicitly allowed to pass a null pointer to this function; in that
    case the function will do nothing.

    # Safety Passing an invalid pointer, or one that was not returned by a FFI
    function can result in undefined behaviour.
    """
    raise NotImplementedError


def create_mock_server(pact_str: str, addr_str: str, *, tls: bool) -> int:
    """
    [DEPRECATED] External interface to create a HTTP mock server.

    A pointer to the pact JSON as a NULL-terminated C string is passed in, as
    well as the port for the mock server to run on. A value of 0 for the port
    will result in a port being allocated by the operating system. The port of
    the mock server is returned.

    [Rust
    `pactffi_create_mock_server`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_create_mock_server)

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


def get_tls_ca_certificate() -> str:
    """
    Fetch the CA Certificate used to generate the self-signed certificate.

    [Rust
    `pactffi_get_tls_ca_certificate`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_get_tls_ca_certificate)

    **NOTE:** The string for the result is allocated on the heap, and will have
    to be freed by the caller using pactffi_string_delete.

    # Errors

    An empty string indicates an error reading the pem file.
    """
    raise NotImplementedError


def create_mock_server_for_pact(pact: PactHandle, addr_str: str, *, tls: bool) -> int:
    """
    [DEPRECATED] External interface to create a HTTP mock server.

    A Pact handle is passed in, as well as the port for the mock server to run
    on. A value of 0 for the port will result in a port being allocated by the
    operating system. The port of the mock server is returned.

    [Rust
    `pactffi_create_mock_server_for_pact`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_create_mock_server_for_pact)

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
    transport_config: str,
) -> int:
    """
    Create a mock server for the provided Pact handle and transport.

    If the transport is not provided (it is a NULL pointer or an empty string),
    will default to an HTTP transport. The address is the interface bind to, and
    will default to the loopback adapter if not specified. Specifying a value of
    zero for the port will result in the operating system allocating the port.

    [Rust
    `pactffi_create_mock_server_for_transport`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_create_mock_server_for_transport)

    Parameters:

    * `pact` - Handle to a Pact model created with created with
      `pactffi_new_pact`.
    * `addr` - Address to bind to (i.e. `127.0.0.1` or `[::1]`). Must be a valid
      UTF-8 NULL-terminated string, or NULL or empty, in which case the loopback
      adapter is used.
    * `port` - Port number to bind to. A value of zero will result in the
      operating system allocating an available port.
    * `transport` - The transport to use (i.e. http, https, grpc). Must be a
      valid UTF-8 NULL-terminated string, or NULL or empty, in which case http
      will be used.
    * `transport_config` - (OPTIONAL) Configuration for the transport as a valid
      JSON string. Set to NULL or empty if not required.

    The port of the mock server is returned.

    # Safety NULL pointers or empty strings can be passed in for the address,
    transport and transport_config, in which case a default value will be used.
    Passing in an invalid pointer will result in undefined behaviour.

    # Errors

    Errors are returned as negative values.

    | Error | Description |
    |-------|-------------|
    | -1 | An invalid handle was received. Handles should be created with `pactffi_new_pact` |
    | -2 | transport_config is not valid JSON |
    | -3 | The mock server could not be started |
    | -4 | The method panicked |
    | -5 | The address is not valid |

    """  # noqa: E501
    raise NotImplementedError


def mock_server_matched(mock_server_port: int) -> bool:
    """
    External interface to check if a mock server has matched all its requests.

    The port number is passed in, and if all requests have been matched, true is
    returned. False is returned if there is no mock server on the given port, or
    if any request has not been successfully matched, or the method panics.

    [Rust
    `pactffi_mock_server_matched`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_mock_server_matched)
    """
    raise NotImplementedError


def mock_server_mismatches(mock_server_port: int) -> str:
    """
    External interface to get all the mismatches from a mock server.

    The port number of the mock server is passed in, and a pointer to a C string
    with the mismatches in JSON format is returned.

    [Rust
    `pactffi_mock_server_mismatches`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_mock_server_mismatches)

    **NOTE:** The JSON string for the result is allocated on the heap, and will
    have to be freed once the code using the mock server is complete. The
    [`cleanup_mock_server`](fn.cleanup_mock_server.html) function is provided
    for this purpose.

    # Errors

    If there is no mock server with the provided port number, or the function
    panics, a NULL pointer will be returned. Don't try to dereference it, it
    will not end well for you.
    """
    raise NotImplementedError


def cleanup_mock_server(mock_server_port: int) -> bool:
    """
    External interface to cleanup a mock server.

    This function will try terminate the mock server with the given port number
    and cleanup any memory allocated for it. Returns true, unless a mock server
    with the given port number does not exist, or the function panics.

    [Rust
    `pactffi_cleanup_mock_server`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_cleanup_mock_server)
    """
    raise NotImplementedError


def write_pact_file(mock_server_port: int, directory: str, *, overwrite: bool) -> int:
    """
    External interface to trigger a mock server to write out its pact file.

    This function should be called if all the consumer tests have passed. The
    directory to write the file to is passed as the second parameter. If a NULL
    pointer is passed, the current working directory is used.

    [Rust
    `pactffi_write_pact_file`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_write_pact_file)

    If overwrite is true, the file will be overwritten with the contents of the
    current pact. Otherwise, it will be merged with any existing pact file.

    Returns 0 if the pact file was successfully written. Returns a positive code
    if the file can not be written, or there is no mock server running on that
    port or the function panics.

    # Errors

    Errors are returned as positive values.

    | Error | Description |
    |-------|-------------|
    | 1 | A general panic was caught |
    | 2 | The pact file was not able to be written |
    | 3 | A mock server with the provided port was not found |
    """
    raise NotImplementedError


def mock_server_logs(mock_server_port: int) -> str:
    """
    Fetch the logs for the mock server.

    This needs the memory buffer log sink to be setup before the mock server is
    started. Returned string will be freed with the `cleanup_mock_server`
    function call.

    [Rust
    `pactffi_mock_server_logs`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_mock_server_logs)

    Will return a NULL pointer if the logs for the mock server can not be
    retrieved.
    """
    raise NotImplementedError


def generate_datetime_string(format: str) -> StringResult:
    """
    Generates a datetime value from the provided format string.

    This uses the current system date and time NOTE: The memory for the returned
    string needs to be freed with the `pactffi_string_delete` function

    [Rust
    `pactffi_generate_datetime_string`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_generate_datetime_string)

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
    `pactffi_check_regex`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_check_regex)

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
    `pactffi_generate_regex_value`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_generate_regex_value)

    # Safety

    The regex pointer must be a valid pointer to a NULL-terminated string.
    Invalid pointers will result in undefined behaviour.
    """
    raise NotImplementedError


def free_string(s: str) -> None:
    """
    [DEPRECATED] Frees the memory allocated to a string by another function.

    [Rust
    `pactffi_free_string`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_free_string)

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
    `pactffi_new_pact`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_new_pact)

    * `consumer_name` - The name of the consumer for the pact.
    * `provider_name` - The name of the provider for the pact.

    Returns a new `PactHandle`. The handle will need to be freed with the
    `pactffi_free_pact_handle` method to release its resources.
    """
    raise NotImplementedError


def new_interaction(pact: PactHandle, description: str) -> InteractionHandle:
    """
    Creates a new HTTP Interaction and returns a handle to it.

    [Rust
    `pactffi_new_interaction`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_new_interaction)

    * `description` - The interaction description. It needs to be unique for
      each interaction.

    Returns a new `InteractionHandle`.
    """
    raise NotImplementedError


def new_message_interaction(pact: PactHandle, description: str) -> InteractionHandle:
    """
    Creates a new message interaction and return a handle to it.

    * `description` - The interaction description. It needs to be unique for
      each interaction.

    [Rust
    `pactffi_new_message_interaction`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_new_message_interaction)

    Returns a new `InteractionHandle`.
    """
    raise NotImplementedError


def new_sync_message_interaction(
    pact: PactHandle,
    description: str,
) -> InteractionHandle:
    """
    Creates a new synchronous message interaction and return a handle to it.

    * `description` - The interaction description. It needs to be unique for
      each interaction.

    [Rust
    `pactffi_new_sync_message_interaction`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_new_sync_message_interaction)

    Returns a new `InteractionHandle`.
    """
    raise NotImplementedError


def upon_receiving(interaction: InteractionHandle, description: str) -> bool:
    """
    Sets the description for the Interaction.

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started)

    [Rust
    `pactffi_upon_receiving`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_upon_receiving)

    * `description` - The interaction description. It needs to be unique for
      each interaction.
    """
    raise NotImplementedError


def given(interaction: InteractionHandle, description: str) -> bool:
    """
    Adds a provider state to the Interaction.

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started)

    [Rust
    `pactffi_given`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_given)

    * `description` - The provider state description. It needs to be unique.
    """
    raise NotImplementedError


def interaction_test_name(interaction: InteractionHandle, test_name: str) -> int:
    """
    Sets the test name annotation for the interaction.

    This allows capturing the name of the test as metadata. This can only be
    used with V4 interactions.

    [Rust
    `pactffi_interaction_test_name`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_interaction_test_name)

    # Safety

    The test name parameter must be a valid pointer to a NULL terminated string.

    # Error Handling

    If the test name can not be set, this will return a positive value.

    * `1` - Function panicked. Error message will be available by calling
      `pactffi_get_error_message`.
    * `2` - Handle was not valid.
    * `3` - Mock server was already started and the integration can not be
      modified.
    * `4` - Not a V4 interaction.
    """
    raise NotImplementedError


def given_with_param(
    interaction: InteractionHandle,
    description: str,
    name: str,
    value: str,
) -> bool:
    """
    Adds a parameter key and value to a provider state to the Interaction.

    If the provider state does not exist, a new one will be created, otherwise
    the parameter will be merged into the existing one. The parameter value will
    be parsed as JSON.

    [Rust
    `pactffi_given_with_param`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_given_with_param)

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started).

    # Parameters

    * `description` - The provider state description. It needs to be unique.
    * `name` - Parameter name.
    * `value` - Parameter value as JSON.
    """
    raise NotImplementedError


def given_with_params(
    interaction: InteractionHandle,
    description: str,
    params: str,
) -> int:
    """
    Adds a provider state to the Interaction.

    If the params is not an JSON object, it will add it as a single parameter
    with a `value` key.

    [Rust
    `pactffi_given_with_params`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_given_with_params)

    # Parameters

    * `description` - The provider state description.
    * `params` - Parameter values as a JSON fragment.

    # Errors

    Returns EXIT_FAILURE (1) if the interaction or Pact can't be modified (i.e.
    the mock server for it has already started).

    Returns 2 and sets the error message (which can be retrieved with
    `pactffi_get_error_message`) if the parameter values con't be parsed as
    JSON.

    Returns 3 if any of the C strings are not valid.

    """
    raise NotImplementedError


def with_request(interaction: InteractionHandle, method: str, path: str) -> bool:
    r"""
    Configures the request for the Interaction.

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started)

    [Rust
    `pactffi_with_request`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_with_request)

    * `method` - The request method. Defaults to GET.
    * `path` - The request path. Defaults to `/`.

    To include matching rules for the path (only regex really makes sense to
    use), include the matching rule JSON format with the value as a single JSON
    document. I.e.

    ```c
    const char* value = "{\"value\":\"/path/to/100\", \"pact:matcher:type\":\"regex\", \"regex\":\"\\/path\\/to\\/\\\\d+\"}";
    pactffi_with_request(handle, "GET", value);
    ```
    See
    [IntegrationJson.md](https://github.com/pact-foundation/pact-reference/blob/master/rust/pact_ffi/IntegrationJson.md)
    """  # noqa: E501
    raise NotImplementedError


def with_query_parameter(
    interaction: InteractionHandle,
    name: str,
    index: int,
    value: str,
) -> bool:
    """
    Configures a query parameter for the Interaction.

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started)

    [Rust
    `pactffi_with_query_parameter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_with_query_parameter)

    * `name` - the query parameter name.
    * `value` - the query parameter value.
    * `index` - the index of the value (starts at 0). You can use this to create
      a query parameter with multiple values

    **DEPRECATED:** Use `pactffi_with_query_parameter_v2`, which deals with
    multiple values correctly
    """
    warnings.warn(
        "This function is deprecated, use with_query_parameter_v2 instead",
        DeprecationWarning,
        stacklevel=2,
    )
    raise NotImplementedError


def with_query_parameter_v2(
    interaction: InteractionHandle,
    name: str,
    index: int,
    value: str,
) -> bool:
    r"""
    Configures a query parameter for the Interaction.

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started)

    [Rust
    `pactffi_with_query_parameter_v2`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_with_query_parameter_v2)

    * `name` - the query parameter name.
    * `value` - the query parameter value. Either a simple string or a JSON
      document.
    * `index` - the index of the value (starts at 0). You can use this to create
      a query parameter with multiple values

    To setup a query parameter with multiple values, you can either call this
    function multiple times with a different index value, i.e. to create
    `id=2&id=3`

    ```c
    pactffi_with_query_parameter_v2(handle, "id", 0, "2");
    pactffi_with_query_parameter_v2(handle, "id", 1, "3");
    ```

    Or you can call it once with a JSON value that contains multiple values:

    ```c
    const char* value = "{\"value\": [\"2\",\"3\"]}";
    pactffi_with_query_parameter_v2(handle, "id", 0, value);
    ```

    To include matching rules for the query parameter, include the matching rule
    JSON format with the value as a single JSON document. I.e.

    ```c
    const char* value = "{\"value\":\"2\", \"pact:matcher:type\":\"regex\", \"regex\":\"\\\\d+\"}";
    pactffi_with_query_parameter_v2(handle, "id", 0, value);
    ```
    See [IntegrationJson.md](https://github.com/pact-foundation/pact-reference/blob/master/rust/pact_ffi/IntegrationJson.md)

    # Safety

    The name and value parameters must be valid pointers to NULL terminated strings.
    ```
    """  # noqa: E501
    raise NotImplementedError


def with_specification(pact: PactHandle, version: PactSpecification) -> bool:
    """
    Sets the specification version for a given Pact model.

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started) or the version is invalid.

    [Rust
    `pactffi_with_specification`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_with_specification)

    * `pact` - Handle to a Pact model
    * `version` - the spec version to use
    """
    raise NotImplementedError


def with_pact_metadata(
    pact: PactHandle,
    namespace_: str,
    name: str,
    value: str,
) -> bool:
    """
    Sets the additional metadata on the Pact file.

    Common uses are to add the client library details such as the name and
    version Returns false if the interaction or Pact can't be modified (i.e. the
    mock server for it has already started)

    [Rust
    `pactffi_with_pact_metadata`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_with_pact_metadata)

    * `pact` - Handle to a Pact model
    * `namespace` - the top level metadat key to set any key values on
    * `name` - the key to set
    * `value` - the value to set
    """
    raise NotImplementedError


def with_header(
    interaction: InteractionHandle,
    part: InteractionPart,
    name: str,
    index: int,
    value: str,
) -> bool:
    """
    Configures a header for the Interaction.

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started)

    [Rust
    `pactffi_with_header`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_with_header)

    * `part` - The part of the interaction to add the header to (Request or
      Response).
    * `name` - the header name.
    * `value` - the header value.
    * `index` - the index of the value (starts at 0). You can use this to create
      a header with multiple values

    **DEPRECATED:** Use `pactffi_with_header_v2`, which deals with multiple
    values correctly
    """
    warnings.warn(
        "This function is deprecated, use with_header_v2 instead",
        DeprecationWarning,
        stacklevel=2,
    )
    raise NotImplementedError


def with_header_v2(
    interaction: InteractionHandle,
    part: InteractionPart,
    name: str,
    index: int,
    value: str,
) -> bool:
    r"""
    Configures a header for the Interaction.

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started)

    [Rust `pactffi_with_header_v2`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_with_header_v2)

    * `part` - The part of the interaction to add the header to (Request or
      Response).
    * `name` - the header name.
    * `value` - the header value.
    * `index` - the index of the value (starts at 0). You can use this to create
      a header with multiple values

    To setup a header with multiple values, you can either call this function
    multiple times with a different index value, i.e. to create `x-id=2, 3`

    ```c
    pactffi_with_header_v2(handle, InteractionPart::Request, "x-id", 0, "2");
    pactffi_with_header_v2(handle, InteractionPart::Request, "x-id", 1, "3");
    ```

    Or you can call it once with a JSON value that contains multiple values:

    ```c
    const char* value = "{\"value\": [\"2\",\"3\"]}";
    pactffi_with_header_v2(handle, InteractionPart::Request, "x-id", 0, value);
    ```

    To include matching rules for the header, include the matching rule JSON
    format with the value as a single JSON document. I.e.

    ```c
    const char* value = "{\"value\":\"2\", \"pact:matcher:type\":\"regex\", \"regex\":\"\\\\d+\"}";
    pactffi_with_header_v2(handle, InteractionPart::Request, "id", 0, value);
    ```

    See [IntegrationJson.md](https://github.com/pact-foundation/pact-reference/blob/master/rust/pact_ffi/IntegrationJson.md)

    NOTE: If you pass in a form with multiple values, the index will be ignored.

    # Safety

    The name and value parameters must be valid pointers to NULL terminated strings.
    """  # noqa: E501
    raise NotImplementedError


def set_header(
    interaction: InteractionHandle,
    part: InteractionPart,
    name: str,
    value: str,
) -> bool:
    """
    Sets a header for the Interaction.

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started). Note that this function will overwrite
    any previously set header values. Also, this function will not process the
    value in any way, so matching rules and generators can not be configured
    with it.

    [Rust
    `pactffi_set_header`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_set_header)

    If matching rules are required to be set, use `pactffi_with_header_v2`.

    * `part` - The part of the interaction to add the header to (Request or
      Response).
    * `name` - the header name.
    * `value` - the header value.

    # Safety The name and value parameters must be valid pointers to NULL
    terminated strings.
    """
    raise NotImplementedError


def response_status(interaction: InteractionHandle, status: int) -> bool:
    """
    Configures the response for the Interaction.

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started)

    [Rust
    `pactffi_response_status`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_response_status)

    * `status` - the response status. Defaults to 200.
    """
    raise NotImplementedError


def with_body(
    interaction: InteractionHandle,
    part: InteractionPart,
    content_type: str,
    body: str,
) -> bool:
    """
    Adds the body for the interaction.

    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started)

    [Rust
    `pactffi_with_body`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_with_body)

    * `part` - The part of the interaction to add the body to (Request or
      Response).
    * `content_type` - The content type of the body. Defaults to `text/plain`.
      Will be ignored if a content type header is already set.
    * `body` - The body contents. For JSON payloads, matching rules can be
      embedded in the body. See
      [IntegrationJson.md](https://github.com/pact-foundation/pact-reference/blob/master/rust/pact_ffi/IntegrationJson.md)

    For HTTP and async message interactions, this will overwrite the body. With
    asynchronous messages, the part parameter will be ignored. With synchronous
    messages, the request contents will be overwritten, while a new response
    will be appended to the message.

    # Safety

    The interaction contents and content type must either be NULL pointers, or
    point to valid UTF-8 encoded NULL-terminated strings. Otherwise, behaviour
    is undefined.

    # Error Handling

    If the contents is a NULL pointer, it will set the body contents as null. If
    the content type is a null pointer, or can't be parsed, it will set the
    content type as TEXT. Returns false if the interaction or Pact can't be
    modified (i.e. the mock server for it has already started) or an error has
    occurred.
    """
    raise NotImplementedError


def with_binary_file(
    interaction: InteractionHandle,
    part: InteractionPart,
    content_type: str,
    body: List[int],
    size: int,
) -> bool:
    """
    Adds a binary file as the body with the expected content type and contents.

    Will use a mime type matcher to match the body. Returns false if the
    interaction or Pact can't be modified (i.e. the mock server for it has
    already started)

    [Rust
    `pactffi_with_binary_file`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_with_binary_file)

    * `interaction` - Interaction handle to set the body for.
    * `part` - Request or response part.
    * `content_type` - Expected content type.
    * `body` - example body contents in bytes
    * `size` - number of bytes in the body

    For HTTP and async message interactions, this will overwrite the body. With
    asynchronous messages, the part parameter will be ignored. With synchronous
    messages, the request contents will be overwritten, while a new response
    will be appended to the message.

    # Safety

    The content type must be a valid UTF-8 encoded NULL-terminated string. The
    body pointer must be valid for reads of `size` bytes, and it must be
    properly aligned and consecutive.

    # Error Handling

    If the body is a NULL pointer, it will set the body contents as null. If the
    content type is a null pointer, or can't be parsed, it will return false.
    Returns false if the interaction or Pact can't be modified (i.e. the mock
    server for it has already started) or an error has occurred.
    """
    raise NotImplementedError


def with_multipart_file_v2(  # noqa: PLR0913
    interaction: InteractionHandle,
    part: InteractionPart,
    content_type: str,
    file: str,
    part_name: str,
    boundary: str,
) -> StringResult:
    """
    Adds a binary file as the body as a MIME multipart.

    Will use a mime type matcher to match the body. Returns an error if the
    interaction or Pact can't be modified (i.e. the mock server for it has
    already started) or an error occurs.

    [Rust
    `pactffi_with_multipart_file_v2`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_with_multipart_file_v2)

    * `interaction` - Interaction handle to set the body for.
    * `part` - Request or response part.
    * `content_type` - Expected content type of the file.
    * `file` - path to the example file
    * `part_name` - name for the mime part
    * `boundary` - boundary for the multipart separation

    This function can be called multiple times. In that case, each subsequent
    call will be appended to the existing multipart body as a new part.

    # Safety

    The content type, file path and part name must be valid pointers to UTF-8
    encoded NULL-terminated strings. Passing invalid pointers or pointers to
    strings that are not NULL terminated will lead to undefined behaviour.

    # Error Handling

    If the boundary is a NULL pointer, a random string will be used. If the file
    path is a NULL pointer, it will set the body contents as as an empty
    mime-part. If the file path does not point to a valid file, or is not able
    to be read, it will return an error result. If the content type is a null
    pointer, or can't be parsed, it will return an error result. Returns an
    error if the interaction or Pact can't be modified (i.e. the mock server for
    it has already started), the interaction is not an HTTP interaction or some
    other error occurs.
    """
    raise NotImplementedError


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
    `pactffi_with_multipart_file`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_with_multipart_file)

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
    raise NotImplementedError


def pact_handle_get_message_iter(pact: PactHandle) -> PactMessageIterator:
    r"""
    Get an iterator over all the messages of the Pact.

    The returned iterator needs to be freed with
    `pactffi_pact_message_iter_delete`.

    [Rust
    `pactffi_pact_handle_get_message_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_handle_get_message_iter)

    # Safety

    The iterator contains a copy of the Pact, so it is always safe to use.

    # Error Handling

    On failure, this function will return a NULL pointer.

    This function may fail if any of the Rust strings contain embedded null
    ('\0') bytes.
    """
    raise NotImplementedError


def pact_handle_get_sync_message_iter(pact: PactHandle) -> PactSyncMessageIterator:
    r"""
    Get an iterator over all the synchronous messages of the Pact.

    The returned iterator needs to be freed with
    `pactffi_pact_sync_message_iter_delete`.

    [Rust
    `pactffi_pact_handle_get_sync_message_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_handle_get_sync_message_iter)

    # Safety

    The iterator contains a copy of the Pact, so it is always safe to use.

    # Error Handling

    On failure, this function will return a NULL pointer.

    This function may fail if any of the Rust strings contain embedded null
    ('\0') bytes.
    """
    raise NotImplementedError


def pact_handle_get_sync_http_iter(pact: PactHandle) -> PactSyncHttpIterator:
    r"""
    Get an iterator over all the synchronous HTTP request/response interactions.

    The returned iterator needs to be freed with
    `pactffi_pact_sync_http_iter_delete`.

    [Rust
    `pactffi_pact_handle_get_sync_http_iter`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_handle_get_sync_http_iter)

    # Safety

    The iterator contains a copy of the Pact, so it is always safe to use.

    # Error Handling

    On failure, this function will return a NULL pointer.

    This function may fail if any of the Rust strings contain embedded null
    ('\0') bytes.
    """
    raise NotImplementedError


def new_message_pact(consumer_name: str, provider_name: str) -> MessagePactHandle:
    """
    Creates a new Pact Message model and returns a handle to it.

    [Rust
    `pactffi_new_message_pact`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_new_message_pact)

    * `consumer_name` - The name of the consumer for the pact.
    * `provider_name` - The name of the provider for the pact.

    Returns a new `MessagePactHandle`. The handle will need to be freed with the
    `pactffi_free_message_pact_handle` function to release its resources.
    """
    raise NotImplementedError


def new_message(pact: MessagePactHandle, description: str) -> MessageHandle:
    """
    Creates a new Message and returns a handle to it.

    [Rust
    `pactffi_new_message`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_new_message)

    * `description` - The message description. It needs to be unique for each
      Message.

    Returns a new `MessageHandle`.
    """
    raise NotImplementedError


def message_expects_to_receive(message: MessageHandle, description: str) -> None:
    """
    Sets the description for the Message.

    [Rust
    `pactffi_message_expects_to_receive`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_expects_to_receive)

    * `description` - The message description. It needs to be unique for each
      message.
    """
    raise NotImplementedError


def message_given(message: MessageHandle, description: str) -> None:
    """
    Adds a provider state to the Interaction.

    [Rust
    `pactffi_message_given`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_given)

    * `description` - The provider state description. It needs to be unique for
      each message
    """
    raise NotImplementedError


def message_given_with_param(
    message: MessageHandle,
    description: str,
    name: str,
    value: str,
) -> None:
    """
    Adds a provider state to the Message with a parameter key and value.

    [Rust
    `pactffi_message_given_with_param`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_given_with_param)

    * `description` - The provider state description. It needs to be unique.
    * `name` - Parameter name.
    * `value` - Parameter value.
    """
    raise NotImplementedError


def message_with_contents(
    message_handle: MessageHandle,
    content_type: str,
    body: List[int],
    size: int,
) -> None:
    """
    Adds the contents of the Message.

    [Rust
    `pactffi_message_with_contents`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_with_contents)

    Accepts JSON, binary and other payload types. Binary data will be base64
    encoded when serialised.

    Note: For text bodies (plain text, JSON or XML), you can pass in a C string
    (NULL terminated) and the size of the body is not required (it will be
    ignored). For binary bodies, you need to specify the number of bytes in the
    body.

    * `content_type` - The content type of the body. Defaults to `text/plain`,
      supports JSON structures with matchers and binary data.
    * `body` - The body contents as bytes. For text payloads (JSON, XML, etc.),
      a C string can be used and matching rules can be embedded in the body.
    * `content_type` - Expected content type (e.g. application/json,
      application/octet-stream)
    * `size` - number of bytes in the message body to read. This is not required
      for text bodies (JSON, XML, etc.).
    """
    raise NotImplementedError


def message_with_metadata(message_handle: MessageHandle, key: str, value: str) -> None:
    """
    Adds expected metadata to the Message.

    [Rust
    `pactffi_message_with_metadata`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_with_metadata)

    * `key` - metadata key
    * `value` - metadata value.
    """
    raise NotImplementedError


def message_reify(message_handle: MessageHandle) -> str:
    """
    Reifies the given message.

    [Rust
    `pactffi_message_reify`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_message_reify)

    Reification is the process of stripping away any matchers, and returning the
    original contents. NOTE: the returned string needs to be deallocated with
    the `free_string` function
    """
    raise NotImplementedError


def write_message_pact_file(
    pact: MessagePactHandle,
    directory: str,
    *,
    overwrite: bool,
) -> int:
    """
    External interface to write out the message pact file.

    This function should be called if all the consumer tests have passed. The
    directory to write the file to is passed as the second parameter. If a NULL
    pointer is passed, the current working directory is used.

    [Rust
    `pactffi_write_message_pact_file`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_write_message_pact_file)

    If overwrite is true, the file will be overwritten with the contents of the
    current pact. Otherwise, it will be merged with any existing pact file.

    Returns 0 if the pact file was successfully written. Returns a positive code
    if the file can not be written, or there is no mock server running on that
    port or the function panics.

    # Errors

    Errors are returned as positive values.

    | Error | Description |
    |-------|-------------|
    | 1 | The pact file was not able to be written |
    | 2 | The message pact for the given handle was not found |
    """
    raise NotImplementedError


def with_message_pact_metadata(
    pact: MessagePactHandle,
    namespace_: str,
    name: str,
    value: str,
) -> None:
    """
    Sets the additional metadata on the Pact file.

    Common uses are to add the client library details such as the name and
    version

    [Rust
    `pactffi_with_message_pact_metadata`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_with_message_pact_metadata)

    * `pact` - Handle to a Pact model
    * `namespace` - the top level metadat key to set any key values on
    * `name` - the key to set
    * `value` - the value to set
    """
    raise NotImplementedError


def pact_handle_write_file(pact: PactHandle, directory: str, *, overwrite: bool) -> int:
    """
    External interface to write out the pact file.

    This function should be called if all the consumer tests have passed. The
    directory to write the file to is passed as the second parameter. If a NULL
    pointer is passed, the current working directory is used.

    [Rust
    `pactffi_pact_handle_write_file`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_pact_handle_write_file)

    If overwrite is true, the file will be overwritten with the contents of the
    current pact. Otherwise, it will be merged with any existing pact file.

    Returns 0 if the pact file was successfully written. Returns a positive code
    if the file can not be written or the function panics.

    # Safety

    The directory parameter must either be NULL or point to a valid NULL
    terminated string.

    # Errors

    Errors are returned as positive values.

    | Error | Description |
    |-------|-------------|
    | 1 | The function panicked. |
    | 2 | The pact file was not able to be written. |
    | 3 | The pact for the given handle was not found. |
    """
    raise NotImplementedError


def new_async_message(pact: PactHandle, description: str) -> MessageHandle:
    """
    Creates a new V4 asynchronous message and returns a handle to it.

    [Rust
    `pactffi_new_async_message`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_new_async_message)

    * `description` - The message description. It needs to be unique for each
      Message.

    Returns a new `MessageHandle`.
    """
    raise NotImplementedError


def free_pact_handle(pact: PactHandle) -> int:
    """
    Delete a Pact handle and free the resources used by it.

    [Rust
    `pactffi_free_pact_handle`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_free_pact_handle)

    # Error Handling

    On failure, this function will return a positive integer value.

    * `1` - The handle is not valid or does not refer to a valid Pact. Could be
      that it was previously deleted.

    """
    raise NotImplementedError


def free_message_pact_handle(pact: MessagePactHandle) -> int:
    """
    Delete a Pact handle and free the resources used by it.

    [Rust
    `pactffi_free_message_pact_handle`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_free_message_pact_handle)

    # Error Handling

    On failure, this function will return a positive integer value.

    * `1` - The handle is not valid or does not refer to a valid Pact. Could be
      that it was previously deleted.

    """
    raise NotImplementedError


def verify(args: str) -> int:
    """
    External interface to verifier a provider.

    [Rust `pactffi_verify`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verify)

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


def verifier_new() -> VerifierHandle:
    """
    Get a Handle to a newly created verifier.

    You should call `pactffi_verifier_shutdown` when done with the verifier to
    free all allocated resources.

    [Rust
    `pactffi_verifier_new`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_new)

    Deprecated: This function is deprecated. Use
    `pactffi_verifier_new_for_application` which allows the calling
    application/framework name and version to be specified.

    # Safety

    This function is safe.

    # Error Handling

    Returns NULL on error.
    """
    warnings.warn(
        "This function is deprecated, use verifier_new_for_application instead",
        DeprecationWarning,
        stacklevel=2,
    )
    raise NotImplementedError


def verifier_new_for_application(name: str, version: str) -> VerifierHandle:
    """
    Get a Handle to a newly created verifier.

    You should call `pactffi_verifier_shutdown` when done with the verifier to
    free all allocated resources

    [Rust
    `pactffi_verifier_new_for_application`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_new_for_application)

    # Safety

    This function is safe.

    # Error Handling

    Returns NULL on error.
    """
    raise NotImplementedError


def verifier_shutdown(handle: VerifierHandle) -> None:
    """
    Shutdown the verifier and release all resources.

    [Rust `pactffi_verifier_shutdown`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_shutdown)
    """
    raise NotImplementedError


def verifier_set_provider_info(  # noqa: PLR0913
    handle: VerifierHandle,
    name: str,
    scheme: str,
    host: str,
    port: int,
    path: str,
) -> None:
    """
    Set the provider details for the Pact verifier.

    Passing a NULL for any field will use the default value for that field.

    [Rust
    `pactffi_verifier_set_provider_info`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_set_provider_info)

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.
    """
    raise NotImplementedError


def verifier_add_provider_transport(
    handle: VerifierHandle,
    protocol: str,
    port: int,
    path: str,
    scheme: str,
) -> None:
    """
    Adds a new transport for the given provider.

    Passing a NULL for any field will use the default value for that field.

    [Rust
    `pactffi_verifier_add_provider_transport`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_add_provider_transport)

    For non-plugin based message interactions, set protocol to "message" and set
    scheme to an empty string or "https" if secure HTTP is required.
    Communication to the calling application will be over HTTP to the default
    provider hostname.

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.
    """
    raise NotImplementedError


def verifier_set_filter_info(
    handle: VerifierHandle,
    filter_description: str,
    filter_state: str,
    filter_no_state: int,
) -> None:
    """
    Set the filters for the Pact verifier.

    [Rust
    `pactffi_verifier_set_filter_info`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_set_filter_info)

    If `filter_description` is not empty, it needs to be as a regular
    expression.

    `filter_no_state` is a boolean value. Set it to greater than zero to turn
    the option on.

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.

    """
    raise NotImplementedError


def verifier_set_provider_state(
    handle: VerifierHandle,
    url: str,
    teardown: int,
    body: int,
) -> None:
    """
    Set the provider state URL for the Pact verifier.

    [Rust
    `pactffi_verifier_set_provider_state`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_set_provider_state)

    `teardown` is a boolean value. If teardown state change requests should be
    made after an interaction is validated (default is false). Set it to greater
    than zero to turn the option on. `body` is a boolean value. Sets if state
    change request data should be sent in the body (> 0, true) or as query
    parameters (== 0, false). Set it to greater than zero to turn the option on.

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.

    """
    raise NotImplementedError


def verifier_set_verification_options(
    handle: VerifierHandle,
    disable_ssl_verification: int,
    request_timeout: int,
) -> int:
    """
    Set the options used by the verifier when calling the provider.

    [Rust
    `pactffi_verifier_set_verification_options`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_set_verification_options)

    `disable_ssl_verification` is a boolean value. Set it to greater than zero
    to turn the option on.

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.

    """
    raise NotImplementedError


def verifier_set_coloured_output(handle: VerifierHandle, coloured_output: int) -> int:
    """
    Enables or disables coloured output using ANSI escape codes.

    By default, coloured output is enabled.

    [Rust
    `pactffi_verifier_set_coloured_output`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_set_coloured_output)

    `coloured_output` is a boolean value. Set it to greater than zero to turn
    the option on.

    # Safety

    This function is safe as long as the handle pointer points to a valid
    handle.

    """
    raise NotImplementedError


def verifier_set_no_pacts_is_error(handle: VerifierHandle, is_error: int) -> int:
    """
    Enables or disables if no pacts are found to verify results in an error.

    [Rust
    `pactffi_verifier_set_no_pacts_is_error`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_set_no_pacts_is_error)

    `is_error` is a boolean value. Set it to greater than zero to enable an
    error when no pacts are found to verify, and set it to zero to disable this.

    # Safety

    This function is safe as long as the handle pointer points to a valid
    handle.

    """
    raise NotImplementedError


def verifier_set_publish_options(  # noqa: PLR0913
    handle: VerifierHandle,
    provider_version: str,
    build_url: str,
    provider_tags: List[str],
    provider_tags_len: int,
    provider_branch: str,
) -> int:
    """
    Set the options used when publishing verification results to the Broker.

    [Rust
    `pactffi_verifier_set_publish_options`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_set_publish_options)

    # Args

    - `handle` - The pact verifier handle to update
    - `provider_version` - Version of the provider to publish
    - `build_url` - URL to the build which ran the verification
    - `provider_tags` - Collection of tags for the provider
    - `provider_tags_len` - Number of provider tags supplied
    - `provider_branch` - Name of the branch used for verification

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.

    """
    raise NotImplementedError


def verifier_set_consumer_filters(
    handle: VerifierHandle,
    consumer_filters: List[str],
    consumer_filters_len: int,
) -> None:
    """
    Set the consumer filters for the Pact verifier.

    [Rust
    `pactffi_verifier_set_consumer_filters`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_set_consumer_filters)

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.

    """
    raise NotImplementedError


def verifier_add_custom_header(
    handle: VerifierHandle,
    header_name: str,
    header_value: str,
) -> None:
    """
    Adds a custom header to be added to the requests made to the provider.

    [Rust
    `pactffi_verifier_add_custom_header`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_add_custom_header)

    # Safety

    The header name and value must point to a valid NULL terminated string and
    must contain valid UTF-8.
    """
    raise NotImplementedError


def verifier_add_file_source(handle: VerifierHandle, file: str) -> None:
    """
    Adds a Pact file as a source to verify.

    [Rust
    `pactffi_verifier_add_file_source`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_add_file_source)

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.

    """
    raise NotImplementedError


def verifier_add_directory_source(handle: VerifierHandle, directory: str) -> None:
    """
    Adds a Pact directory as a source to verify.

    All pacts from the directory that match the provider name will be verified.

    [Rust
    `pactffi_verifier_add_directory_source`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_add_directory_source)

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.

    """
    raise NotImplementedError


def verifier_url_source(
    handle: VerifierHandle,
    url: str,
    username: str,
    password: str,
    token: str,
) -> None:
    """
    Adds a URL as a source to verify.

    The Pact file will be fetched from the URL.

    [Rust
    `pactffi_verifier_url_source`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_url_source)

    If a username and password is given, then basic authentication will be used
    when fetching the pact file. If a token is provided, then bearer token
    authentication will be used.

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.

    """
    raise NotImplementedError


def verifier_broker_source(
    handle: VerifierHandle,
    url: str,
    username: str,
    password: str,
    token: str,
) -> None:
    """
    Adds a Pact broker as a source to verify.

    This will fetch all the pact files from the broker that match the provider
    name.

    [Rust
    `pactffi_verifier_broker_source`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_broker_source)

    If a username and password is given, then basic authentication will be used
    when fetching the pact file. If a token is provided, then bearer token
    authentication will be used.

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.

    """
    raise NotImplementedError


def verifier_broker_source_with_selectors(  # noqa: PLR0913
    handle: VerifierHandle,
    url: str,
    username: str,
    password: str,
    token: str,
    enable_pending: int,
    include_wip_pacts_since: str,
    provider_tags: List[str],
    provider_tags_len: int,
    provider_branch: str,
    consumer_version_selectors: List[str],
    consumer_version_selectors_len: int,
    consumer_version_tags: List[str],
    consumer_version_tags_len: int,
) -> None:
    """
    Adds a Pact broker as a source to verify.

    This will fetch all the pact files from the broker that match the provider
    name and the consumer version selectors (See
    `https://docs.pact.io/pact_broker/advanced_topics/consumer_version_selectors/`).

    [Rust
    `pactffi_verifier_broker_source_with_selectors`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_broker_source_with_selectors)

    The consumer version selectors must be passed in in JSON format.

    `enable_pending` is a boolean value. Set it to greater than zero to turn the
    option on.

    If the `include_wip_pacts_since` option is provided, it needs to be a date
    formatted in ISO format (YYYY-MM-DD).

    If a username and password is given, then basic authentication will be used
    when fetching the pact file. If a token is provided, then bearer token
    authentication will be used.

    # Safety

    All string fields must contain valid UTF-8. Invalid UTF-8 will be replaced
    with U+FFFD REPLACEMENT CHARACTER.

    """
    raise NotImplementedError


def verifier_execute(handle: VerifierHandle) -> int:
    """
    Runs the verification.

    [Rust `pactffi_verifier_execute`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_execute)

    # Error Handling

    Errors will be reported with a non-zero return value.
    """
    raise NotImplementedError


def verifier_cli_args() -> str:
    """
    External interface to retrieve the CLI options and arguments.

    This available when calling the CLI interface, returning them as a JSON
    string.

    [Rust
    `pactffi_verifier_cli_args`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_cli_args)

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


def verifier_logs(handle: VerifierHandle) -> str:
    """
    Extracts the logs for the verification run.

    This needs the memory buffer log sink to be setup before the verification is
    executed. The returned string will need to be freed with the `free_string`
    function call to avoid leaking memory.

    [Rust
    `pactffi_verifier_logs`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_logs)

    Will return a NULL pointer if the logs for the verification can not be
    retrieved.
    """
    raise NotImplementedError


def verifier_logs_for_provider(provider_name: str) -> str:
    """
    Extracts the logs for the verification run for the provider name.

    This needs the memory buffer log sink to be setup before the verification is
    executed. The returned string will need to be freed with the `free_string`
    function call to avoid leaking memory.

    [Rust
    `pactffi_verifier_logs_for_provider`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_logs_for_provider)

    Will return a NULL pointer if the logs for the verification can not be
    retrieved.
    """
    raise NotImplementedError


def verifier_output(handle: VerifierHandle, strip_ansi: int) -> str:
    """
    Extracts the standard output for the verification run.

    The returned string will need to be freed with the `free_string` function
    call to avoid leaking memory.

    [Rust
    `pactffi_verifier_output`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_output)

    * `strip_ansi` - This parameter controls ANSI escape codes. Setting it to a
      non-zero value
    will cause the ANSI control codes to be stripped from the output.

    Will return a NULL pointer if the handle is invalid.
    """
    raise NotImplementedError


def verifier_json(handle: VerifierHandle) -> str:
    """
    Extracts the verification result as a JSON document.

    The returned string will need to be freed with the `free_string` function
    call to avoid leaking memory.

    [Rust
    `pactffi_verifier_json`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_verifier_json)

    Will return a NULL pointer if the handle is invalid.
    """
    raise NotImplementedError


def using_plugin(pact: PactHandle, plugin_name: str, plugin_version: str) -> int:
    """
    Add a plugin to be used by the test.

    The plugin needs to be installed correctly for this function to work.

    [Rust
    `pactffi_using_plugin`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_using_plugin)

    * `plugin_name` is the name of the plugin to load.
    * `plugin_version` is the version of the plugin to load. It is optional, and
      can be NULL.

    Returns zero on success, and a positive integer value on failure.

    Note that plugins run as separate processes, so will need to be cleaned up
    afterwards by calling `pactffi_cleanup_plugins` otherwise you will have
    plugin processes left running.

    # Safety

    `plugin_name` must be a valid pointer to a NULL terminated string.
    `plugin_version` may be null, and if not NULL must also be a valid pointer
    to a NULL terminated string. Invalid pointers will result in undefined
    behaviour.

    # Errors

    * `1` - A general panic was caught.
    * `2` - Failed to load the plugin.
    * `3` - Pact Handle is not valid.

    When an error errors, LAST_ERROR will contain the error message.
    """
    raise NotImplementedError


def cleanup_plugins(pact: PactHandle) -> None:
    """
    Decrement the access count on any plugins that are loaded for the Pact.

    This will shutdown any plugins that are no longer required (access count is
    zero).

    [Rust
    `pactffi_cleanup_plugins`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_cleanup_plugins)
    """
    raise NotImplementedError


def interaction_contents(
    interaction: InteractionHandle,
    part: InteractionPart,
    content_type: str,
    contents: str,
) -> int:
    """
    Setup the interaction part using a plugin.

    The contents is a JSON string that will be passed on to the plugin to
    configure the interaction part. Refer to the plugin documentation on the
    format of the JSON contents.

    [Rust
    `pactffi_interaction_contents`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_interaction_contents)

    Returns zero on success, and a positive integer value on failure.

    * `interaction` - Handle to the interaction to configure.
    * `part` - The part of the interaction to configure (request or response).
      It is ignored for messages.
    * `content_type` - NULL terminated C string of the content type of the part.
    * `contents` - NULL terminated C string of the JSON contents that gets
      passed to the plugin.

    # Safety

    `content_type` and `contents` must be a valid pointers to NULL terminated
    strings. Invalid pointers will result in undefined behaviour.

    # Errors

    * `1` - A general panic was caught.
    * `2` - The mock server has already been started.
    * `3` - The interaction handle is invalid.
    * `4` - The content type is not valid.
    * `5` - The contents JSON is not valid JSON.
    * `6` - The plugin returned an error.

    When an error errors, LAST_ERROR will contain the error message.
    """
    raise NotImplementedError


def matches_string_value(
    matching_rule: MatchingRule,
    expected_value: str,
    actual_value: str,
    cascaded: int,
) -> str:
    """
    Determines if the string value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_string_value`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matches_string_value)

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
) -> str:
    """
    Determines if the unsigned integer value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_u64_value`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matches_u64_value)

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
) -> str:
    """
    Determines if the signed integer value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_i64_value`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matches_i64_value)

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
) -> str:
    """
    Determines if the floating point value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_f64_value`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matches_f64_value)

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
) -> str:
    """
    Determines if the boolean value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_bool_value`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matches_bool_value)

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
) -> str:
    """
    Determines if the binary value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_binary_value`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matches_binary_value)

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
) -> str:
    """
    Determines if the JSON value matches the given matching rule.

    If the value matches OK, will return a NULL pointer. If the value does not
    match, will return a error message as a NULL terminated string. The error
    message pointer will need to be deleted with the `pactffi_string_delete`
    function once it is no longer required.

    [Rust
    `pactffi_matches_json_value`](https://docs.rs/pact_ffi/0.4.9/pact_ffi/?search=pactffi_matches_json_value)

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
