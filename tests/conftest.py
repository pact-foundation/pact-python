"""
PyTest configuration file for the v3 API tests.

This file is loaded automatically by PyTest when running the tests in this
directory.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

import pact_ffi


@pytest.fixture(scope="session", autouse=True)
def _setup_pact_logging() -> None:
    """
    Set up logging for the pact package.
    """
    pact_ffi.log_to_stderr("INFO")


@pytest.fixture
def temp_assets(tmp_path: Path) -> Path:
    """
    Create a temporary directory with some minimal files for testing.

    The directory is populated with a few minimal files:

    - `test.py`: A minimal hello-world Python script.
    - `test.txt`: A minimal text file.
    - `test.json`: A minimal JSON file.
    - `test.png`: A minimal PNG image.
    """
    tmp_path = Path(tempfile.mkdtemp())
    with (tmp_path / "test.py").open("w") as f:
        f.write('print("Hello, world!")')
    with (tmp_path / "test.txt").open("w") as f:
        f.write("Hello, world!")
    with (tmp_path / "test.json").open("w") as f:
        json.dump({"hello": "world"}, f)
    with (tmp_path / "test.png").open("wb") as f:
        f.write(
            b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52"
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4"
            b"\x89\x00\x00\x00\x0a\x49\x44\x41\x54\x78\x9c\x63\x00\x01\x00\x00"
            b"\x05\x00\x01\x0d\x0a\x2d\xb4\x00\x00\x00\x00\x49\x45\x4e\x44\xae"
            b"\x42\x60\x82",
        )

    return tmp_path
