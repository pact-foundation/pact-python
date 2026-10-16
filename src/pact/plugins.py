"""
Plugin log entries buffered by the Pact library.

Pact plugins run as separate processes. Their log entries are forwarded to the
`pact.plugins` logger by [`pact.logging`][logging], and are also buffered
by the Pact library for the lifetime of the process, keyed by plugin instance.
[`get_logs`][plugins.get_logs] returns the buffered entries as
[`PluginLogEntry`][plugins.PluginLogEntry] objects, which carry the plugin
name, timestamp and source in addition to the fields available on the
forwarded log records.

The plugin instance ID is reported on each forwarded record as
`plugin_instance_id`, and is otherwise not exposed by the library.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Literal

import pact_ffi
from pact.logging import ensure_initialised, from_ffi_level

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ["PluginLogEntry", "get_logs"]


@dataclass(frozen=True)
class PluginLogEntry:
    """
    A log entry emitted by a running plugin.

    Entries are returned by [`get_logs`][plugins.get_logs]. Each one is either
    a line the plugin wrote to its stderr or a structured record it sent over
    the plugin protocol, as given by `source`.
    """

    plugin_instance_id: str
    """UUID assigned by the plugin driver when the plugin instance started."""

    level: str
    """Log level: one of `TRACE`, `DEBUG`, `INFO`, `WARN` or `ERROR`."""

    message: str
    """Human-readable log message."""

    test_run_id: str | None = None
    """
    Test run ID set with [`set_test_run_id`][logging.set_test_run_id]
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
                datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)
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
            The matching `logging` level, as given by
            [`from_ffi_level`][logging.from_ffi_level].
        """
        return from_ffi_level(self.level)


def get_logs(plugin_instance_id: str) -> list[PluginLogEntry]:
    """
    Return the log entries buffered for a plugin instance.

    Args:
        plugin_instance_id:
            The plugin instance whose logs to retrieve, as reported on the
            `plugin_instance_id` attribute of forwarded log records.

    Returns:
        The buffered entries in the order they were recorded. An unknown
        instance ID yields an empty list.

    Raises:
        RuntimeError:
            If the Pact library cannot return the buffered entries.
    """
    ensure_initialised()
    return [
        PluginLogEntry.from_dict(entry)
        for entry in pact_ffi.get_plugin_logs(plugin_instance_id)
    ]
