"""Wrapper to pact reference dynamic libraries using FFI."""
import os
import platform
import tempfile
from enum import unique, Enum
from typing import List

from cffi import FFI
import threading


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


@unique
class LogLevel(Enum):
    OFF = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5


class PactFFI(object):
    """This interfaces with the Rust crate `pact_ffi`_, which exposes the Pact
    API via a C Foreign Function Interface. In the case of python, the library
    is then accessed using `CFFI`_.

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
        # We want to make sure we only initialise once, or the log setup will fail
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(PactFFI, cls).__new__(cls)
                cls.ffi = FFI()

                # Define all the functions from the various modules, since we can
                # only load the library once
                cls.ffi.cdef(
                    """
                // root crate
                char *pactffi_version(void);
    
                // verifier
                int pactffi_verify(char *);
                
                // mock_server
                void pactffi_free_string(char *);
                
                // log
                int pactffi_log_to_file(char *, int);
                int pactffi_log_to_buffer(int);
                char * pactffi_fetch_log_buffer(void);
                
                // experimenting
                char *pactffi_verifier_cli_args(void);
                """
                )
                cls.lib = cls._load_ffi_library(cls.ffi)

                # We can setup logs like this, if preferred to buffer:
                # The output will be stored in a file in this directory, which will
                # be cleaned up automatically at the end
                PactFFI.output_dir = tempfile.TemporaryDirectory()
                # Setup logging to a file in the output_dir
                PactFFI.output_file = os.path.join(PactFFI.output_dir.name, "output")
                output_c = cls.ffi.new("char[]", bytes(cls.output_file, "utf-8"))
                result = cls.lib.pactffi_log_to_file(output_c, LogLevel.INFO.value)
                assert LogToBufferStatus(result) == LogToBufferStatus.SUCCESS

                # Having problems with the buffer output, when running via CLI
                # Reverting to log file output instead
                # result = cls.lib.pactffi_log_to_buffer(LogLevel.INFO.value)
                # assert LogToBufferStatus(result) == LogToBufferStatus.SUCCESS
        return cls._instance

    def version(self) -> str:
        """Get the current library version.

        :return: pact_ffi library version, for example "0.0.1"
        """
        result = self.lib.pactffi_version()
        return self.ffi.string(result).decode("utf-8")

    @staticmethod
    def _load_ffi_library(ffi):
        """Load the appropriate library for the current platform."""
        target_platform = platform.platform().lower()

        if target_platform in ["darwin", "macos"]:
            libname = "pact/bin/libpact_ffi-osx-x86_64.dylib"
        elif "linux" in target_platform:
            libname = "pact/bin/libpact_ffi-linux-x86_64.so"
        elif "windows" in target_platform:
            libname = "pact/bin/pact_ffi-windows-x86_64.dll"
        else:
            msg = (
                f"Unfortunately, {platform.platform()} is not a supported "
                f"platform. Only Linux, Windows, and OSX are currently "
                f"supported."
            )
            raise Exception(msg)

        # TODO: Hardcoding while messing, revert when done
        libname = "/home/mgeeves/dev/GitHub/pact-reference/rust/target/release/libpact_ffi.so"
        return ffi.dlopen(libname)

    def get_logs(self) -> List[str]:
        """Wrapper to retrieve the contents of the FFI log buffer.

        :return: List of log entries, each a line of log output
        """

        # Having problems with the buffer output, when running via CLI
        # Reverting to log file output instead
        # result = self.lib.pactffi_fetch_log_buffer()
        # print(f"{result=}")
        # return self.ffi.string(result).decode("utf-8").rstrip().split("\n")

        # If using log to file, retrieve like this, otherwise remove
        lines = open(PactFFI.output_file).readlines()
        open(PactFFI.output_file, "w").close()
        return [line.lstrip("\x00") for line in lines]
