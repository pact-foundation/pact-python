"""Wrapper to pact reference dynamic libraries using FFI."""
from enum import Enum, unique
from typing import NamedTuple, List

from pact.ffi.pact_ffi import PactFFI


@unique
class VerifyStatus(Enum):
    SUCCESS = 0  # Operation succeeded
    VERIFIER_FAILED = 1  # The verification process failed, see output for errors
    NULL_POINTER = 2  # A null pointer was received
    PANIC = 3  # The method panicked
    INVALID_ARGS = 4  # Invalid arguments were provided to the verification process


class VerifyResult(NamedTuple):
    return_code: VerifyStatus
    logs: List[str]


class Verifier(PactFFI):
    """A Pact Verifier Wrapper.

    This interfaces with the Rust FFI crate pact_ffi, specifically the
    `verifier`_ module.

    .. _verifier:
        https://docs.rs/pact_ffi/0.0.1/pact_ffi/verifier/index.html
    """

    def verify(self, args=None) -> VerifyResult:
        """Call verify method."""

        if args:
            c_args = self.ffi.new('char[]', bytes(args, 'utf-8'))
        else:
            c_args = self.ffi.NULL

        # This fails if called a second time after the library has been loaded
        # ..but still seems to work
        # result = lib.pactffi_log_to_buffer()
        # assert LogToBufferStatus(result) == LogToBufferStatus.SUCCESS
        # Additionally, when reading from the buffer it seems to come back empty
        # when running normally. Storing to a temporary file, at least for now.
        # with tempfile.TemporaryDirectory() as td:
        #     output = os.path.join(td, 'output')
        #     output_c = ffi.new('char[]', bytes(output, 'utf-8'))
        #     result = lib.pactffi_log_to_file(output_c)
        #     x = 1
        #     result = lib.pactffi_verify(c_args)
        #
        #     lines = open(output).readlines()

        result = self.lib.pactffi_verify(c_args)
        logs = self._get_logs()
        return VerifyResult(result, logs)
