"""
Pytest configuration.

As the compatibility suite makes use of a submodule, we need to make sure the
submodule has been initialized before running the tests.
"""

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def _submodule_init() -> None:
    """Initialize the submodule."""
    # Locate the git execute
    submodule_dir = Path(__file__).parent / "definition"
    if submodule_dir.is_dir():
        return

    git_exec = shutil.which("git")
    if git_exec is None:
        msg = (
            "Submodule not initialized and git executable not found."
            " Please initialize the submodule with `git submodule init`."
        )
        raise RuntimeError(msg)
    subprocess.check_call([git_exec, "submodule", "init"])  # noqa: S603
