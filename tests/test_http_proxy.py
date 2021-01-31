from pact import http_proxy as http_proxy
from unittest import TestCase
from mock import patch, Mock
import json

class HttpProxyTestCase(TestCase):
    def test_ping(self):
        res = http_proxy.app.test_client().get('/ping')
        self.assertEqual(res.status_code, 200)
        json_res = res.get_json()
        self.assertEqual(json_res['ping'], 'pong')

    @patch.object(http_proxy, 'request')
    def test_shutdown(self, mock_request):
        mock_shutdown = Mock()
        mock_request.environ.get.return_value(mock_shutdown)
        res = http_proxy.app.test_client().post('/shutdown')
        self.assertEqual(res.status_code, 200)

    def test_shutdown_should_raise_500(self):
        res = http_proxy.app.test_client().post('/shutdown')
        self.assertEqual(res.status_code, 500)
        self.assertEqual(res.get_json(), {
            "description": "Not running with the Werkzeug Server",
            "name": "RuntimeError"
        })

    def test_setup(self):
        payload = {'anyPayload': 'really'}
        res = http_proxy.app.test_client().post(
            '/setup',
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(res.status_code, 201)
        json_res = res.get_json()
        assert json_res == payload

    def setup_state(self, payload):
        setup_res = http_proxy.app.test_client().post(
            '/setup',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(setup_res.status_code, 201)

    def test_handle_http_error(self):
        res = http_proxy.app.test_client().get(
            '/something_does_not_exist'
        )
        self.assertEqual(res.status_code, 404)
        json_res = res.get_json()
        json_res['code'] = 404
        json_res['name'] = 'Not Found'

    def test_home_should_return_expected_resonse(self):
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

        res = http_proxy.app.test_client().post(
            '/',
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(res.get_json(), {'contents': message})

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
        res = http_proxy.app.test_client().post(
            '/',
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(res.status_code, 500)
        assert res.get_json() == {
            'description': 'No matched handler.',
            'name': 'RuntimeError'
        }
