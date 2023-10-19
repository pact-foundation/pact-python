"""
Common fixtures for tests.
"""
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest


@pytest.fixture()
def temp_dir() -> Generator[Path, Any, None]:
    """
    Create a temporary directory.

    This fixture automatically handles cleanup of the temporary directory once
    the test has finished.

    The directory is populated with a few minimal files:

    - `test.py`: A minimal hello-world Python script.
    - `test.txt`: A minimal text file.
    - `test.json`: A minimal JSON file.
    - `test.png`: A minimal PNG image.
    """
    temp_dir = Path(tempfile.mkdtemp())
    with (temp_dir / "test.py").open("w") as f:
        f.write('print("Hello, world!")')
    with (temp_dir / "test.txt").open("w") as f:
        f.write("Hello, world!")
    with (temp_dir / "test.json").open("w") as f:
        json.dump({"hello": "world"}, f)
    with (temp_dir / "test.png").open("wb") as f:
        f.write(
            b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52"
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4"
            b"\x89\x00\x00\x00\x0a\x49\x44\x41\x54\x78\x9c\x63\x00\x01\x00\x00"
            b"\x05\x00\x01\x0d\x0a\x2d\xb4\x00\x00\x00\x00\x49\x45\x4e\x44\xae"
            b"\x42\x60\x82",
        )

    yield temp_dir
    shutil.rmtree(temp_dir)
