"""Wrapper to pact reference dynamic libraries using FFI."""
from cffi import FFI
import platform

class FFIVerify(object):
    """A Pact Verifier Wrapper."""

    def version(self):
        """Publish version info."""
        ffi = FFI()
        ffi.cdef("""
        char *pactffi_version(void);
        """)
        lib = self._load_ffi_library(ffi)
        result = lib.pactffi_version()
        return ffi.string(result).decode('utf-8')

    def verify(self):
        """Call verify method."""
        ffi = FFI()
        ffi.cdef("""
        char *pactffi_verify(void);
        """)
        lib = self._load_ffi_library(ffi)
        result = lib.pactffi_version()
        return ffi.string(result).decode('utf-8')

# pactffi_verify

    def _load_ffi_library(self, ffi):
        """Load the right library."""
        target_platform = platform.platform().lower()

        if 'darwin' in target_platform or 'macos' in target_platform:
            libname = "libs/libpact_ffi-osx-x86_64.dylib"
        elif 'linux' in target_platform:
            libname = "libs/libpact_ffi-linux-x86_64.so"
        elif 'windows' in target_platform:
            libname = "libs/libpact_ffi-osx-x86_64.dylib"
        else:
            msg = ('Unfortunately, {} is not a supported platform. Only Linux,'
                   ' Windows, and OSX are currently supported.').format(
                platform.platform())
            raise Exception(msg)

        return ffi.dlopen(libname)
