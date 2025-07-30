"""
PyTest configuration file for the v3 API tests.

This file is loaded automatically by PyTest when running the tests in this
directory.
"""

import pytest

import pact_ffi


@pytest.fixture(scope="session", autouse=True)
def _setup_pact_logging() -> None:
    """
    Set up logging for the pact package.
    """
    pact_ffi.log_to_stderr("INFO")
