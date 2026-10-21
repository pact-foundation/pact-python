"""
`unittest` integration for Pact logs.

[`PactTestMixin`][testing.unittest.PactTestMixin] scopes the Pact test run
ID to each test and prints the Pact log records collected during a test to
stderr when the test fails or errors:

```python
import unittest

from pact.testing.unittest import PactTestMixin


class ConsumerTest(PactTestMixin, unittest.TestCase):
    def test_something(self) -> None: ...
```

List the mixin before `unittest.TestCase` so that its `run` wraps the test.
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING, Any

from pact import logging as pact_logging

if TYPE_CHECKING:
    import unittest

__all__ = ["PactTestMixin"]


class _BufferHandler(logging.Handler):
    """
    Handler buffering every record, and forwarding some to a parent logger.

    While [`PactTestMixin`][testing.unittest.PactTestMixin] lowers the `pact`
    logger, it stops the logger propagating. This handler stands in for
    propagation, handing the parent's handlers only the records which would
    have reached them at the logger's previous level.
    """

    def __init__(self, parent: logging.Logger | None, threshold: int) -> None:
        super().__init__(logging.NOTSET)
        self.records: list[logging.LogRecord] = []
        self._parent = parent
        self._threshold = threshold

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)
        if self._parent is not None and record.levelno >= self._threshold:
            self._parent.callHandlers(record)


class _ResultProxy:
    """
    Wrapper around a test result noting whether the test failed or errored.

    Every attribute is looked up on the wrapped result. Pytest passes its own
    result object to `run`, which lacks the `failures` and `errors` lists of
    `unittest.TestResult`.
    """

    _FAILING = frozenset({"addError", "addFailure", "addSubTest"})

    def __init__(self, result: object) -> None:
        self._result = result
        self.failed = False

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        attribute = getattr(self._result, name)
        if name not in self._FAILING:
            return attribute

        def record(*args: Any) -> Any:  # noqa: ANN401
            # `addSubTest` is called with `err=None` for a passing subtest.
            if name != "addSubTest" or args[-1] is not None:
                self.failed = True
            return attribute(*args)

        return record


def _enclosing_test_run_id() -> str | None:
    # Looked up, never imported: `unittest` suites need not have pytest
    # installed.
    pytest_plugin = sys.modules.get("pact.testing.pytest")
    if pytest_plugin is None:
        return None
    return pytest_plugin.current_test_run_id()


class PactTestMixin:
    """
    Mixin for `unittest.TestCase` subclasses using Pact.

    While a test runs, its `id()` is set as the Pact test run ID and every
    record on the `pact` logger is buffered. If the test fails or errors, the
    buffered records are written to stderr under a banner naming the test.
    Afterwards, the run ID is cleared or, when pytest runs the test case, set
    back to the test's node ID.

    A logger only hands records at or above its effective level to its
    handlers, so when the `pact` logger has no explicit level it is lowered to
    [`forwarding_level`][pact_logging.forwarding_level] for the duration of the
    test and restored afterwards. Handlers above the `pact` logger still
    receive only the records at or above its previous effective level.
    Handlers attached to the `pact` logger or below it receive every buffered
    record.
    """

    def run(
        self,
        result: unittest.TestResult | None = None,
    ) -> unittest.TestResult | None:
        """
        Run the test with the Pact run ID set and Pact logs buffered.

        Args:
            result:
                The result to record into. When omitted, the test's
                `defaultTestResult()` is used, and its `startTestRun()` and
                `stopTestRun()` are called around the test, as
                `unittest.TestCase.run` does.

        Returns:
            The result the test was recorded into.
        """
        owns_result = result is None
        if result is None:
            result = self.defaultTestResult()  # type: ignore[attr-defined]
            result.startTestRun()
        test_id: str = self.id()  # type: ignore[attr-defined]
        proxy = _ResultProxy(result)

        pact_logger = logging.getLogger("pact")
        lowered = pact_logger.level == logging.NOTSET
        propagate = pact_logger.propagate
        handler = _BufferHandler(
            pact_logger.parent if lowered and propagate else None,
            pact_logger.getEffectiveLevel(),
        )

        pact_logging.set_test_run_id(test_id)
        pact_logger.addHandler(handler)
        if lowered:
            pact_logger.setLevel(pact_logging.forwarding_level())
            pact_logger.propagate = False
        try:
            super().run(proxy)  # type: ignore[misc]
            if proxy.failed:
                self._dump(test_id, handler.records)
            return result
        finally:
            if lowered:
                pact_logger.setLevel(logging.NOTSET)
                pact_logger.propagate = propagate
            pact_logger.removeHandler(handler)
            pact_logging.set_test_run_id(_enclosing_test_run_id())
            if owns_result:
                result.stopTestRun()

    @staticmethod
    def _dump(test_id: str, records: list[logging.LogRecord]) -> None:
        formatter = logging.Formatter("%(levelname)s %(name)s: %(message)s")
        lines = [f"--- Pact logs for {test_id} ---"]
        lines.extend(formatter.format(record) for record in records)
        lines.append("--- end of Pact logs ---")
        sys.stderr.write("\n".join(lines) + "\n")
