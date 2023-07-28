import json
import requests

from pact.ffi.pact_consumer import *

PACT_FILE_DIR = './examples/pacts'

def test_ffi_message_consumer():
    # Setup http pact for testing
    pact = new_pact('http-consumer-2', 'http-provider')
    interaction = new_interaction(pact, 'A PUT request to generate book cover')
    # setup interaction request
    upon_receiving(interaction, 'A PUT request to generate book cover')
    given(interaction, 'A book with id fb5a885f-f7e8-4a50-950f-c1a64a94d500 is required')
    with_request(interaction, 'PUT', '/api/books/fb5a885f-f7e8-4a50-950f-c1a64a94d500/generate-cover')
    with_request_header(interaction, 'Content-Type', 0, 'application/json')
    with_request_body(interaction, 'application/json', [])
    # setup interaction response
    response_status(interaction, 204)
    # Setup message pact for testing
    contents = {
        "uuid": {
            "pact:matcher:type": 'regex',
            "regex": '^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$',
            "value": 'fb5a885f-f7e8-4a50-950f-c1a64a94d500'
        }
    }
    message_pact = new_pact('message-consumer-2', 'message-provider')
    message = new_message(message_pact, 'Book (id fb5a885f-f7e8-4a50-950f-c1a64a94d500) created message')
    message_expects_to_receive(message, 'Book (id fb5a885f-f7e8-4a50-950f-c1a64a94d500) created message')
    message_given(message, 'A book with id fb5a885f-f7e8-4a50-950f-c1a64a94d500 is required')
    message_with_contents(message, 'application/json', contents)
    
    # Start mock server
    mock_server_port = start_mock_server(pact, '0.0.0.0', 0, 'http', None)
    reified = message_reify(message)
    uuid = json.loads(reified)['contents']['uuid']
    
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

    # verify and write pact if success
    verify(mock_server_port, pact, PACT_FILE_DIR, message_pact)
