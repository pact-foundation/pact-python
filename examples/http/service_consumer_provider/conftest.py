"""
Shared PyTest configuration for the service-as-consumer/provider example.
"""

from __future__ import annotations

import contextlib
from pathlib import Path

import pytest

import pact_ffi

EXAMPLE_DIR = Path(__file__).parent.resolve()


@pytest.fixture(scope="session")
def pacts_path() -> Path:
    """
    Fixture for the Pact directory.

    Returns:
        Path to the directory where Pact contract files are written.
    """
    return EXAMPLE_DIR / "pacts"


@pytest.fixture(scope="session", autouse=True)
def _setup_pact_logging() -> None:
    """
    Set up logging for the pact package.
    """
    # If the logger is already configured (e.g., when running alongside other
    # examples), log_to_stderr raises RuntimeError. We suppress it here so
    # that the first configuration wins.
    with contextlib.suppress(RuntimeError):
        pact_ffi.log_to_stderr("INFO")
