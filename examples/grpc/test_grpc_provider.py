from sys import version_info
from time import sleep
import pytest
from pact import VerifierV3
import subprocess
from pact.ffi.verifier import VerifyStatus

@pytest.mark.skipif(
    version_info < (3, 7),
    reason="https://stackoverflow.com/questions/71759248/importerror-cannot-import-name-builder-from-google-protobuf-internal")
def test_grpc_local_pact():

    grpc_server_process = subprocess.Popen(['python', 'area_calculator_server.py'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT, universal_newlines=True)

    # grpc_server_process = subprocess.Popen(['python', 'area_calculator_server.py'],
    #                                        cwd=join(dirname(__file__), '..', '..', 'examples', 'area_calculator'),
    #                                        stdout=subprocess.PIPE,
    #                                        stderr=subprocess.STDOUT, universal_newlines=True)
    sleep(3)

    verifier = VerifierV3(provider="area-calculator-provider-example",
                          provider_base_url="tcp://127.0.0.1:37757",
                          )
    result = verifier.verify_pacts(
        sources=["../pacts/grpc-consumer-python-area-calculator-provider.json"],
    )
    grpc_server_process.terminate()
    assert VerifyStatus(result.return_code) == VerifyStatus.SUCCESS
    # TODO - Plugin success or failure not returned in logs
