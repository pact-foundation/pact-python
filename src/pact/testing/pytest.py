"""
Pytest plugin scoping the Pact test run ID to each test.

The plugin is registered through the `pytest11` entry point and is active
whenever `pact-python` is installed. It provides one autouse fixture,
[`pact_test_run_id`][pact.testing.pytest.pact_test_run_id], which sets the
test's node ID as the Pact test run ID for the test's duration. The Pact
library's records from the test's thread, and the log entries a plugin sends
back for the test's requests, then carry the test which caused them.

Disable the plugin with `-p no:pact`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator


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
    # Imported here so that collecting the plugin does not load the FFI shared
    # library in every environment where pact-python is installed.
    from pact import logging as pact_logging  # noqa: PLC0415

    pact_logging.set_test_run_id(request.node.nodeid)
    yield request.node.nodeid
    pact_logging.set_test_run_id(None)
