"""Wrapper to pact reference dynamic libraries using FFI."""
from pact.ffi.verifier import VerifyResult
from pact.pact_exception import PactException
from cffi import FFI
from pact.ffi.register_ffi import RegisterFfi
from pact.verify_wrapper import expand_directories, is_url

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
        # lib.pactffi_log_to_stdout(5)
        lib.pactffi_log_to_buffer(1)
        verifier = lib.pactffi_verifier_new_for_application(b'pact-python',b'1.0.0')
        lib.pactffi_verifier_set_provider_info(verifier,provider.encode('ascii'),b'http', b'localhost', 8000, b'/');
        lib.pactffi_verifier_set_verification_options(verifier, False, 5000)

        local_file = False
        all_pact_urls = False
        if pacts:
            all_pact_urls = expand_directories(list(pacts))
            for pact_url in all_pact_urls:
                if not is_url(pact_url):
                    local_file = True

        if all_pact_urls and local_file:
            for pact in all_pact_urls:
                lib.pactffi_verifier_add_file_source(verifier, pact.encode('ascii'));
        elif all_pact_urls and local_file is False:
            for pact in all_pact_urls:
                # void pactffi_verifier_url_source(struct VerifierHandle *handle,
                #                  const char *url,
                #                  const char *username,
                #                  const char *password,
                #                  const char *token);
                lib.pactffi_verifier_url_source(verifier, pact.encode('ascii'),b'NULL',b'NULL',b'NULL');
        

        result = lib.pactffi_verifier_execute(verifier);
        get_logs = lib.pactffi_verifier_logs(verifier);
        
        
        # lib.pactffi_log_to_stderr(5)
        # result = lib.pactffi_version()
        # foo = [tuple(map(lambda x: x.encode('ascii'), tup)) for tup in pacts]
        # lib.pactffi_verifier_add_directory_source(verifier, *pacts.each.encode('ascii'));

        

        # lib.pactffi_verifier_add_file_source(verifier, b'./pacts/consumer-provider.json');



        lib.pactffi_verifier_shutdown(verifier);
        # return get_logs
        logs = ffi.string(get_logs).decode('utf-8').rstrip().split("\n")
        print(logs)
        return VerifyResult(result, logs)

    def _validate_input(self, pacts, **kwargs):
        if len(pacts) == 0 and not self._broker_present(**kwargs):
            raise PactException('Pact urls or Pact broker required')

    def _broker_present(self, **kwargs):
        if kwargs.get('broker_url') is None:
            return False
        return True
