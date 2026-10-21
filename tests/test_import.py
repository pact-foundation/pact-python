"""
Tests for the import-time footprint of `pact`.
"""

from __future__ import annotations

import importlib
import subprocess
import sys

import pytest

import pact


@pytest.mark.parametrize(
    "module",
    [
        pytest.param("http.server", id="http.server"),
        pytest.param("pact._server", id="pact._server"),
        pytest.param("pact_ffi", id="pact_ffi"),
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


@pytest.mark.parametrize(
    ("name", "module", "attribute"),
    [
        pytest.param("Pact", "pact.pact", "Pact", id="Pact"),
        pytest.param("Verifier", "pact.verifier", "Verifier", id="Verifier"),
        pytest.param("logging", "pact.logging", None, id="logging"),
        pytest.param("testing", "pact.testing", None, id="testing"),
    ],
)
def test_lazy_attribute(name: str, module: str, attribute: str | None) -> None:
    imported = importlib.import_module(module)
    expected = imported if attribute is None else getattr(imported, attribute)
    assert getattr(pact, name) is expected
    assert vars(pact)[name] is expected


def test_unknown_attribute() -> None:
    with pytest.raises(AttributeError, match="has no attribute 'missing'"):
        _ = pact.missing


def test_dir_lists_lazy_attributes() -> None:
    # A fresh interpreter, so that no lazy attribute has been imported yet.
    code = "import pact; print(' '.join(dir(pact)))"
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
    )
    assert {"Pact", "Verifier", "logging", "testing"} <= set(result.stdout.split())


def test_state_handler_url_alias() -> None:
    from pact.types import StateHandlerUrl  # noqa: PLC0415

    assert StateHandlerUrl is str
