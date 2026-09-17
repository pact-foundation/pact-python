"""
Plugin observability for Pact.

Pact plugins run as separate processes, so their log output is not visible to
the Python test process by default. This module exposes the mechanisms the Pact
FFI provides to correlate plugin activity with a test and to retrieve plugin
logs:

-   [`set_test_run_id`][plugins.set_test_run_id] tags requests sent to
    plugins from the current thread with an identifier, so that plugin log
    entries can be traced back to the test which caused them.
-   [`register_log_callback`][plugins.register_log_callback] invokes a
    Python callable for every log entry emitted by any running plugin.
-   [`forward_to_logging`][plugins.forward_to_logging] is a ready-made
    callback which emits plugin log entries through the standard library
    `logging` module.
-   [`get_logs`][plugins.get_logs] returns the log entries buffered for a
    plugin instance, whether or not a callback was registered.

The Pact FFI only captures plugin log entries once it has been initialised
with [`init_with_log_level`][pact_ffi.init_with_log_level] or
[`init`][pact_ffi.init]. These also configure the FFI's own logging, in place of
[`log_to_stderr`][pact_ffi.log_to_stderr].

A typical pytest setup initialises the FFI and forwards plugin logs to
`logging` once per session, and tags each test with its node ID:

```python
import pytest

import pact_ffi
from pact import plugins


@pytest.fixture(autouse=True, scope="session")
def plugin_logging():
    pact_ffi.init_with_log_level("INFO")
    plugins.forward_to_logging()


@pytest.fixture(autouse=True)
def plugin_test_run_id(request):
    plugins.set_test_run_id(request.node.nodeid)
    yield request.node.nodeid
    plugins.set_test_run_id(None)
```
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Literal

import pact_ffi

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

logger = logging.getLogger(__name__)

# The FFI's callback is registered once and dispatches to whichever Python
# callable is current, so that deregistration works even though the underlying
# library ignores a NULL registration.
_callback: Callable[[PluginLogEntry], None] | None = None
_trampoline_registered = False

_LEVELS: Mapping[str, int] = {
    "TRACE": logging.DEBUG,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARN": logging.WARNING,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


@dataclass(frozen=True)
class PluginLogEntry:
    """
    A log entry emitted by a running plugin.

    Entries delivered through
    [`register_log_callback`][plugins.register_log_callback] carry only the
    fields the FFI passes to the callback; `plugin_name`, `timestamp` and
    `source` are populated only for entries retrieved with
    [`get_logs`][plugins.get_logs].
    """

    plugin_instance_id: str
    """UUID assigned by the plugin driver when the plugin instance started."""

    level: str
    """Log level: one of `TRACE`, `DEBUG`, `INFO`, `WARN` or `ERROR`."""

    message: str
    """Human-readable log message."""

    test_run_id: str | None = None
    """
    Test run ID set with [`set_test_run_id`][plugins.set_test_run_id]
    when the plugin request was made, if any.
    """

    target: str | None = None
    """Logger name or module path within the plugin, if known."""

    plugin_name: str | None = None
    """Plugin name from its manifest."""

    timestamp: datetime | None = None
    """Time at which the entry was recorded, in UTC."""

    source: Literal["Stderr", "LogRpc"] | None = None
    """
    Where the entry originated: a raw line on the plugin's stderr, or a
    structured record sent over the plugin protocol.
    """

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PluginLogEntry:
        """
        Create an entry from the JSON object emitted by the Pact FFI.

        Args:
            data:
                A single decoded log entry as returned by
                [`get_plugin_logs`][pact_ffi.get_plugin_logs].

        Returns:
            The entry, with `timestamp_ms` converted to a UTC `datetime` and
            empty optional fields normalised to `None`.
        """
        timestamp_ms = data.get("timestamp_ms")
        return cls(
            plugin_instance_id=data["plugin_instance_id"],
            level=data["level"],
            message=data["message"],
            test_run_id=data.get("test_run_id") or None,
            target=data.get("target") or None,
            plugin_name=data.get("plugin_name") or None,
            timestamp=(
                datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
                if timestamp_ms is not None
                else None
            ),
            source=data.get("source"),
        )

    @property
    def logging_level(self) -> int:
        """
        The entry's level as a standard library `logging` level.

        Returns:
            The matching `logging` level constant. Unknown levels map to
            `logging.INFO`.
        """
        return _LEVELS.get(self.level.upper(), logging.INFO)


def set_test_run_id(test_run_id: str | None) -> None:
    """
    Set the test run ID for the current thread.

    The ID is attached to every request sent to a plugin from the current
    thread, and is reported back in the `test_run_id` of the plugin's log
    entries. Using the test's identifier (such as pytest's `request.node.nodeid`)
    makes it possible to attribute plugin logs to the test which triggered them.

    The ID is thread-local, so it must be set on the thread which drives the
    interaction or verification.

    Args:
        test_run_id:
            The identifier to attach, or `None` to clear a previously set ID.
    """
    pact_ffi.set_test_run_id(test_run_id)


def _dispatch(
    plugin_instance_id: str,
    test_run_id: str,
    level: str,
    target: str,
    message: str,
) -> None:
    if _callback is None:
        return
    _callback(
        PluginLogEntry(
            plugin_instance_id=plugin_instance_id,
            level=level,
            message=message,
            test_run_id=test_run_id or None,
            target=target or None,
        )
    )


def register_log_callback(
    callback: Callable[[PluginLogEntry], None] | None,
) -> None:
    """
    Register a callback invoked for every plugin log entry.

    The callback receives a [`PluginLogEntry`][plugins.PluginLogEntry] for
    each entry emitted by any running plugin. Only one callback is active at a
    time; registering a new one replaces the previous one.

    The callback runs on a thread owned by the Pact library, so it must be
    thread-safe and must return promptly. It must not call into Pact itself.
    Exceptions raised by the callback are reported by CFFI and otherwise
    ignored.

    Args:
        callback:
            The callable to invoke, or `None` to stop receiving entries.
    """
    global _callback, _trampoline_registered  # noqa: PLW0603

    _callback = callback
    if callback is not None and not _trampoline_registered:
        pact_ffi.register_plugin_log_callback(_dispatch)
        _trampoline_registered = True


def forward_to_logging(target: logging.Logger | str | None = None) -> None:
    """
    Forward plugin log entries to the standard library `logging` module.

    Each entry is emitted at the equivalent `logging` level, with the plugin
    instance ID, test run ID and target available on the log record as
    `plugin_instance_id`, `test_run_id` and `plugin_target` for use in
    formatters and filters.

    This registers a callback with
    [`register_log_callback`][plugins.register_log_callback], and so
    replaces any callback registered previously.

    Args:
        target:
            The logger, or logger name, to emit entries through. Defaults to
            the `pact.plugins` logger.
    """
    if target is None:
        destination = logger
    elif isinstance(target, str):
        destination = logging.getLogger(target)
    else:
        destination = target

    def _emit(entry: PluginLogEntry) -> None:
        destination.log(
            entry.logging_level,
            "%s",
            entry.message,
            extra={
                "plugin_instance_id": entry.plugin_instance_id,
                "test_run_id": entry.test_run_id,
                "plugin_target": entry.target,
            },
        )

    register_log_callback(_emit)


def get_logs(plugin_instance_id: str) -> list[PluginLogEntry]:
    """
    Return the log entries buffered for a plugin instance.

    The Pact library buffers every plugin log entry for the lifetime of the
    process, independently of any registered callback. The plugin instance ID
    is reported on each [`PluginLogEntry`][plugins.PluginLogEntry], and is
    otherwise not exposed by the library.

    Args:
        plugin_instance_id:
            The plugin instance whose logs to retrieve.

    Returns:
        The buffered entries in the order they were recorded. An unknown
        instance ID yields an empty list.
    """
    return [
        PluginLogEntry.from_dict(entry)
        for entry in pact_ffi.get_plugin_logs(plugin_instance_id)
    ]
