import json
import requests

from pact.ffi.pact_consumer import *

PACT_FILE_DIR = './examples/pacts'

def test_ffi_http_consumer():
    request_interaction_body = {
        "isbn": {
            "pact:matcher:type": "type",
            "value": "0099740915"
        },
        "title": {
            "pact:matcher:type": "type",
            "value": "The Handmaid\'s Tale"
        },
        "description": {
            "pact:matcher:type": "type",
            "value": "Brilliantly conceived and executed, this powerful evocation of twenty-first century America gives full rein to Margaret Atwood\'s devastating irony, wit and astute perception."
        },
        "author": {
            "pact:matcher:type": "type",
            "value": "Margaret Atwood"
        },
        "publicationDate": {
            "pact:matcher:type": "regex",
            "regex": "^\\d{4}-[01]\\d-[0-3]\\dT[0-2]\\d:[0-5]\\d:[0-5]\\d([+-][0-2]\\d:[0-5]\\d|Z)$",
            "value": "1985-07-31T00:00:00+00:00"
        }
    }

    response_interaction_body = {
        "@context": "/api/contexts/Book",
        "@id": {
            "pact:matcher:type": "regex",
            "regex": "^\\/api\\/books\\/[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$",
            "value": "/api/books/0114b2a8-3347-49d8-ad99-0e792c5a30e6"
        },
        "@type": "Book",
        "title": {
            "pact:matcher:type": "type",
            "value": "Voluptas et tempora repellat corporis excepturi."
        },
        "description": {
            "pact:matcher:type": "type",
            "value": "Quaerat odit quia nisi accusantium natus voluptatem. Explicabo corporis eligendi ut ut sapiente ut qui quidem. Optio amet velit aut delectus. Sed alias asperiores perspiciatis deserunt omnis. Mollitia unde id in."
        },
        "author": {
            "pact:matcher:type": "type",
            "value": "Melisa Kassulke"
        },
        "publicationDate": {
            "pact:matcher:type": "regex",
            "regex": "^\\d{4}-[01]\\d-[0-3]\\dT[0-2]\\d:[0-5]\\d:[0-5]\\d([+-][0-2]\\d:[0-5]\\d|Z)$",
            "value": "1999-02-13T00:00:00+07:00"
        },
        "reviews": [
        ]
    }
    # Setup pact for testing
    pact = new_pact('http-consumer-1', 'http-provider')
    interaction = new_interaction(pact, 'A POST request to create book')
    # setup interaction request
    upon_receiving(interaction, 'A POST request to create book')
    given(interaction, 'No book fixtures required')
    with_request(interaction, 'POST', '/api/books')
    with_request_header(interaction, 'Content-Type', 0, 'application/json')
    with_request_body(interaction, 'application/json', request_interaction_body)
    # setup interaction response
    response_status(interaction, 200)
    with_response_header(interaction, 'Content-Type', 0, 'application/ld+json; charset=utf-8')
    with_response_body(interaction, 'application/json', response_interaction_body)
    # Start mock server
    mock_server_port = start_mock_server(pact, '0.0.0.0', 0, 'http', None)

    # Make our client call
    body = {
        "isbn": '0099740915',
        "title": "The Handmaid's Tale",
        "description": 'Brilliantly conceived and executed, this powerful evocation of twenty-first century America gives full rein to Margaret Atwood\'s devastating irony, wit and astute perception.',
        "author": 'Margaret Atwood',
        "publicationDate": '1985-07-31T00:00:00+00:00'
    }
    expected_response = '{"@context":"/api/contexts/Book","@id":"/api/books/0114b2a8-3347-49d8-ad99-0e792c5a30e6","@type":"Book","author":"Melisa Kassulke","description":"Quaerat odit quia nisi accusantium natus voluptatem. Explicabo corporis eligendi ut ut sapiente ut qui quidem. Optio amet velit aut delectus. Sed alias asperiores perspiciatis deserunt omnis. Mollitia unde id in.","publicationDate":"1999-02-13T00:00:00+07:00","reviews":[],"title":"Voluptas et tempora repellat corporis excepturi."}'
    try:
        response = requests.post(f"http://127.0.0.1:{mock_server_port}/api/books", data=json.dumps(body),
                                 headers={'Content-Type': 'application/json'})
        print(f"Client response: {response.text}")
        print(f"expected_response: {expected_response}")
        print(f"Client response - matched: {response.text == expected_response}")
        response.raise_for_status()
    except requests.HTTPError as http_err:
        print(f'Client request - HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Client request - Other error occurred: {err}')  # Python 3.6

    verify(mock_server_port, pact, PACT_FILE_DIR)
