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
        pytest.param("yarl", id="yarl"),
    ],
)
def test_import_does_not_load(module: str) -> None:
    """
    Check that `import pact` defers modules only some code paths need.

    A fresh interpreter is used, as the test session has already imported
    most modules.
    """
    code = f"import sys, pact; print({module!r} in sys.modules)"
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "False", f"`import pact` loaded {module}"


def test_state_handler_url_alias() -> None:
    from pact.types import StateHandlerUrl  # noqa: PLC0415

    assert StateHandlerUrl is str
