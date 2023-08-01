import json
import os
from pact.ffi.native_mock_server import MockServer, MockServerStatus
from sys import path
path.insert(0, './examples/area_calculator')
from area_calculator_client import get_rectangle_area  # noqa: E402

# from examples.area_calculator.area_calculator_client import get_rectangle_area

m = MockServer()
PACT_FILE_DIR = './examples/pacts'

def test_ffi_grpc_consumer():
    # Setup pact for testing
    pact = m.new_pact('grpc-consumer-python', 'area-calculator-provider')
    message_pact = m.new_sync_message_interaction(pact, 'A gRPC calculateMulti request')
    m.with_specification(pact, 5)
    m.using_plugin(pact, 'protobuf', '0.3.4')

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
    m.interaction_contents(message_pact, "res", 'application/grpc', json.dumps(contents))
    mock_server_port = m.start_mock_server(pact, '0.0.0.0', 0, 'grpc', None)

    # Make our client call
    expected_response = 12.0
    response = get_rectangle_area(f"localhost:{mock_server_port}")
    print(f"Client response: {response}")
    print(f"Client response - matched expected: {response == expected_response}")

    # Check our result and write pact to file
    result = m.verify(mock_server_port, pact, PACT_FILE_DIR)
    assert MockServerStatus(result.return_code) == MockServerStatus.SUCCESS
