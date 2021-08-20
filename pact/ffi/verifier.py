"""Wrapper to pact reference dynamic libraries using FFI."""
from enum import Enum, unique
from typing import NamedTuple

from cffi import FFI

from pact.ffi.pact_ffi import PactFFI


@unique
class VerifyStatus(Enum):
    """Errors are returned as non-zero numeric values.

    1. The verification process failed, see output for errors
    2. A null pointer was received
    3. The method panicked
    4. Invalid arguments were provided to the verification process"""

    OK = 0
    ERR_VERIFIER_FAILED = 1
    ERR_NULL_POINTER = 2
    ERR_PANIC = 3
    ERR_INVALID_ARGS = 4


class VerifyResult(NamedTuple):
    return_code: VerifyStatus
    logs: str


class Verifier(PactFFI):
    """A Pact Verifier Wrapper.

    This interfaces with the Rust FFI crate pact_ffi, specifically the
    `verifier`_ module.

    .. _verifier:
        https://docs.rs/pact_ffi/0.0.1/pact_ffi/verifier/index.html
    """

    def verify(self, args=None) -> VerifyResult:
        """Call verify method."""
        ffi = FFI()
        ffi.cdef(
            """
        int pactffi_verify(char *);
        """
        )
        lib = self._load_ffi_library(ffi)

        if args:
            c_args = ffi.new('char[]', bytes(args, 'utf-8'))
        else:
            c_args = ffi.NULL

        result = lib.pactffi_verify(c_args)
        return VerifyResult(result, "todo")
