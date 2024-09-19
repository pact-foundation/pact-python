"""
Common Pytest configuration for the V3 examples.
"""

import pytest


@pytest.fixture(scope="session", autouse=True)
def _setup_pact_logging() -> None:
    """
    Set up logging for the pact package.
    """
    from pact.v3 import ffi

    ffi.log_to_stderr("INFO")
