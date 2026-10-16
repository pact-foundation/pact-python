"""
Shared pytest configuration for the XML example.

Defines the `pacts_path` fixture used by both consumer and provider tests to
locate the directory where generated Pact contract files are stored.
"""

from __future__ import annotations

from pathlib import Path

import pytest

EXAMPLE_DIR = Path(__file__).parent.resolve()


@pytest.fixture(scope="session")
def pacts_path() -> Path:
    """Fixture providing the path to the generated Pact contract files."""
    return EXAMPLE_DIR / "pacts"
