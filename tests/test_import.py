"""
Tests for the import-time footprint of `pact`.
"""

from __future__ import annotations

import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    "module",
    [
        pytest.param("http.server", id="http.server"),
        pytest.param("pact._server", id="pact._server"),
    ],
)
def test_import_does_not_load(module: str) -> None:
    """
    Check that `import pact` defers modules only some code paths need.

    A fresh interpreter is used, as the test session has already imported
    most modules.
    """
    code = f"import sys, pact; sys.exit({module!r} in sys.modules)"
    result = subprocess.run([sys.executable, "-c", code], check=False)  # noqa: S603
    assert result.returncode == 0, f"`import pact` loaded {module}"
