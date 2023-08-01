import json
import requests

from pact import PactV3
from pact.ffi.native_mock_server import MockServerStatus
from pact.matchers_v3 import Like, Regex

def test_ffi_http_consumer():
    request_interaction_body = {
        "isbn": Like("0099740915"),
        "title": Like("The Handmaid\'s Tale"),
        "description": Like("Brilliantly conceived and executed, this powerful evocation of twenty-first"
                            " century America gives full rein to Margaret Atwood\'s devastating irony, wit and astute perception."),
        "author": Like("Margaret Atwood"),
        "publicationDate":
        Regex("\\d{4}-[01]\\d-[0-3]\\dT[0-2]\\d:[0-5]\\d:[0-5]\\d([+-][0-2]\\d:[0-5]\\d|Z)", "1985-07-31T00:00:00+00:00"),
    }

    response_interaction_body = {
        "@context": "/api/contexts/Book",
        "@id":
        Regex("^\\/api\\/books\\/[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$", "/api/books/0114b2a8-3347-49d8-ad99-0e792c5a30e6"),
        "@type": "Book",
        "title": Like("Voluptas et tempora repellat corporis excepturi."),
        "description": Like("Quaerat odit quia nisi accusantium natus voluptatem. Explicabo corporis eligendi "
                            "ut ut sapiente ut qui quidem. Optio amet velit aut delectus. Sed alias asperiores "
                            "perspiciatis deserunt omnis. Mollitia unde id in."),
        "author":
            Like("Melisa Kassulke"),
        "publicationDate": Regex(
            "^\\d{4}-[01]\\d-[0-3]\\dT[0-2]\\d:[0-5]\\d:[0-5]\\d([+-][0-2]\\d:[0-5]\\d|Z)$",
            "1999-02-13T00:00:00+07:00"
        ),
        "reviews": [
        ]
    }

    # Setup pact for testing
    provider = PactV3('http-consumer-1', 'http-provider')
    (provider
     .new_http_interaction('A POST request to create book')
     .given('No book fixtures required')
     .upon_receiving('A POST request to create book')
     .with_request(
         'POST',
         '/api/books',
         headers=[{"name": "Content-Type", "value": 'application/json'}],
         body=request_interaction_body
     )
     .will_respond_with(
         200,
         headers=[{"name": "Content-Type", "value": 'application/ld+json; charset=utf-8'}],
         body=response_interaction_body,
     )
     )

    # Start mock server (the port is also available via provider.mock_server_port)
    # mock_server_port = provider.start_service()
    mock_server_port = provider.start_service()

    # Make our client call
    body = {
        "isbn": '0099740915',
        "title": "The Handmaid's Tale",
        "description": "Brilliantly conceived and executed, this powerful evocation of twenty-first "
        "century America gives full rein to Margaret Atwood\'s devastating irony, wit and astute perception.",
        "author": 'Margaret Atwood',
        "publicationDate": '1985-07-31T00:00:00+00:00'
    }
    expected_response = {
        "@context": "/api/contexts/Book",
        "@id": "/api/books/0114b2a8-3347-49d8-ad99-0e792c5a30e6",
        "@type": "Book",
        "author": "Melisa Kassulke",
        "description": "Quaerat odit quia nisi accusantium natus voluptatem. Explicabo corporis eligendi ut ut sapiente ut qui quidem. "
        "Optio amet velit aut delectus. Sed alias asperiores perspiciatis deserunt omnis. Mollitia unde id in.",
        "publicationDate": "1999-02-13T00:00:00+07:00",
        "reviews": [],
        "title": "Voluptas et tempora repellat corporis excepturi."}
    try:
        response = requests.post(f"http://127.0.0.1:{mock_server_port}/api/books", data=json.dumps(body),
                                 headers={'Content-Type': 'application/json'})
        print(f"{expected_response}")
        print(f"Client response - matched: {json.loads(response.text) == expected_response}")
        response.raise_for_status()
    except requests.HTTPError as http_err:
        print(f'Client request - HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Client request - Other error occurred: {err}')  # Python 3.6

    result = provider.verify()
    assert MockServerStatus(result.return_code) == MockServerStatus.SUCCESS
