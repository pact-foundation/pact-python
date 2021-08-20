"""Wrapper to pact reference dynamic libraries using FFI."""

import platform

from cffi import FFI


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



    def version(self) -> str:
        """Get the current library version.

        :return: pact_ffi library version, for example "0.0.1"
        """
        ffi = FFI()
        ffi.cdef(
            """
        char *pactffi_version(void);
        """
        )
        lib = self._load_ffi_library(ffi)
        result = lib.pactffi_version()

        return ffi.string(result).decode('utf-8')

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
