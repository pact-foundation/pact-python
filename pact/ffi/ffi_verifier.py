"""Wrapper to pact reference dynamic libraries using FFI."""
from pact.pact_exception import PactException
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

    def verify(self, *pacts, provider_base_url, provider, enable_pending=False,
               include_wip_pacts_since=None, **kwargs):
        """Call verify method."""
        self._validate_input(pacts, **kwargs)

        ffi = FFI()
        ffi.cdef("""
        char *pactffi_verify(void);
        """)
        lib = self._load_ffi_library(ffi)
        result = lib.pactffi_version()
        return ffi.string(result).decode('utf-8')

    def _load_ffi_library(self, ffi):
        """Load the right library."""
        target_platform = platform.platform().lower()

        if ("darwin" in target_platform or "macos" in target_platform) and "aarch64" or "arm64" in platform.machine():
            # TODO: Untested, can someone with the appropriate architecture verify?
            libname = "pact/bin/libpact_ffi-osx-aarch64-apple-darwin.dylib"
        elif target_platform in ["darwin", "macos"]:
            libname = "pact/bin/libpact_ffi-osx-x86_64.dylib"
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

    def _validate_input(self, pacts, **kwargs):
        if len(pacts) == 0 and not self._broker_present(**kwargs):
            raise PactException('Pact urls or Pact broker required')

    def _broker_present(self, **kwargs):
        if kwargs.get('broker_url') is None:
            return False
        return True
