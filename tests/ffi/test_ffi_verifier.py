import pytest
import mock

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

def test_pact_files_provided():
    # mock_Popen.return_value.returncode = 0
    wrapper = FFIVerify()

    result = wrapper.verify(
                                    './pacts/consumer-provider.json',
        #                             './pacts/consumer-provider2.json',
                                    provider='test_provider',
                                    provider_base_url='http://localhost')
    assert 'foo' in str(result)
    # self.default_call.insert(0, './pacts/consumer-provider.json')
    # self.default_call.insert(1, './pacts/consumer-provider2.json')
    # self.assertProcess(*self.default_call)
    # self.assertEqual(result, 0)
