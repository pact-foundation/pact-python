"""
Unit tests for [`pact.plugins`][pact.plugins].
"""

from __future__ import annotations

import json
import logging
import sys
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from pact import Pact, plugins
from pact.plugins import PluginLogEntry

if TYPE_CHECKING:
    from pathlib import Path


class TestPluginLogEntry:
    """Tests for [`PluginLogEntry`][pact.plugins.PluginLogEntry]."""

    def test_from_dict(self) -> None:
        entry = PluginLogEntry.from_dict({
            "plugin_name": "protobuf",
            "plugin_instance_id": "abc",
            "test_run_id": "tests/test_x.py::test_y",
            "level": "WARN",
            "message": "something",
            "target": "plugin::module",
            "timestamp_ms": 1_700_000_000_000,
            "source": "LogRpc",
        })
        assert entry == PluginLogEntry(
            plugin_instance_id="abc",
            level="WARN",
            message="something",
            test_run_id="tests/test_x.py::test_y",
            target="plugin::module",
            plugin_name="protobuf",
            timestamp=datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC),
            source="LogRpc",
        )

    def test_from_dict_optional_fields(self) -> None:
        entry = PluginLogEntry.from_dict({
            "plugin_instance_id": "abc",
            "test_run_id": None,
            "level": "INFO",
            "message": "something",
            "target": None,
        })
        assert entry.test_run_id is None
        assert entry.target is None
        assert entry.plugin_name is None
        assert entry.timestamp is None
        assert entry.source is None

    @pytest.mark.parametrize(
        ("level", "expected"),
        [
            pytest.param("TRACE", 5, id="trace"),
            pytest.param("WARN", logging.WARNING, id="warn"),
            pytest.param("BOGUS", logging.INFO, id="unknown"),
        ],
    )
    def test_logging_level(self, level: str, expected: int) -> None:
        entry = PluginLogEntry(plugin_instance_id="abc", level=level, message="")
        assert entry.logging_level == expected


class TestGetLogs:
    """Tests for [`get_logs`][pact.plugins.get_logs]."""

    def test_unknown_instance(self) -> None:
        assert plugins.get_logs("does-not-exist") == []

    @pytest.mark.skipif(sys.platform == "win32", reason="fake plugin is a shell script")
    def test_buffered_stderr(
        self,
        caplog: pytest.LogCaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        # A plugin which writes to stderr and exits without completing the
        # handshake. Its instance ID is only reported on the forwarded records.
        plugin_dir = tmp_path / "fake-0.0.1"
        plugin_dir.mkdir()
        (plugin_dir / "pact-plugin.json").write_text(
            json.dumps({
                "pluginInterfaceVersion": 1,
                "name": "fake",
                "version": "0.0.1",
                "executableType": "exec",
                "entryPoint": "fake-plugin",
            })
        )
        entry_point = plugin_dir / "fake-plugin"
        entry_point.write_text("#!/bin/sh\necho 'fake plugin starting' >&2\nexit 1\n")
        entry_point.chmod(0o755)
        monkeypatch.setenv("PACT_PLUGIN_DIR", str(tmp_path))
        monkeypatch.setenv("PACT_DO_NOT_TRACK", "true")
        caplog.set_level(logging.DEBUG, logger="pact.plugins")

        pact = Pact("consumer", "provider").with_specification("V4")
        with pytest.raises(RuntimeError, match="Failed to load the plugin fake"):
            pact.using_plugin("fake", "0.0.1")

        # The plugin's output is read on a separate thread, which may lag
        # behind the failed load.
        instance_ids: set[str] = set()
        deadline = time.monotonic() + 5
        while not instance_ids and time.monotonic() < deadline:
            instance_ids = {
                r.__dict__["plugin_instance_id"]
                for r in caplog.records
                if r.name == "pact.plugins" and r.getMessage() == "fake plugin starting"
            }
            time.sleep(0.05)
        assert len(instance_ids) == 1

        entries = plugins.get_logs(instance_ids.pop())

        entry = next(e for e in entries if e.message == "fake plugin starting")
        assert entry.plugin_name == "fake"
        assert entry.source == "Stderr"
        assert entry.timestamp is not None
