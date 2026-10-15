"""
Unit tests for [`pact.logging`][pact.logging].
"""

from __future__ import annotations

import atexit
import logging
import subprocess
import sys
import textwrap
from typing import TYPE_CHECKING

import aiohttp
import pytest

import pact_ffi
from pact import Pact
from pact import logging as pact_logging

if TYPE_CHECKING:
    from collections.abc import Generator


def emit_core(
    log_id: str = "",
    test_run_id: str = "",
    level: str = "INFO",
    target: str = "pact_matching",
    message: str = "hello",
) -> None:
    """Invoke the core log callback registered with the FFI as the library would."""
    callback = pact_ffi._log_callback  # noqa: SLF001
    assert callback is not None
    callback(
        *(s.encode("utf-8") for s in (log_id, test_run_id, level, target, message))
    )


def emit_plugin(
    plugin_instance_id: str = "instance",
    test_run_id: str = "",
    level: str = "INFO",
    target: str = "",
    message: str = "hello",
) -> None:
    """Invoke the plugin log callback registered with the FFI as the library would."""
    callback = pact_ffi._plugin_log_callback  # noqa: SLF001
    assert callback is not None
    callback(
        *(
            s.encode("utf-8")
            for s in (plugin_instance_id, test_run_id, level, target, message)
        )
    )


@pytest.fixture
def uninitialised(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """
    Reset the initialisation flag and stub the FFI calls, recording their names.

    The FFI logger can be applied once per process, so the initialisation path
    is exercised against stubs.
    """
    calls: list[str] = []
    monkeypatch.setattr(pact_logging, "_initialised", False)
    monkeypatch.setattr(pact_logging, "_level_warned", False)
    monkeypatch.setattr(pact_logging, "_applied_level", logging.CRITICAL)
    monkeypatch.setattr(atexit, "register", lambda *_a, **_k: None)
    for name in (
        "set_log_callback_level",
        "log_to_buffer",
        "register_log_callback",
        "register_plugin_log_callback",
    ):
        monkeypatch.setattr(pact_ffi, name, lambda *_a, _n=name, **_k: calls.append(_n))
    return calls


class TestLevels:
    """Tests for the level mappings."""

    def test_trace_is_registered(self) -> None:
        assert logging.getLevelName(pact_logging.TRACE) == "TRACE"

    @pytest.mark.parametrize(
        ("level", "expected"),
        [
            pytest.param(pact_logging.TRACE, pact_ffi.LevelFilter.TRACE, id="trace"),
            pytest.param(logging.DEBUG, pact_ffi.LevelFilter.DEBUG, id="debug"),
            pytest.param(logging.INFO, pact_ffi.LevelFilter.INFO, id="info"),
            pytest.param(logging.WARNING, pact_ffi.LevelFilter.WARN, id="warning"),
            pytest.param(logging.ERROR, pact_ffi.LevelFilter.ERROR, id="error"),
            pytest.param(logging.CRITICAL, pact_ffi.LevelFilter.ERROR, id="critical"),
            pytest.param(15, pact_ffi.LevelFilter.DEBUG, id="between-debug-and-info"),
        ],
    )
    def test_to_ffi_level(self, level: int, expected: pact_ffi.LevelFilter) -> None:
        assert pact_logging.to_ffi_level(level) == expected

    @pytest.mark.parametrize(
        ("level", "expected"),
        [
            pytest.param("TRACE", pact_logging.TRACE, id="trace"),
            pytest.param("DEBUG", logging.DEBUG, id="debug"),
            pytest.param("INFO", logging.INFO, id="info"),
            pytest.param("WARN", logging.WARNING, id="warn"),
            pytest.param("ERROR", logging.ERROR, id="error"),
            pytest.param("warn", logging.WARNING, id="lowercase"),
            pytest.param("BOGUS", logging.INFO, id="unknown"),
        ],
    )
    def test_from_ffi_level(self, level: str, expected: int) -> None:
        assert pact_logging.from_ffi_level(level) == expected


class TestFfiLevel:
    """Tests for [`_ffi_level`][pact.logging._ffi_level]."""

    @pytest.fixture(autouse=True)
    def _reset_loggers(self) -> Generator[None, None, None]:
        yield
        logging.getLogger("pact.ffi").setLevel(logging.NOTSET)
        logging.getLogger("pact.plugins").setLevel(logging.NOTSET)

    def test_default_when_unset(self) -> None:
        assert pact_logging._ffi_level() == pact_logging.to_ffi_level(  # noqa: SLF001
            pact_logging.DEFAULT_LEVEL
        )

    def test_most_verbose_explicit_level_wins(self) -> None:
        logging.getLogger("pact.ffi").setLevel(logging.ERROR)
        logging.getLogger("pact.plugins").setLevel(pact_logging.TRACE)
        assert pact_logging._ffi_level() == pact_ffi.LevelFilter.TRACE  # noqa: SLF001

    def test_single_explicit_level(self) -> None:
        logging.getLogger("pact.ffi").setLevel(logging.ERROR)
        assert pact_logging._ffi_level() == pact_ffi.LevelFilter.ERROR  # noqa: SLF001


class TestEnsureInitialised:
    """Tests for [`ensure_initialised`][pact.logging.ensure_initialised]."""

    def test_applies_logger_and_registers_callbacks(
        self, uninitialised: list[str]
    ) -> None:
        pact_logging.ensure_initialised()
        assert uninitialised == [
            "set_log_callback_level",
            "log_to_buffer",
            "register_log_callback",
            "register_plugin_log_callback",
        ]

    @pytest.mark.parametrize(
        ("level", "expected"),
        [
            pytest.param(
                logging.NOTSET,
                pact_logging.to_ffi_level(pact_logging.DEFAULT_LEVEL),
                id="default",
            ),
            pytest.param(logging.DEBUG, pact_ffi.LevelFilter.DEBUG, id="debug"),
            pytest.param(pact_logging.TRACE, pact_ffi.LevelFilter.TRACE, id="trace"),
        ],
    )
    def test_applies_forwarding_level(
        self,
        uninitialised: list[str],
        monkeypatch: pytest.MonkeyPatch,
        level: int,
        expected: pact_ffi.LevelFilter,
    ) -> None:
        applied: list[object] = []
        monkeypatch.setattr(pact_ffi, "set_log_callback_level", applied.append)
        ffi_logger = logging.getLogger("pact.ffi")
        ffi_logger.setLevel(level)
        try:
            pact_logging.ensure_initialised()
        finally:
            ffi_logger.setLevel(logging.NOTSET)
        assert applied == [expected]
        assert "log_to_buffer" in uninitialised

    def test_registers_shutdown_hook(
        self, uninitialised: list[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        registered: list[object] = []
        monkeypatch.setattr(atexit, "register", registered.append)

        pact_logging.ensure_initialised()
        assert registered == [pact_logging._shutdown]  # noqa: SLF001

        del uninitialised[:]
        pact_logging._shutdown()  # noqa: SLF001
        assert uninitialised == [
            "set_log_callback_level",
            "register_log_callback",
            "register_plugin_log_callback",
        ]

    def test_shutdown_swallows_errors(
        self, uninitialised: list[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fail(*_a: object, **_k: object) -> None:
            raise RuntimeError

        monkeypatch.setattr(pact_ffi, "set_log_callback_level", fail)
        pact_logging._shutdown()  # noqa: SLF001
        assert uninitialised == [
            "register_log_callback",
            "register_plugin_log_callback",
        ]

    def test_is_idempotent(self, uninitialised: list[str]) -> None:
        pact_logging.ensure_initialised()
        pact_logging.ensure_initialised()
        assert len(uninitialised) == 4

    def test_warns_once_when_level_raised_later(
        self,
        uninitialised: list[str],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        pact_logging.ensure_initialised()
        with caplog.at_level(pact_logging.TRACE, logger="pact.ffi"):
            pact_logging.ensure_initialised()
            pact_logging.ensure_initialised()

        applied = pact_logging.to_ffi_level(pact_logging.DEFAULT_LEVEL)
        warnings = [r for r in caplog.records if r.name == "pact"]
        assert len(warnings) == 1
        assert f"forwarded at {applied.name}" in warnings[0].getMessage()
        assert len(uninitialised) == 4

    def test_silent_when_level_unchanged(
        self,
        uninitialised: list[str],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        pact_logging.ensure_initialised()
        with caplog.at_level(logging.WARNING, logger="pact.ffi"):
            pact_logging.ensure_initialised()
        assert not [r for r in caplog.records if r.name == "pact"]
        assert uninitialised

    def test_warns_when_logger_already_applied(
        self,
        uninitialised: list[str],
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        def fail(*_a: object, **_k: object) -> None:
            msg = "There was an unknown error setting the logger."
            raise RuntimeError(msg)

        monkeypatch.setattr(pact_ffi, "log_to_buffer", fail)
        with caplog.at_level(logging.WARNING, logger="pact"):
            pact_logging.ensure_initialised()

        assert [r.levelno for r in caplog.records] == [logging.WARNING]
        assert "configured externally" in caplog.records[0].getMessage()
        assert uninitialised[-2:] == [
            "register_log_callback",
            "register_plugin_log_callback",
        ]


class TestCallbacks:
    """Tests for the records emitted by the FFI callbacks."""

    @pytest.fixture(autouse=True)
    def _initialised(self) -> None:
        pact_logging.ensure_initialised()
        # ensure_initialised() is a no-op past the first call in the process,
        # so another test module may have since replaced the FFI callbacks
        # with its own (e.g. to assert on deregistration). Re-register the
        # module's own callbacks so these tests do not depend on suite order.
        pact_ffi.register_log_callback(pact_logging._core_callback)  # noqa: SLF001
        pact_ffi.register_plugin_log_callback(pact_logging._plugin_callback)  # noqa: SLF001

    def test_core_record(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(pact_logging.TRACE, logger="pact.ffi"):
            emit_core(
                log_id="server-1",
                test_run_id="run-1",
                level="WARN",
                target="pact_matching::matchers",
                message="careful",
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.name == "pact.ffi.pact_matching::matchers"
        assert record.levelno == logging.WARNING
        assert record.getMessage() == "careful"
        assert record.__dict__["test_run_id"] == "run-1"
        assert record.__dict__["log_id"] == "server-1"

    def test_core_empty_strings_become_none(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(pact_logging.TRACE, logger="pact.ffi"):
            emit_core(level="TRACE")

        record = caplog.records[0]
        assert record.levelno == pact_logging.TRACE
        assert record.__dict__["test_run_id"] is None
        assert record.__dict__["log_id"] is None

    def test_plugin_record(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.DEBUG, logger="pact.plugins"):
            emit_plugin("inst", "run-1", "ERROR", "plugin::mod", "boom")

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.name == "pact.plugins"
        assert record.levelno == logging.ERROR
        assert record.getMessage() == "boom"
        assert record.__dict__["plugin_instance_id"] == "inst"
        assert record.__dict__["test_run_id"] == "run-1"
        assert record.__dict__["plugin_target"] == "plugin::mod"

    def test_plugin_empty_strings_become_none(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.DEBUG, logger="pact.plugins"):
            emit_plugin(test_run_id="", target="")

        record = caplog.records[0]
        assert record.__dict__["test_run_id"] is None
        assert record.__dict__["plugin_target"] is None

    def test_handler_exceptions_do_not_propagate(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        The Python callbacks swallow handler errors.

        The callbacks are invoked directly: the CFFI handle already discards
        exceptions (printing a traceback to stderr), so driving it would not
        exercise the guard inside the callbacks.
        """

        def boom(*_a: object, **_k: object) -> None:
            raise RuntimeError

        monkeypatch.setattr(logging.getLogger("pact.ffi.x"), "log", boom)
        monkeypatch.setattr(logging.getLogger("pact.plugins"), "log", boom)
        pact_logging._core_callback("", "", "INFO", "x", "hello")  # noqa: SLF001
        pact_logging._plugin_callback("instance", "", "INFO", "", "hello")  # noqa: SLF001
        assert capsys.readouterr().err == ""


class TestFfiStandIns:
    """The `pact_ffi` functions which apply a logger, once `pact` is imported."""

    @pytest.mark.parametrize("name", pact_logging._REPLACED_FFI_FUNCTIONS)  # noqa: SLF001
    def test_warns_at_caller(self, name: str) -> None:
        with pytest.warns(UserWarning, match=rf"pact_ffi\.{name} has no effect") as w:
            result = getattr(pact_ffi, name)("INFO")

        assert result is None
        assert w[0].filename == __file__

    def test_does_not_apply_a_logger(self) -> None:
        # Applying a logger is permanent for the process, so the test runs in a
        # separate interpreter. The logger can be applied once, so the final
        # `log_to_buffer` only succeeds if the stand-ins applied nothing.
        script = textwrap.dedent(
            """
            import warnings

            import pact_ffi
            import pact

            warnings.simplefilter("ignore")
            pact_ffi.log_to_stderr("INFO")
            pact_ffi.init_with_log_level("INFO")
            pact_ffi.init("LOG_LEVEL")
            pact_ffi.log_to_buffer("OFF")
            """
        )
        subprocess.run(  # noqa: S603
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            text=True,
        )


class TestEndToEnd:
    """Records forwarded from the Pact library during a consumer test."""

    @pytest.mark.asyncio
    async def test_mock_server_records(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO, logger="pact.ffi")
        pact = Pact("consumer", "provider")
        (
            pact
            .upon_receiving("a request")
            .with_request("GET", "/")
            .will_respond_with(200)
        )
        with pact.serve() as srv:
            async with (
                aiohttp.ClientSession(srv.url) as session,
                session.get("/") as resp,
            ):
                assert resp.status == 200

        records = [r for r in caplog.records if r.name.startswith("pact.ffi.")]
        assert records
        assert any(r.__dict__.get("log_id") is not None for r in records)


class TestSetTestRunId:
    """Tests for [`set_test_run_id`][pact.logging.set_test_run_id]."""

    def test_set_and_clear(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list[str | None] = []
        monkeypatch.setattr(pact_ffi, "set_test_run_id", calls.append)
        pact_logging.set_test_run_id("tests/test_x.py::test_y")
        pact_logging.set_test_run_id(None)
        assert calls == ["tests/test_x.py::test_y", None]
