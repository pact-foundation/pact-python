"""Wrapper to pact reference dynamic libraries using FFI."""
from pact.pact_exception import PactException
from cffi import FFI
from pact.ffi.register_ffi import RegisterFfi

class FFIVerify(object):
    """A Pact Verifier Wrapper."""

    def version(self):
        """Publish version info."""
        ffi = FFI()
        lib = RegisterFfi().get_ffi_lib(ffi)
        result = lib.pactffi_version()
        return ffi.string(result).decode('utf-8')

    def verify(self, *pacts, provider_base_url, provider, enable_pending=False,
               include_wip_pacts_since=None, **kwargs):
        """Call verify method."""
        self._validate_input(pacts, **kwargs)

        ffi = FFI()
        lib = RegisterFfi().get_ffi_lib(ffi)
        lib.pactffi_log_to_stdout(5)
        verifier = lib.pactffi_verifier_new_for_application(b'pact-python',b'1.0.0')
        lib.pactffi_verifier_set_provider_info(verifier,provider.encode('ascii'),b'http', b'localhost', 8000, b'/');
        result = lib.pactffi_verifier_execute(verifier);
        get_logs = lib.pactffi_verifier_logs(verifier);
        
        if pacts:
            for pact in pacts:
                lib.pactffi_verifier_add_file_source(verifier, pact.encode('ascii'));
        

        
        
        # lib.pactffi_log_to_stderr(5)
        # lib.pactffi_log_to_buffer(5)
        # result = lib.pactffi_version()
        # foo = [tuple(map(lambda x: x.encode('ascii'), tup)) for tup in pacts]
        # lib.pactffi_verifier_add_directory_source(verifier, *pacts.each.encode('ascii'));

        

        # lib.pactffi_verifier_add_file_source(verifier, b'./pacts/consumer-provider.json');



        lib.pactffi_verifier_shutdown(verifier);
        # return get_logs
        print(ffi.string(get_logs).decode('utf-8'))
        return result

    def _validate_input(self, pacts, **kwargs):
        if len(pacts) == 0 and not self._broker_present(**kwargs):
            raise PactException('Pact urls or Pact broker required')

    def _broker_present(self, **kwargs):
        if kwargs.get('broker_url') is None:
            return False
        return True
