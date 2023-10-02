"""
Tests of the FFI module.

These tests are intended to ensure that the FFI module is working correctly.
They are not intended to test the Pact API itself, as that is handled by the
client library.
"""

from pact.v3 import ffi


def test_version() -> None:
    assert isinstance(ffi.version(), str)
    assert len(ffi.version()) > 0
    assert ffi.version().count(".") == 2
