"""Wrapper to pact reference dynamic libraries using FFI."""
import os
import platform
import tempfile
from enum import unique, Enum
from typing import List

from cffi import FFI


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
    output_dir: tempfile.TemporaryDirectory = None
    output_file: str = None

    def __init__(self):
        if not PactFFI.output_dir:
            # The output will be stored in a file in this directory, which will
            # be cleaned up automatically at the end
            PactFFI.output_dir = tempfile.TemporaryDirectory()

            PactFFI.ffi = FFI()

            # Define all the functions from the various modules, since we can
            # only load the library once
            PactFFI.ffi.cdef(
                """
            // root crate
            char *pactffi_version(void);

            // verifier
            int pactffi_verify(char *);
            
            // log
            int pactffi_log_to_file(char *);
            """
            )
            PactFFI.lib = self._load_ffi_library(PactFFI.ffi)

            # Setup logging to a file in the output_dir
            PactFFI.output_file = os.path.join(PactFFI.output_dir.name, 'output')
            output_c = self.ffi.new('char[]', bytes(self.output_file, 'utf-8'))
            result = self.lib.pactffi_log_to_file(output_c)
            assert LogToBufferStatus(result) == LogToBufferStatus.SUCCESS

    def version(self) -> str:
        """Get the current library version.

        :return: pact_ffi library version, for example "0.0.1"
        """
        result = self.lib.pactffi_version()
        return self.ffi.string(result).decode('utf-8')

    def _load_ffi_library(self, ffi):
        """Load the appropriate library for the current platform."""
        target_platform = platform.platform().lower()

        if target_platform in ['darwin', 'macos']:
            libname = "pact/bin/libpact_ffi-osx-x86_64.dylib"
        elif 'linux' in target_platform:
            libname = "pact/bin/libpact_ffi-linux-x86_64.so"
        elif 'windows' in target_platform:
            libname = "pact/bin/pact_ffi-windows-x86_64.dll"
        else:
            msg = (
                f'Unfortunately, {platform.platform()} is not a supported '
                f'platform. Only Linux, Windows, and OSX are currently '
                f'supported.'
            )
            raise Exception(msg)

        return ffi.dlopen(libname)

    def _get_logs(self) -> List[str]:
        """Wrapper to retrieve the contents of the FFI logfile.
        This will additionally empty the log file, ready for the next call.
        :return:
        """

        lines = open(PactFFI.output_file).readlines()
        open(PactFFI.output_file, 'w').close()
        return lines
