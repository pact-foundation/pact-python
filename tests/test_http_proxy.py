from unittest import TestCase
from pact.http_proxy import app
from fastapi.testclient import TestClient
client = TestClient(app)


class HttpProxyTestCase(TestCase):

    def test_ping(self):
        res = client.get('/ping')
        self.assertEqual(res.status_code, 200)
        assert res.json() == {"ping": "pong"}

    def test_handle_http_error(self):
        res = client.get(
            '/something_does_not_exist'
        )
        self.assertEqual(res.status_code, 404)
        json_res = res.json()
        json_res['code'] = 404
        json_res['name'] = 'Not Found'

    def test_setup(self):
        payload = {'anyPayload': 'really'}
        res = client.post(
            '/setup',
            json=payload
        )

        self.assertEqual(res.status_code, 201)
        json_res = res.json()
        assert json_res == payload

    def setup_state(self, payload):
        setup_res = client.post(
            '/setup',
            json=payload
        )
        self.assertEqual(setup_res.status_code, 201)

    def test_home_should_return_expected_response(self):
        message = {
            'event': 'ObjectCreated:Put',
            'bucket': 'bucket_name',
            'key': 'path_to_file_in_s3.pdf',
            'documentType': 'application/pdf'
        }

        data = {
            'messageHandlers': {
                'A document created successfully': message
            }
        }

        self.setup_state(data)

        payload = {
            'providerStates': [{'name': 'A document created successfully'}]
        }

        res = client.post(
            '/',
            json=payload
        )

        self.assertEqual(res.json(), {'contents': message})

    def test_home_raise_runtime_error_if_no_matched(self):
        data = {
            'messageHandlers': {
                'A document created successfully': {
                    'event': 'ObjectCreated:Put'
                }
            }
        }
        self.setup_state(data)
        payload = {
            'providerStates': [{'name': 'New state to raise RuntimeError'}]
        }
        res = client.post(
            '/',
            json=payload
        )

        self.assertEqual(res.status_code, 500)
        assert res.json() == {
            'detail': 'No matched handler.'
        }
