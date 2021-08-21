"""Wrapper to pact reference dynamic libraries using FFI."""
import os
import tempfile
from enum import Enum, unique
from typing import NamedTuple, List

from cffi import FFI

from pact.ffi.pact_ffi import PactFFI


@unique
class VerifyStatus(Enum):
    SUCCESS = 0  # Operation succeeded
    VERIFIER_FAILED = 1  # The verification process failed, see output for errors
    NULL_POINTER = 2  # A null pointer was received
    PANIC = 3  # The method panicked
    INVALID_ARGS = 4  # Invalid arguments were provided to the verification process


@unique
class LogToBufferStatus(Enum):
    SUCCESS = 0  # Operation succeeded
    CANT_SET_LOGGER = -1  # Can't set the logger
    NO_LOGGER = -2  # No logger has been initialized
    SPECIFIER_NOT_UTF8 = -3  # The sink specifier was not UTF-8 encoded
    UNKNOWN_SINK_TYPE = -4  # The sink type specified is not a known type
    MISSING_FILE_PATH = -5  # No file path was specified in the sink specification
    CANT_OPEN_SINK_TO_FILE = -6  # Opening a sink to the given file failed
    CANT_CONSTRUCT_SINK = -7  # Can't construct sink


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
        ffi = FFI()
        ffi.cdef(
            """
        int pactffi_verify(char *);
        int pactffi_log_to_file(char *);
        """
        )
        lib = self._load_ffi_library(ffi)

        if args:
            c_args = ffi.new('char[]', bytes(args, 'utf-8'))
        else:
            c_args = ffi.NULL

        # This fails if called a second time after the library has been loaded
        # ..but still seems to work
        # result = lib.pactffi_log_to_buffer()
        # assert LogToBufferStatus(result) == LogToBufferStatus.SUCCESS
        # Additionally, when reading from the buffer it seems to come back empty
        # when running normally. Storing to a temporary file, at least for now.
        with tempfile.TemporaryDirectory() as td:
            output = os.path.join(td, 'output')
            output_c = ffi.new('char[]', bytes(output, 'utf-8'))
            lib.pactffi_log_to_file(output_c)

            result = lib.pactffi_verify(c_args)

            lines = open(output).readlines()

        return VerifyResult(result, lines)
