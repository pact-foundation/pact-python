"""
Python bindings for the Pact FFI.

This module provides a Python interface to the Pact FFI. It is a thin wrapper
around the C API, and is intended to be used by the Pact Python client library
to provide a Pythonic interface to Pact.

This module is not intended to be used directly by Pact users. Pact users
should use the Pact Python client library instead. No guarantees are made
about the stability of this module's API.
"""

from ._ffi import ffi, lib


def version() -> str:
    """Return the version of the Pact FFI library."""
    return ffi.string(lib.pactffi_version()).decode("utf-8")
