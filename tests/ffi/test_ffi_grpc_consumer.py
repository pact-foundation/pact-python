import os
from subprocess import Popen
from os.path import join, dirname

# import examples.area_calculator.area_calculator_pb2 as area_calculator_pb2
# from examples.area_calculator.area_calculator_client import get_rectangle_area
from pact.ffi.pact_consumer import *
import sys
sys.path.insert(0, './examples/area_calculator')
from area_calculator_client import get_rectangle_area

PACT_FILE_DIR = './examples/pacts'

def test_ffi_grpc_consumer():
    # Setup pact for testing
    pact = new_pact('grpc-consumer-python', 'area-calculator-provider')
    message_pact = new_sync_message_interaction(pact, 'A gRPC calculateMulti request')
    with_specification(pact, 5)
    using_plugin(pact, 'protobuf', '0.3.4')

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
    interaction_contents(message_pact, "res", 'application/grpc', json.dumps(contents))
    mock_server_port = start_mock_server(pact, '0.0.0.0', 0, 'grpc', None)

    # Make our client call
    expected_response = 12.0
    response = get_rectangle_area(f"localhost:{mock_server_port}")
    print(f"Client response: {response}")
    print(f"Client response - matched expected: {response == expected_response}")

    # Check our result and write pact to file
    verify(mock_server_port, pact, PACT_FILE_DIR)