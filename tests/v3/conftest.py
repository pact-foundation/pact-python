"""
PyTest configuration file for the v3 API tests.

This file is loaded automatically by PyTest when running the tests in this
directory.
"""

import pytest

from pact.v3 import ffi


@pytest.fixture(scope="session", autouse=True)
def _setup_pact_logging() -> None:
    """
    Set up logging for the pact package.
    """
    ffi.log_to_stderr("INFO")
