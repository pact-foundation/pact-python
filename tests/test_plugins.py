"""
Unit tests for the [`pact.plugins`][pact.plugins] observability helpers.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pytest

import pact_ffi
from pact import plugins
from pact.plugins import PluginLogEntry

if TYPE_CHECKING:
    from collections.abc import Generator


def emit(
    plugin_instance_id: str = "instance",
    test_run_id: str = "",
    level: str = "INFO",
    target: str = "",
    message: str = "hello",
) -> None:
    """
    Invoke the callback registered with the FFI as the library would.
    """
    callback = pact_ffi._plugin_log_callback  # noqa: SLF001
    assert callback is not None
    callback(
        plugin_instance_id.encode("utf-8"),
        test_run_id.encode("utf-8"),
        level.encode("utf-8"),
        target.encode("utf-8"),
        message.encode("utf-8"),
    )


@pytest.fixture(autouse=True)
def _reset_callback() -> Generator[None, None, None]:
    yield
    plugins.register_log_callback(None)


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
            timestamp=datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc),
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
            pytest.param("TRACE", logging.DEBUG, id="trace"),
            pytest.param("DEBUG", logging.DEBUG, id="debug"),
            pytest.param("INFO", logging.INFO, id="info"),
            pytest.param("WARN", logging.WARNING, id="warn"),
            pytest.param("ERROR", logging.ERROR, id="error"),
            pytest.param("warn", logging.WARNING, id="lowercase"),
            pytest.param("BOGUS", logging.INFO, id="unknown"),
        ],
    )
    def test_logging_level(self, level: str, expected: int) -> None:
        entry = PluginLogEntry(plugin_instance_id="abc", level=level, message="")
        assert entry.logging_level == expected


class TestSetTestRunId:
    """Tests for [`set_test_run_id`][pact.plugins.set_test_run_id]."""

    def test_set_and_clear(self) -> None:
        plugins.set_test_run_id("tests/test_x.py::test_y")
        plugins.set_test_run_id(None)


class TestRegisterLogCallback:
    """Tests for [`register_log_callback`][pact.plugins.register_log_callback]."""

    def test_callback_receives_entry(self) -> None:
        received: list[PluginLogEntry] = []
        plugins.register_log_callback(received.append)

        emit("inst", "run-1", "DEBUG", "mod", "hello")

        assert received == [
            PluginLogEntry(
                plugin_instance_id="inst",
                level="DEBUG",
                message="hello",
                test_run_id="run-1",
                target="mod",
            )
        ]

    def test_empty_strings_become_none(self) -> None:
        received: list[PluginLogEntry] = []
        plugins.register_log_callback(received.append)

        emit(test_run_id="", target="")

        assert received[0].test_run_id is None
        assert received[0].target is None

    def test_replaces_previous_callback(self) -> None:
        first: list[PluginLogEntry] = []
        second: list[PluginLogEntry] = []
        plugins.register_log_callback(first.append)
        plugins.register_log_callback(second.append)

        emit()

        assert first == []
        assert len(second) == 1

    def test_none_deregisters(self) -> None:
        received: list[PluginLogEntry] = []
        plugins.register_log_callback(received.append)
        plugins.register_log_callback(None)

        emit()

        assert received == []


class TestForwardToLogging:
    """Tests for [`forward_to_logging`][pact.plugins.forward_to_logging]."""

    def test_default_logger(self, caplog: pytest.LogCaptureFixture) -> None:
        plugins.forward_to_logging()

        with caplog.at_level(logging.DEBUG, logger="pact.plugins"):
            emit("inst", "run-1", "WARN", "mod", "careful")

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.name == "pact.plugins"
        assert record.levelno == logging.WARNING
        assert record.getMessage() == "careful"
        assert record.__dict__["plugin_instance_id"] == "inst"
        assert record.__dict__["test_run_id"] == "run-1"
        assert record.__dict__["plugin_target"] == "mod"

    def test_named_logger(self, caplog: pytest.LogCaptureFixture) -> None:
        plugins.forward_to_logging("my.plugins")

        with caplog.at_level(logging.DEBUG, logger="my.plugins"):
            emit(level="ERROR", message="boom")

        assert [(r.name, r.levelno) for r in caplog.records] == [
            ("my.plugins", logging.ERROR)
        ]

    def test_logger_instance(self, caplog: pytest.LogCaptureFixture) -> None:
        plugins.forward_to_logging(logging.getLogger("other"))

        with caplog.at_level(logging.DEBUG, logger="other"):
            emit(level="TRACE", message="detail")

        assert [(r.name, r.levelno) for r in caplog.records] == [
            ("other", logging.DEBUG)
        ]


class TestGetLogs:
    """Tests for [`get_logs`][pact.plugins.get_logs]."""

    def test_unknown_instance(self) -> None:
        assert plugins.get_logs("does-not-exist") == []
