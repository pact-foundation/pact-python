import pytest
import mock
from pact.ffi.verifier import VerifyStatus

from pact.pact_exception import PactException
from pact.ffi.ffi_verifier import FFIVerify

def test_version():
    assert FFIVerify().version() == "0.4.5"


@mock.patch("os.listdir")
def test_pact_urls_or_broker_required(mock_Popen):
    # mock_Popen.return_value.returncode = 2
    verifier = FFIVerify()

    with pytest.raises(PactException) as e:
        verifier.verify(provider='provider', provider_base_url='http://localhost')

    assert 'Pact urls or Pact broker required' in str(e)

def test_pact_local_file_provided_but_does_not_exist():
    wrapper = FFIVerify()
    result = wrapper.verify(
                                    './pacts/consumer-provider.json',
                                    provider='test_provider',
                                    provider_base_url='http://localhost')
    assert VerifyStatus(result.return_code) == VerifyStatus.VERIFIER_FAILED
    assert "Failed to load pact './pacts/consumer-provider.json' - No such file or directory" in "\n".join(result.logs)

def test_pact_url_provided_but_does_not_exist():
    wrapper = FFIVerify()
    result = wrapper.verify(
                                    'http://broker.com/pacts/consumer-provider.json',
                                    provider='test_provider',
                                    provider_base_url='http://localhost')
    assert VerifyStatus(result.return_code) == VerifyStatus.VERIFIER_FAILED
    assert "Failed to load pact 'http://broker.com/pacts/consumer-provider.json' - Request failed with status - 404 Not Found" in "\n".join(result.logs)
