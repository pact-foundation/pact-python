"""
Pytest plugin scoping the Pact test run ID to each test.

The plugin is registered through the `pytest11` entry point and is active
whenever `pact-python` is installed. It provides one autouse fixture,
[`pact_test_run_id`][testing.pytest.pact_test_run_id], which sets the
test's node ID as the Pact test run ID for the test's duration. The Pact
library's records from the test's thread, and the log entries a plugin sends
back for the test's requests, then carry the test which caused them.

The plugin does not load the Pact FFI. While no module has imported Pact
Python's logging integration, the run ID is held in Python, and applied once
the integration is imported.

Disable the plugin with `-p no:pact`.
"""

from __future__ import annotations

import sys
import threading
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

_state = threading.local()


def current_test_run_id() -> str | None:
    """
    Run ID of the test running on the current thread.

    Returns:
        The node ID set by [`pact_test_run_id`][testing.pytest.pact_test_run_id],
        or `None` outside a test.
    """
    return getattr(_state, "test_run_id", None)


def _set_test_run_id(test_run_id: str | None) -> None:
    _state.test_run_id = test_run_id
    # Looked up, never imported: importing it would load the FFI in sessions
    # which never use Pact.
    pact_logging = sys.modules.get("pact.logging")
    if pact_logging is not None:
        pact_logging.set_test_run_id(test_run_id)


@pytest.fixture(autouse=True)
def pact_test_run_id(request: pytest.FixtureRequest) -> Generator[str, None, None]:
    """
    Set the test's node ID as the Pact test run ID.

    Args:
        request:
            The pytest request for the running test.

    Yields:
        The node ID set as the run ID. It is cleared on teardown.
    """
    _set_test_run_id(request.node.nodeid)
    yield request.node.nodeid
    _set_test_run_id(None)
