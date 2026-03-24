"""
Shared pytest configuration for the XML example.

Defines the `pacts_path` fixture used by both consumer and provider tests to
locate the directory where generated Pact contract files are stored.
"""

from __future__ import annotations

import contextlib
from pathlib import Path

import pytest

import pact_ffi

EXAMPLE_DIR = Path(__file__).parent.resolve()


@pytest.fixture(scope="session")
def pacts_path() -> Path:
    """Fixture providing the path to the generated Pact contract files."""
    return EXAMPLE_DIR / "pacts"


@pytest.fixture(scope="session", autouse=True)
def _setup_pact_logging() -> None:
    """
    Set up logging for the pact package.
    """
    # If the logger is already configured, this will raise a RuntimeError.
    with contextlib.suppress(RuntimeError):
        pact_ffi.log_to_stderr("INFO")
