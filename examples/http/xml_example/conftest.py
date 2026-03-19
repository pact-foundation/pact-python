from __future__ import annotations

from pathlib import Path

import pytest


EXAMPLE_DIR = Path(__file__).parent.resolve()


@pytest.fixture(scope="session")
def pacts_path() -> Path:
    return EXAMPLE_DIR / "pacts"
