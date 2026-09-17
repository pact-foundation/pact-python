"""
Tests for [`PactTestMixin`][pact.testing.unittest.PactTestMixin].
"""

from __future__ import annotations

import contextlib
import logging
import unittest
from typing import TYPE_CHECKING

import pytest

import pact.logging
from pact.testing.unittest import PactTestMixin

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def run_ids(monkeypatch: pytest.MonkeyPatch) -> list[str | None]:
    calls: list[str | None] = []
    monkeypatch.setattr(pact.logging, "set_test_run_id", calls.append)
    return calls


class Example(PactTestMixin, unittest.TestCase):
    """`unittest.TestCase` exercising `PactTestMixin` for the tests below."""

    # Keep pytest from collecting the deliberately failing cases.
    __test__ = False

    def test_passes(self) -> None:
        logging.getLogger("pact.ffi.x").info("quiet")

    def test_fails(self) -> None:
        logging.getLogger("pact.ffi.x").info("noisy")
        self.fail("boom")

    def test_errors(self) -> None:
        logging.getLogger("pact.plugins").warning("plugin noise")
        raise RuntimeError

    def test_subtest_fails(self) -> None:
        logging.getLogger("pact.ffi.x").info("subtest noise")
        with self.subTest(case=1):
            self.fail("boom")


def run(name: str) -> unittest.TestResult:
    result = unittest.TestResult()
    Example(name).run(result)
    return result


def test_sets_and_clears_run_id(run_ids: list[str | None]) -> None:
    run("test_passes")
    assert run_ids == [f"{Example.__module__}.Example.test_passes", None]


def test_silent_on_success(capsys: pytest.CaptureFixture[str]) -> None:
    result = run("test_passes")
    assert result.wasSuccessful()
    assert capsys.readouterr().err == ""


def test_dumps_logs_on_failure(capsys: pytest.CaptureFixture[str]) -> None:
    result = run("test_fails")
    assert len(result.failures) == 1
    output = capsys.readouterr().err
    assert "--- Pact logs for" in output
    assert "test_fails" in output
    assert "noisy" in output


def test_dumps_logs_on_error(capsys: pytest.CaptureFixture[str]) -> None:
    result = run("test_errors")
    assert len(result.errors) == 1
    assert "plugin noise" in capsys.readouterr().err


def test_dumps_logs_on_subtest_failure(capsys: pytest.CaptureFixture[str]) -> None:
    result = run("test_subtest_fails")
    assert len(result.failures) == 1
    assert "subtest noise" in capsys.readouterr().err


def test_runs_under_pytest(pytester: pytest.Pytester) -> None:
    # Pytest passes its own result object to `run`, which has no `failures`
    # or `errors` lists.
    pytester.makepyfile(
        test_example="""
        import logging
        import unittest

        from pact.testing.unittest import PactTestMixin


        class Example(PactTestMixin, unittest.TestCase):
            def test_passes(self):
                pass

            def test_fails(self):
                logging.getLogger("pact.ffi.x").info("noisy")
                self.fail("boom")
        """
    )

    result = pytester.runpytest("-p", "no:cacheprovider")

    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines(["--- Pact logs for *test_fails ---", "*noisy"])


@contextlib.contextmanager
def quiet_root() -> Generator[None, None, None]:
    """
    Root logger at `WARNING` and the `pact` logger unset, as outside pytest.

    Pytest's `log_level = "NOTSET"` setting lowers the root logger at the
    start of each test phase, so this is entered inside the test body.
    """
    root = logging.getLogger()
    pact_logger = logging.getLogger("pact")
    root_level, pact_level = root.level, pact_logger.level
    root.setLevel(logging.WARNING)
    pact_logger.setLevel(logging.NOTSET)
    try:
        yield
    finally:
        root.setLevel(root_level)
        pact_logger.setLevel(pact_level)


def test_dumps_logs_below_root_level(capsys: pytest.CaptureFixture[str]) -> None:
    with quiet_root():
        assert not logging.getLogger("pact.ffi.x").isEnabledFor(logging.INFO)
        result = run("test_fails")
        assert logging.getLogger("pact").level == logging.NOTSET
    assert len(result.failures) == 1
    assert "noisy" in capsys.readouterr().err


class _ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_root_handlers_keep_their_level() -> None:
    # A handler on the root logger, as `logging.basicConfig()` installs, sees
    # only the records which reach it without the mixin.
    root_handler = _ListHandler()
    logging.getLogger().addHandler(root_handler)
    try:
        with quiet_root():
            run("test_passes")
            run("test_errors")
            assert logging.getLogger("pact").propagate
    finally:
        logging.getLogger().removeHandler(root_handler)
    assert [r.getMessage() for r in root_handler.records] == ["plugin noise"]


def test_keeps_explicit_pact_level() -> None:
    pact_logger = logging.getLogger("pact")
    pact_logger.setLevel(logging.ERROR)
    try:
        run("test_fails")
        assert pact_logger.level == logging.ERROR
    finally:
        pact_logger.setLevel(logging.NOTSET)


def test_handler_is_removed() -> None:
    before = list(logging.getLogger("pact").handlers)
    run("test_fails")
    assert logging.getLogger("pact").handlers == before


def test_run_without_result(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []

    class Recording(unittest.TestResult):
        def startTestRun(self) -> None:  # noqa: N802
            calls.append("start")

        def stopTestRun(self) -> None:  # noqa: N802
            calls.append("stop")

    monkeypatch.setattr(Example, "defaultTestResult", lambda _self: Recording())
    result = Example("test_fails").run()
    assert isinstance(result, Recording)
    assert len(result.failures) == 1
    assert calls == ["start", "stop"]
    assert "noisy" in capsys.readouterr().err
