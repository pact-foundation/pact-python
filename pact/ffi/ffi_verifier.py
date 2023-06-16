"""Wrapper to pact reference dynamic libraries using FFI."""
from pact.pact_exception import PactException
from cffi import FFI
from register_ffi import get_ffi_lib

class FFIVerify(object):
    """A Pact Verifier Wrapper."""

    def version(self):
        """Publish version info."""
        ffi = FFI()
        lib = get_ffi_lib(ffi)
        result = lib.pactffi_version()
        return ffi.string(result).decode('utf-8')

    def verify(self, *pacts, provider_base_url, provider, enable_pending=False,
               include_wip_pacts_since=None, **kwargs):
        """Call verify method."""
        self._validate_input(pacts, **kwargs)

        ffi = FFI()
        lib = get_ffi_lib(ffi)
        result = lib.pactffi_version()
        return ffi.string(result).decode('utf-8')

    def _validate_input(self, pacts, **kwargs):
        if len(pacts) == 0 and not self._broker_present(**kwargs):
            raise PactException('Pact urls or Pact broker required')

    def _broker_present(self, **kwargs):
        if kwargs.get('broker_url') is None:
            return False
        return True
