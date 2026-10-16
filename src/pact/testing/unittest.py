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
import unittest

from pact import logging as pact_logging

__all__ = ["PactTestMixin"]


class _ListHandler(logging.Handler):
    """Handler appending every record to a list."""

    def __init__(self) -> None:
        super().__init__(logging.NOTSET)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class PactTestMixin:
    """
    Mixin for `unittest.TestCase` subclasses using Pact.

    While a test runs, its `id()` is set as the Pact test run ID and every
    record on the `pact` logger is buffered. If the test fails or errors, the
    buffered records are written to stderr under a banner naming the test.

    A logger only hands records at or above its effective level to its
    handlers, so when the `pact` logger has no explicit level it is lowered to
    [`forwarding_level`][pact_logging.forwarding_level] for the duration of the
    test and restored afterwards.
    """

    def run(
        self,
        result: unittest.TestResult | None = None,
    ) -> unittest.TestResult | None:
        """
        Run the test with the Pact run ID set and Pact logs buffered.

        Args:
            result:
                The result to record into. When omitted, a new
                `unittest.TestResult` is created, as `unittest.TestCase.run`
                does.

        Returns:
            The result returned by `unittest.TestCase.run`.
        """
        if result is None:
            result = unittest.TestResult()
        test_id: str = self.id()  # type: ignore[attr-defined]

        handler = _ListHandler()
        pact_logger = logging.getLogger("pact")
        failures = len(result.failures) + len(result.errors)

        pact_logging.set_test_run_id(test_id)
        pact_logger.addHandler(handler)
        lowered = pact_logger.level == logging.NOTSET
        if lowered:
            pact_logger.setLevel(pact_logging.forwarding_level())
        try:
            outcome = super().run(result)  # type: ignore[misc]
            if len(result.failures) + len(result.errors) > failures:
                self._dump(test_id, handler.records)
            return outcome
        finally:
            if lowered:
                pact_logger.setLevel(logging.NOTSET)
            pact_logger.removeHandler(handler)
            pact_logging.set_test_run_id(None)

    @staticmethod
    def _dump(test_id: str, records: list[logging.LogRecord]) -> None:
        formatter = logging.Formatter("%(levelname)s %(name)s: %(message)s")
        lines = [f"--- Pact logs for {test_id} ---"]
        lines.extend(formatter.format(record) for record in records)
        lines.append("--- end of Pact logs ---")
        sys.stderr.write("\n".join(lines) + "\n")
