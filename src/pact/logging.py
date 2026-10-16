"""
Logging integration between the Pact library and the standard `logging` module.

The Pact FFI and Pact plugins run outside the Python interpreter, so their log
output does not reach `logging` on its own. This module initialises the FFI
once, on the first use of [`Pact`][pact.Pact] or [`Verifier`][verifier.Verifier],
and re-emits every event through `logging`:

-   Events from the Pact library are emitted on the `pact.ffi` logger, with
    the Rust module path appended and its `::` separators replaced by `.`
    (for example `pact.ffi.pact_matching.matchers`). Each record carries
    `log_id` and `test_run_id` as extra attributes. `log_id` identifies the
    operation which emitted the event: the mock server ID while the server
    handles a request, or `verify:<provider name>` while verifying a
    provider. `test_run_id` is the ID set on the emitting thread with
    [`set_test_run_id`][set_test_run_id].
-   Events from plugins are emitted on the `pact.plugins` logger, with
    `plugin_instance_id`, `test_run_id` and `plugin_target` as extra
    attributes.

Nothing needs to be configured. Verbosity is controlled with `logging`:

```python
import logging

logging.getLogger("pact.ffi").setLevel(logging.DEBUG)
```

The FFI forwards events at the most verbose level set explicitly on the
`pact.ffi` and `pact.plugins` loggers, or at [`DEFAULT_LEVEL`][DEFAULT_LEVEL]
when neither is set. That level is fixed when the FFI is initialised, so set
logger levels before creating the first `Pact` or `Verifier`. The Pact
library's `TRACE` level is exposed as [`TRACE`][TRACE], below `logging.DEBUG`.

Log records can be attributed to the test which caused them by setting a test
run ID with [`set_test_run_id`][set_test_run_id]. The pytest plugin in
[`pact.testing.pytest`][testing.pytest] and the `unittest` mixin in
[`pact.testing.unittest`][testing.unittest] do this automatically.

Importing `pact` replaces `pact_ffi.init`, `pact_ffi.init_with_log_level`,
`pact_ffi.log_to_stderr`, `pact_ffi.log_to_stdout` and `pact_ffi.log_to_file`
with functions which emit a `UserWarning` and do nothing else. A logger
applied through one of them before `pact` was imported is kept: events are
still forwarded to `logging`, at the more restrictive of that sink's level and
the level above, and a warning is emitted on the `pact` logger.
"""

from __future__ import annotations

import atexit
import contextlib
import logging
import threading
import warnings
from typing import TYPE_CHECKING

import pact_ffi

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = [
    "DEFAULT_LEVEL",
    "TRACE",
    "ensure_initialised",
    "forwarding_level",
    "from_ffi_level",
    "set_test_run_id",
    "to_ffi_level",
]

logger = logging.getLogger("pact")

# MARK: Level mapping

TRACE = 5
"""
Level of the Pact library's `TRACE` events, below `logging.DEBUG`.
"""

logging.addLevelName(TRACE, "TRACE")

DEFAULT_LEVEL = logging.INFO
"""
Level at which the Pact library forwards events when neither the `pact.ffi` nor
the `pact.plugins` logger has an explicit level.

`INFO` is the default because the library's `DEBUG` output is dominated by
per-FFI-call tracing, per-request matching dumps and, when a plugin is
loaded, transport chatter from `hyper`, `rustls` and `reqwest`, none of
which helps once a test has already passed.
"""

_TO_FFI: list[tuple[int, pact_ffi.LevelFilter]] = [
    (logging.ERROR, pact_ffi.LevelFilter.ERROR),
    (logging.WARNING, pact_ffi.LevelFilter.WARN),
    (logging.INFO, pact_ffi.LevelFilter.INFO),
    (logging.DEBUG, pact_ffi.LevelFilter.DEBUG),
    (TRACE, pact_ffi.LevelFilter.TRACE),
]

_FROM_FFI: dict[str, int] = {
    "TRACE": TRACE,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
}


def to_ffi_level(level: int) -> pact_ffi.LevelFilter:
    """
    Convert a `logging` level to the FFI level filter admitting it.

    Args:
        level:
            A `logging` level. Levels between two standard levels map to the
            more verbose one, so that every record at `level` is admitted.

    Returns:
        The [`LevelFilter`][pact_ffi.LevelFilter] which forwards records at
        `level`.
    """
    for threshold, ffi_level in _TO_FFI:
        if level >= threshold:
            return ffi_level
    return pact_ffi.LevelFilter.TRACE


def from_ffi_level(level: str) -> int:
    """
    Convert a Pact library level name to a `logging` level.

    Args:
        level:
            One of `TRACE`, `DEBUG`, `INFO`, `WARN` or `ERROR`, in any case.

    Returns:
        The matching `logging` level. Unknown names map to `logging.INFO`.
    """
    return _FROM_FFI.get(level.upper(), logging.INFO)


def forwarding_level() -> int:
    """
    `logging` level at which the Pact library forwards events.

    Returns:
        The most verbose level set explicitly on the `pact.ffi` and
        `pact.plugins` loggers, or [`DEFAULT_LEVEL`][DEFAULT_LEVEL] when
        neither has one.
    """
    explicit = [
        lg.level
        for lg in (logging.getLogger("pact.ffi"), logging.getLogger("pact.plugins"))
        if lg.level != logging.NOTSET
    ]
    return min(explicit) if explicit else DEFAULT_LEVEL


def _ffi_level() -> pact_ffi.LevelFilter:
    """
    Level filter to forward events at.

    Returns:
        The [`LevelFilter`][pact_ffi.LevelFilter] admitting every record at
        [`forwarding_level`][forwarding_level].
    """
    return to_ffi_level(forwarding_level())


# MARK: FFI callbacks


def _core_callback(
    log_id: str,
    test_run_id: str,
    level: str,
    target: str,
    message: str,
) -> None:
    # Runs on a thread owned by the Pact library; an exception here has nowhere
    # to go, so it is discarded.
    with contextlib.suppress(Exception):
        name = f"pact.ffi.{target.replace('::', '.')}" if target else "pact.ffi"
        logging.getLogger(name).log(
            from_ffi_level(level),
            "%s",
            message,
            extra={
                "test_run_id": test_run_id or None,
                "log_id": log_id or None,
            },
        )


def _plugin_callback(
    plugin_instance_id: str,
    test_run_id: str,
    level: str,
    target: str,
    message: str,
) -> None:
    with contextlib.suppress(Exception):
        logging.getLogger("pact.plugins").log(
            from_ffi_level(level),
            "%s",
            message,
            extra={
                "plugin_instance_id": plugin_instance_id,
                "test_run_id": test_run_id or None,
                "plugin_target": target or None,
            },
        )


# MARK: One-time initialisation

_initialised = False
_lock = threading.Lock()


def ensure_initialised() -> None:
    """
    Initialise the Pact library's logging once.

    Applies a logger with no visible sink at the level returned by
    `_ffi_level`, registers the callbacks which re-emit library and plugin
    events through `logging`, and registers an `atexit` hook which
    deregisters them again. Later calls return immediately.

    If a logger was already applied, through one of the `pact_ffi.log_to_*`
    functions called before `pact` was imported, a warning is logged on the
    `pact` logger and the callbacks are registered against that logger
    instead.
    """
    global _initialised  # noqa: PLW0603

    with _lock:
        if _initialised:
            return
        pact_ffi.set_log_callback_level(_ffi_level())
        try:
            pact_ffi.log_to_buffer(pact_ffi.LevelFilter.OFF)
        except RuntimeError:
            logger.warning(
                "Pact FFI logging was configured externally; "
                "events more verbose than that sink are not forwarded to logging."
            )
        pact_ffi.register_log_callback(_core_callback)
        pact_ffi.register_plugin_log_callback(_plugin_callback)
        atexit.register(_shutdown)
        _initialised = True


def _shutdown() -> None:
    """
    Stop forwarding events and deregister the callbacks.

    Registered with `atexit` by [`ensure_initialised`][ensure_initialised].
    """
    # A callback fired from a library thread during interpreter finalisation
    # cannot acquire the GIL and aborts the process.
    with contextlib.suppress(Exception):
        pact_ffi.set_log_callback_level("OFF")
    with contextlib.suppress(Exception):
        pact_ffi.register_log_callback(None)
    with contextlib.suppress(Exception):
        pact_ffi.register_plugin_log_callback(None)


# MARK: FFI logger stand-ins

_REPLACED_FFI_FUNCTIONS = (
    "init",
    "init_with_log_level",
    "log_to_stderr",
    "log_to_stdout",
    "log_to_file",
)


def _stand_in(name: str) -> Callable[..., None]:
    """
    Create a replacement for a `pact_ffi` function which applies a logger.

    Pact Python applies the FFI logger itself, and the logger can be applied
    once per process. A suite which still calls one of these functions after
    `pact` is imported gets a warning in place of the FFI's "Logger already
    initialized" error.

    Args:
        name:
            Name of the `pact_ffi` function being replaced.

    Returns:
        A function accepting any arguments, which emits a `UserWarning` and
        returns `None`.
    """

    def stand_in(*_args: object, **_kwargs: object) -> None:
        warnings.warn(
            f"pact_ffi.{name} has no effect: Pact Python forwards the Pact "
            "library's logs to the logging module. Remove the call and set the "
            "levels of the 'pact.ffi' and 'pact.plugins' loggers instead.",
            UserWarning,
            stacklevel=2,
        )

    stand_in.__name__ = stand_in.__qualname__ = name
    return stand_in


for _name in _REPLACED_FFI_FUNCTIONS:
    setattr(pact_ffi, _name, _stand_in(_name))


# MARK: Test Run ID


def set_test_run_id(test_run_id: str | None) -> None:
    """
    Set the test run ID for the current thread.

    The ID is reported as the `test_run_id` attribute on the records the Pact
    library emits from the current thread. It is also attached to every
    request sent to a plugin from the current thread, so the log entries the
    plugin sends back while handling that request carry it too. Lines a
    plugin writes to its stderr do not.

    Records from the library's own threads do not carry this ID, and are
    identified by their `log_id` instead. While the mock server handles a
    request, `log_id` is the mock server ID and `test_run_id` is `None`.
    While a provider is verified, `log_id` is `verify:<provider name>` and
    most records carry an ID which the verifier generates for the run as
    `test_run_id`.

    Args:
        test_run_id:
            The identifier to attach, such as pytest's `request.node.nodeid`,
            or `None` to clear a previously set ID.
    """
    pact_ffi.set_test_run_id(test_run_id)
