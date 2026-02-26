"""
Utility functions for Pact.

This module defines a number of utility functions that are used in specific
contexts within the Pact library. These functions are not intended to be
used directly by consumers of the library and as such, may change without
notice.
"""

from __future__ import annotations

import asyncio
import contextvars
import dis
import inspect
import logging
import socket
import warnings
from contextlib import closing
from functools import partial
from inspect import Parameter, _ParameterKind
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine, Mapping

try:
    import sniffio  # type: ignore[import-not-found]
except ImportError:
    sniffio = None  # type: ignore[assignment]

try:
    import trio  # type: ignore[import-not-found]
    from trio.lowlevel import current_trio_token  # type: ignore[import-not-found]
except ImportError:
    trio = None  # type: ignore[assignment]
    current_trio_token = None  # type: ignore[assignment]

try:
    import curio  # type: ignore[import-not-found,import-untyped]
except (ImportError, AttributeError):
    curio = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

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

_T = TypeVar("_T")


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
            will typically be a single character, but may be two characters for
            some codes.

    Returns:
        The equivalent Java SimpleDateFormat format string.

    Raises:
        ValueError:
            If the code is locale-dependent or unsupported.
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
    if code == "w":
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


def apply_args(f: Callable[..., _T], args: Mapping[str, object]) -> _T:  # noqa: C901, PLR0912
    """
    Apply arguments to a function.

    This function passes through the arguments to the function, doing so
    intelligently by performing runtime introspection to determine whether
    it is possible to pass arguments by name, and falling back to positional
    arguments if not.

    This function supports both synchronous and asynchronous callables. If the
    callable is a coroutine function, it will be executed in an event loop.

    Args:
        f:
            The function to apply the arguments to.

        args:
            The arguments to apply. The dictionary is ordered such that, if an
            argument cannot be passed by name, it will be passed by position
            as per the order of the keys in the dictionary.

    Returns:
        The result of the function.
    """
    # Check if f is a partial wrapping an async function
    func_to_check = f.func if isinstance(f, partial) else f
    is_async = inspect.iscoroutinefunction(func_to_check)
    signature = inspect.signature(f)
    f_name = (
        f.__qualname__
        if hasattr(f, "__qualname__")
        else f"{type(f).__module__}.{type(f).__name__}"
    )
    args = dict(args)

    # If the signature has a `*args` parameter, then parameters which appear as
    # positional-or-keyword must be passed as positional arguments.
    if any(
        param.kind == Parameter.VAR_POSITIONAL
        for param in signature.parameters.values()
    ):
        positional_match: list[_ParameterKind] = [
            Parameter.POSITIONAL_ONLY,
            Parameter.POSITIONAL_OR_KEYWORD,
        ]
        keyword_match: list[_ParameterKind] = [Parameter.KEYWORD_ONLY]
    else:
        positional_match = [Parameter.POSITIONAL_ONLY]
        keyword_match = [Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY]

    # First, we inspect the keyword arguments and try and pass in some arguments
    # by currying them in.
    for param in signature.parameters.values():
        # Try matching the parameter name, or if it starts with underscore,
        # also try matching without the leading underscore.
        arg_key = None
        if param.name in args:
            arg_key = param.name
        elif (
            param.name.startswith("_")
            and len(param.name) > 1
            and param.name[1:] in args
        ):
            arg_key = param.name[1:]

        if arg_key is None:
            # If a parameter is not known, we will ignore it.
            #
            # If the ignored parameter doesn't have a default value, it will
            # result in a exception, but we will also warn the user here.
            if param.default == Parameter.empty and param.kind not in [
                Parameter.VAR_POSITIONAL,
                Parameter.VAR_KEYWORD,
            ]:
                msg = (
                    f"Function {f_name} appears to have required "
                    f"parameter '{param.name}' that will not be passed"
                )
                warnings.warn(msg, stacklevel=2)

            continue

        if param.kind in positional_match:
            # We iterate through the parameters in order that they are defined,
            # making it fine to pass them in by position one at a time.
            f = partial(f, args[arg_key])
            del args[arg_key]
            continue

        if param.kind in keyword_match:
            f = partial(f, **{param.name: args[arg_key]})
            del args[arg_key]
            continue

    # At this stage, we have checked all arguments. If we have any arguments
    # remaining, we will try and pass them through variadic arguments if the
    # function accepts them.
    if args:
        if Parameter.VAR_KEYWORD in [
            param.kind for param in signature.parameters.values()
        ]:
            f = partial(f, **args)
            args.clear()
        elif Parameter.VAR_POSITIONAL in [
            param.kind for param in signature.parameters.values()
        ]:
            f = partial(f, *args.values())
            args.clear()
        else:
            logger.debug(
                "Function %s was called with remaining arguments: %s. "
                "This is not necessarily a bug; whether extra arguments are "
                "acceptable depends on the function's signature and intended usage.",
                f_name,
                list(args.keys()),
                extra={
                    "function_name": f_name,
                    "remaining_args": list(args.keys()),
                },
            )

    try:
        if is_async:
            result = f()
            if inspect.iscoroutine(result):
                return _run_async_coroutine(result)
            return result
        return f()
    except Exception:
        logger.exception("Error occurred while calling function %s", f_name)
        raise


def _run_async_coroutine(coro: Coroutine[Any, Any, _T]) -> _T:  # noqa: C901
    """
    Run a coroutine in an event loop.

    Detects the async runtime (asyncio, trio, or curio) and executes the
    coroutine appropriately. Preserves ContextVars when creating a new event
    loop, which is important when handlers are called from threads.

    Args:
        coro:
            The coroutine to run.

    Returns:
        The result of the coroutine.

    Raises:
        RuntimeError:
            If the detected runtime (trio or curio) is not installed.
    """
    runtime = _detect_async_runtime_from_coroutine(coro)

    if runtime == "trio":
        if trio is None:
            msg = "trio is not installed"
            raise RuntimeError(msg)

        if current_trio_token is not None:
            try:
                token = current_trio_token()

                async def _run_with_token() -> _T:
                    return await coro

                return trio.from_thread.run_sync(_run_with_token, trio_token=token)  # type: ignore[return-value]
            except RuntimeError:
                pass

        ctx = contextvars.copy_context()

        async def _run_trio() -> _T:
            return await coro

        return ctx.run(trio.run, _run_trio)

    if runtime == "curio":
        if curio is None:
            msg = "curio is not installed"
            raise RuntimeError(msg)

        try:
            return curio.AWAIT(coro)
        except RuntimeError:
            ctx = contextvars.copy_context()

            async def _run_curio() -> _T:
                return await coro

            return ctx.run(curio.run, _run_curio)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        future: asyncio.Future[_T] = asyncio.run_coroutine_threadsafe(coro, loop)  # type: ignore[arg-type,assignment]
        return future.result()

    ctx = contextvars.copy_context()
    return ctx.run(asyncio.run, coro)  # type: ignore[arg-type,return-value]


def _detect_async_runtime_from_coroutine(coro: Coroutine[Any, Any, _T]) -> str:  # noqa: C901
    """
    Detect async runtime by inspecting the coroutine object.

    Args:
        coro:
            The coroutine object to inspect.

    Returns:
        The detected runtime: "asyncio", "trio", or "curio".
    """
    if sniffio is not None:
        try:
            return sniffio.current_async_library()
        except sniffio.AsyncLibraryNotFoundError:
            pass

    # Inspect bytecode to check for qualified attribute access (e.g., trio.sleep)
    # This is more robust than just checking co_names for module and method separately
    func_code = coro.cr_code  # type: ignore[attr-defined]

    # Parse bytecode to find LOAD_GLOBAL/LOAD_NAME followed by LOAD_ATTR patterns
    # This detects qualified accesses like `trio.sleep()` or `curio.spawn()`
    bytecode = list(dis.get_instructions(func_code))

    trio_detected = False
    curio_detected = False

    for i, instr in enumerate(bytecode):
        # Check for module.attribute pattern (LOAD_GLOBAL/LOAD_NAME + LOAD_ATTR)
        if instr.opname in ("LOAD_GLOBAL", "LOAD_NAME") and i + 1 < len(bytecode):
            next_instr = bytecode[i + 1]
            if next_instr.opname == "LOAD_ATTR":
                module_name = instr.argval
                attr_name = next_instr.argval

                # Check for trio-specific qualified access
                if module_name == "trio":
                    trio_indicators = {
                        "sleep",
                        "open_nursery",
                        "CancelScope",
                        "current_trio_token",
                    }
                    if attr_name in trio_indicators:
                        trio_detected = True

                # Check for curio-specific qualified access
                elif module_name == "curio":
                    curio_indicators = {"sleep", "spawn", "TaskGroup", "AWAIT"}
                    if attr_name in curio_indicators:
                        curio_detected = True

    # Trio takes precedence if both are detected
    if trio_detected:
        return "trio"
    if curio_detected:
        return "curio"

    # Default to asyncio as it's the most common
    return "asyncio"
