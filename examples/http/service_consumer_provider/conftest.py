"""
Shared PyTest configuration for the service-as-consumer/provider example.
"""

from __future__ import annotations

from pathlib import Path

import pact_ffi
import pytest

EXAMPLE_DIR = Path(__file__).parent.resolve()


@pytest.fixture(scope="session")
def pacts_path() -> Path:
    """
    Fixture for the Pact directory.
    """
    return EXAMPLE_DIR / "pacts"


@pytest.fixture(scope="session", autouse=True)
def _setup_pact_logging() -> None:
    """
    Set up logging for the pact package.
    """
    pact_ffi.log_to_stderr("INFO")
