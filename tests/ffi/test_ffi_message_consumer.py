import json
import requests

from pact.ffi.pact_ffi import PactFFI
from tests.ffi.utils import check_results, se
from pact.__version__ import __version__

pactlib = PactFFI()
PACT_FILE_DIR = './examples/pacts'

def test_ffi_message_consumer():
    # Setup pact for testing
    pact_handle = pactlib.lib.pactffi_new_pact(b'http-consumer-2', b'http-provider')
    pactlib.lib.pactffi_with_pact_metadata(pact_handle, b'pact-python', b'version', se(__version__))
    interaction = pactlib.lib.pactffi_new_interaction(pact_handle, b'A PUT request to generate book cover')
    message_pact = pactlib.lib.pactffi_new_pact(b'message-consumer-2', b'message-provider')
    message = pactlib.lib.pactffi_new_message(message_pact, b'Book (id fb5a885f-f7e8-4a50-950f-c1a64a94d500) created message')

    # setup interaction request
    pactlib.lib.pactffi_upon_receiving(interaction, b'A PUT request to generate book cover')
    pactlib.lib.pactffi_given(interaction, b'A book with id fb5a885f-f7e8-4a50-950f-c1a64a94d500 is required')
    pactlib.lib.pactffi_with_request(interaction, b'PUT', b'/api/books/fb5a885f-f7e8-4a50-950f-c1a64a94d500/generate-cover')
    pactlib.lib.pactffi_with_header_v2(interaction, 0, b'Content-Type', 0, b'application/json')
    pactlib.lib.pactffi_with_body(interaction, 0, b'application/json', b'[]')
    # setup interaction response
    pactlib.lib.pactffi_response_status(interaction, 204)
    contents = {
        "uuid": {
            "pact:matcher:type": 'regex',
            "regex": '^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$',
            "value": 'fb5a885f-f7e8-4a50-950f-c1a64a94d500'
        }
    }
    length = len(json.dumps(contents))
    size = length + 1
    pactlib.lib.pactffi_message_expects_to_receive(message, b'Book (id fb5a885f-f7e8-4a50-950f-c1a64a94d500) created message')
    pactlib.lib.pactffi_message_given(message, b'A book with id fb5a885f-f7e8-4a50-950f-c1a64a94d500 is required')
    pactlib.lib.pactffi_message_with_contents(message, b'application/json', pactlib.ffi.new("char[]", json.dumps(contents).encode('ascii')), size)
    # Start mock server
    mock_server_port = pactlib.lib.pactffi_create_mock_server_for_transport(pact_handle, b'0.0.0.0', 0, b'http', pactlib.ffi.cast("void *", 0))
    print(f"Mock server started: {mock_server_port}")
    reified = pactlib.lib.pactffi_message_reify(message)
    uuid = json.loads(pactlib.ffi.string(reified).decode('utf-8'))['contents']['uuid']

    # Make our client call
    body = []
    try:
        response = requests.put(f"http://127.0.0.1:{mock_server_port}/api/books/{uuid}/generate-cover", data=json.dumps(body),
                                headers={'Content-Type': 'application/json'})
        print(f"Client response - matched: {response.text}")
        print(f"Client response - matched: {response.status_code}")
        print(f"Client response - matched: {response.status_code == '204'}")
        response.raise_for_status()
    except requests.HTTPError as http_err:
        print(f'Client request - HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Client request - Other error occurred: {err}')  # Python 3.6

    check_results(pactlib, mock_server_port, pact_handle, PACT_FILE_DIR, message_pact)
