"""
PyTest configuration file for the v3 API tests.

This file is loaded automatically by PyTest when running the tests in this
directory.
"""

import pytest


@pytest.fixture(scope="session", autouse=True)
def _setup_pact_logging() -> None:
    """
    Set up logging for the pact package.
    """
    from pact.v3 import ffi

    ffi.log_to_stderr("INFO")
