"""
Shared PyTest configuration for the service-as-consumer/provider example.
"""

from __future__ import annotations

from pathlib import Path

import pytest

EXAMPLE_DIR = Path(__file__).parent.resolve()


@pytest.fixture(scope="session")
def pacts_path() -> Path:
    """
    Fixture for the Pact directory.

    Returns:
        Path to the directory where Pact contract files are written.
    """
    return EXAMPLE_DIR / "pacts"
