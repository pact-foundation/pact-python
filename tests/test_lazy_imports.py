"""
Tests for compatibility with PEP 810 lazy imports.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 15),
    reason="Lazy imports require Python 3.15",
)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        pytest.param("pact_ffi.ffi", "FFI", id="pact_ffi.ffi"),
        pytest.param("pact_ffi.lib", "Lib", id="pact_ffi.lib"),
        pytest.param("pact_ffi.__version__", "str", id="pact_ffi.__version__"),
        pytest.param("pact.__version__", "str", id="pact.__version__"),
        pytest.param("pact.match", "module", id="pact.match"),
        pytest.param("pact.generate", "module", id="pact.generate"),
        pytest.param("pact.xml", "module", id="pact.xml"),
    ],
)
def test_attribute_under_lazy_imports(expression: str, expected: str) -> None:
    # Reading `__version_tuple__` first loads the `__version__` submodule
    # before `__version__` itself is resolved, which is the order that once
    # replaced the attribute with the submodule.
    code = (
        "import pact, pact_ffi; "
        "pact.__version_tuple__; pact_ffi.__version_tuple__; "
        f"print(type({expression}).__name__)"
    )
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-X", "lazy_imports=all", "-c", code],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == expected


def test_ffi_call_under_lazy_imports() -> None:
    code = "import pact_ffi; print(pact_ffi.version())"
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-X", "lazy_imports=all", "-c", code],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip()
