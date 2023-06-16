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
