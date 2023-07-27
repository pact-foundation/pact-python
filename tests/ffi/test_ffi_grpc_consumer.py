import os
import json
from tests.ffi.utils import check_results, se
from pact.ffi.pact_ffi import PactFFI
from area_calculator_client import get_rectangle_area
import sys
sys.path.insert(0, './examples/area_calculator')

pactlib = PactFFI()
PACT_FILE_DIR = './examples/pacts'

def test_ffi_grpc_consumer():
    # Setup pact for testing
    pact_handle = pactlib.lib.pactffi_new_pact(b'grpc-consumer-python', b'area-calculator-provider')
    pactlib.lib.pactffi_with_pact_metadata(pact_handle, b'pact-python', b'ffi', se(pactlib.version()))
    message_pact = pactlib.lib.pactffi_new_sync_message_interaction(pact_handle, b'A gRPC calculateMulti request')
    pactlib.lib.pactffi_with_specification(pact_handle, 5)

    # our interaction contents
    contents = {
        "pact:proto": os.path.abspath('./examples/proto/area_calculator.proto'),
        "pact:proto-service": 'Calculator/calculateOne',
        "pact:content-type": 'application/protobuf',
        "request": {
            "rectangle": {
                "length": 'matching(number, 3)',
                "width": 'matching(number, 4)'
            }
        },
        "response": {
            "value": ['matching(number, 12)']
        }
    }

    # Start mock server
    pactlib.lib.pactffi_using_plugin(pact_handle, b'protobuf', b'0.3.4')
    pactlib.lib.pactffi_interaction_contents(message_pact, 0, b'application/grpc', pactlib.ffi.new("char[]", json.dumps(contents).encode('ascii')))
    mock_server_port = pactlib.lib.pactffi_create_mock_server_for_transport(pact_handle, b'0.0.0.0', 0, b'grpc', pactlib.ffi.cast("void *", 0))
    print(f"Mock server started: {mock_server_port}")

    # Make our client call
    expected_response = 12.0
    response = get_rectangle_area(f"localhost:{mock_server_port}")
    print(f"Client response: {response}")
    print(f"Client response - matched expected: {response == expected_response}")

    # Check our result and write pact to file
    check_results(pactlib, mock_server_port, pact_handle, PACT_FILE_DIR)
