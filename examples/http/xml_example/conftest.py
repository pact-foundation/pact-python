"""
Pytest fixture (placeholder, will be completed).
"""

from __future__ import annotations

from pathlib import Path

import pytest

EXAMPLE_DIR = Path(__file__).parent.resolve()


@pytest.fixture(scope="session")
def pacts_path() -> Path:
    """Setup the path for generated pact files."""
    return EXAMPLE_DIR / "pacts"
