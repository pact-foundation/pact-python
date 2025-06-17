"""
Common Pytest configuration for the V3 examples.
"""

import pytest

from pact.v3 import ffi


@pytest.fixture(scope="session", autouse=True)
def _setup_pact_logging() -> None:
    """
    Set up logging for the pact package.
    """
    ffi.log_to_stderr("INFO")
