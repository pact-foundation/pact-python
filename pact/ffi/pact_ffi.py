"""Wrapper to pact reference dynamic libraries using FFI."""
import os
import tempfile
from typing import List

from cffi import FFI
import threading

from pact.ffi.log import LogToBufferStatus, LogLevel
from pact.ffi.register_ffi import RegisterFfi


class PactFFI(object):
    """This interfaces with the Rust crate `pact_ffi`.

    Interface with the pact_ffi API via a C Foreign Function Interface. In the case of python, the library
    is then accessed using `CFFI`.

    This class will implement the shared library loading, along with a wrapper
    for the functions provided by the base crate. For each of the Rust modules
    exposed, a corresponding python class will extend this base class, and
    provide the wrapper for the functions the module provides.

    .. _pact_ffi:
        https://docs.rs/pact_ffi/0.0.1/pact_ffi/index.html
    .. _CFFI:
        https://cffi.readthedocs.io/en/latest/
    """

    ffi: FFI = None
    lib = None

    _instance = None
    _lock = threading.Lock()

    # Required if outputting logs to a file, can be remove if using a buffer
    output_dir: tempfile.TemporaryDirectory = None
    output_file: str = None

    def __new__(cls):
        """Initiate the ffi."""
        # Make sure we only initialise once, or the log setup will fail
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(PactFFI, cls).__new__(cls)
                cls.ffi = FFI()

                # # Define all the functions from the various modules, since we
                # # can only load the library once
                # cls.lib = RegisterFfi().get_ffi_lib(cls.ffi)
                cls.lib = cls._load_ffi_library(cls.ffi)

                # We can setup logs like this, if preferred to buffer:
                # The output will be stored in a file in this directory, which
                # will be cleaned up automatically at the end
                PactFFI.output_dir = tempfile.TemporaryDirectory()
                # Setup logging to a file in the output_dir
                # PactFFI.output_file = os.path.join(PactFFI.output_dir.name, "output")
                # output_c = cls.ffi.new("char[]", bytes(cls.output_file, "utf-8"))
                # result = cls.lib.pactffi_log_to_file(output_c, LogLevel.INFO.value)
                # assert LogToBufferStatus(result) == LogToBufferStatus.SUCCESS

                # Having problems with the buffer output, when running via CLI
                # Reverting to log file output instead
                result = cls.lib.pactffi_log_to_buffer(LogLevel.INFO.value)
                assert LogToBufferStatus(result) == LogToBufferStatus.SUCCESS
        return cls._instance

    def version(self) -> str:
        """Get the current library version.

        :return: pact_ffi library version, for example "0.0.1"
        """
        result = self.lib.pactffi_version()
        return self.ffi.string(result).decode("utf-8")

    @staticmethod
    def _load_ffi_library(ffi):
        return RegisterFfi().get_ffi_lib(ffi)

    def get_logs(self) -> List[str]:
        """Retrieve the contents of the FFI log buffer.

        :return: List of log entries, each a line of log output
        """
        # Having problems with the buffer output, when running via CLI
        # Reverting to log file output instead
        result = self.lib.pactffi_fetch_log_buffer(b'NULL')
        logs = self.ffi.string(result).decode("utf-8").rstrip().split("\n")
        print(f"{logs=}")
        self.lib.pactffi_string_delete(result)
        return logs

        # # If using log to file, retrieve like this:
        # lines = open(PactFFI.output_file).readlines()
        # open(PactFFI.output_file, "w").close()
        # return [line.lstrip("\x00") for line in lines]
