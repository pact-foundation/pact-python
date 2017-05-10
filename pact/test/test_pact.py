import os
from unittest import TestCase

from mock import patch, call, Mock

from .. import Consumer, Provider, pact
from ..constants import MOCK_SERVICE_PATH
from ..pact import Pact, FromTerms, Request, Response


class PactTestCase(TestCase):
    def setUp(self):
        self.consumer = Consumer('TestConsumer')
        self.provider = Provider('TestProvider')

    def test_init_defaults(self):
        target = Pact(self.consumer, self.provider)
        self.assertIs(target.consumer, self.consumer)
        self.assertIs(target.cors, False)
        self.assertEqual(target.host_name, 'localhost')
        self.assertEqual(target.log_dir, os.getcwd())
        self.assertEqual(target.pact_dir, os.getcwd())
        self.assertEqual(target.port, 1234)
        self.assertIs(target.provider, self.provider)
        self.assertIs(target.ssl, False)
        self.assertIsNone(target.sslcert)
        self.assertIsNone(target.sslkey)
        self.assertEqual(target.uri, 'http://localhost:1234')
        self.assertEqual(target.version, '2.0.0')
        self.assertIsNone(target._description)
        self.assertIsNone(target._provider_state)
        self.assertIsNone(target._request)
        self.assertIsNone(target._response)
        self.assertIsNone(target._scenario)

    def test_init_custom_mock_service(self):
        target = Pact(
            self.consumer, self.provider, host_name='192.168.1.1', port=8000,
            log_dir='/logs', ssl=True, sslcert='/ssl.cert', sslkey='/ssl.pem',
            cors=True, pact_dir='/pacts', version='3.0.0')

        self.assertIs(target.consumer, self.consumer)
        self.assertIs(target.cors, True)
        self.assertEqual(target.host_name, '192.168.1.1')
        self.assertEqual(target.log_dir, '/logs')
        self.assertEqual(target.pact_dir, '/pacts')
        self.assertEqual(target.port, 8000)
        self.assertIs(target.provider, self.provider)
        self.assertIs(target.ssl, True)
        self.assertEqual(target.sslcert, '/ssl.cert')
        self.assertEqual(target.sslkey, '/ssl.pem')
        self.assertEqual(target.uri, 'https://192.168.1.1:8000')
        self.assertEqual(target.version, '3.0.0')
        self.assertIsNone(target._description)
        self.assertIsNone(target._provider_state)
        self.assertIsNone(target._request)
        self.assertIsNone(target._response)
        self.assertIsNone(target._scenario)

    def test_definition_sparse(self):
        target = Pact(self.consumer, self.provider)
        (target
         .given('I am creating a new pact using the Pact class')
         .upon_receiving('a specific request to the server')
         .with_request('GET', '/path')
         .will_respond_with(200, body='success'))

        self.assertEqual(
            target._provider_state,
            'I am creating a new pact using the Pact class')

        self.assertEqual(
            target._description, 'a specific request to the server')

        self.assertEqual(target._request, {'path': '/path', 'method': 'GET'})
        self.assertEqual(target._response, {'status': 200, 'body': 'success'})

    def test_definition_all_options(self):
        target = Pact(self.consumer, self.provider)
        (target
         .given('I am creating a new pact using the Pact class')
         .upon_receiving('a specific request to the server')
         .with_request('GET', '/path',
                       body={'key': 'value'},
                       headers={'Accept': 'application/json'},
                       query={'search': 'test'})
         .will_respond_with(
             200,
             body='success', headers={'Content-Type': 'application/json'}))

        self.assertEqual(
            target._provider_state,
            'I am creating a new pact using the Pact class')

        self.assertEqual(
            target._description, 'a specific request to the server')

        self.assertEqual(target._request, {
            'path': '/path',
            'method': 'GET',
            'body': {'key': 'value'},
            'headers': {'Accept': 'application/json'},
            'query': {'search': 'test'}})
        self.assertEqual(target._response, {
            'status': 200,
            'body': 'success',
            'headers': {'Content-Type': 'application/json'}})


class PactSetupTestCase(PactTestCase):
    def setUp(self):
        super(PactSetupTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_requests = patch('requests.api.request').start()
        self.target = Pact(self.consumer, self.provider)
        (self.target
         .given('I am creating a new pact using the Pact class')
         .upon_receiving('a specific request to the server')
         .with_request('GET', '/path')
         .will_respond_with(200, body='success'))

        self.delete_call = call('delete', 'http://localhost:1234/interactions',
                                headers={'X-Pact-Mock-Service': 'true'})

        self.post_interactions_call = call(
            'post', 'http://localhost:1234/interactions',
            data=None,
            headers={'X-Pact-Mock-Service': 'true'},
            json={
                'response': {'status': 200, 'body': 'success'},
                'request': {'path': '/path', 'method': 'GET'},
                'description': 'a specific request to the server',
                'provider_state': 'I am creating a new pact using the '
                                  'Pact class'})

    def test_error_deleting_interactions(self):
        self.mock_requests.side_effect = iter([
            Mock(status_code=500, content='deletion error')])

        with self.assertRaises(AssertionError) as e:
            self.target.setup()

        self.assertEqual(str(e.exception), 'deletion error')
        self.assertEqual(self.mock_requests.call_count, 1)
        self.mock_requests.assert_has_calls([self.delete_call])

    def test_error_posting_interactions(self):
        self.mock_requests.side_effect = iter([
            Mock(status_code=200),
            Mock(status_code=500, content='post interactions error')])

        with self.assertRaises(AssertionError) as e:
            self.target.setup()

        self.assertEqual(str(e.exception), 'post interactions error')
        self.assertEqual(self.mock_requests.call_count, 2)
        self.mock_requests.assert_has_calls(
            [self.delete_call, self.post_interactions_call])

    def test_successful(self):
        self.mock_requests.side_effect = iter([Mock(status_code=200)] * 4)
        self.target.setup()

        self.assertEqual(self.mock_requests.call_count, 2)
        self.mock_requests.assert_has_calls([
            self.delete_call, self.post_interactions_call])


class PactStartShutdownServerTestCase(TestCase):
    def setUp(self):
        super(PactStartShutdownServerTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_Popen = patch.object(pact, 'Popen', autospec=True).start()
        self.mock_Popen.return_value.returncode = 0

    def test_start_fails(self):
        self.mock_Popen.return_value.returncode = 1
        pact = Pact(Consumer('consumer'), Provider('provider'),
                    log_dir='/logs', pact_dir='/pacts')

        with self.assertRaises(RuntimeError):
            pact.start_service()

        self.mock_Popen.assert_called_once_with([
            MOCK_SERVICE_PATH, 'start',
            '--host=localhost',
            '--port=1234',
            '--log', '/logs/pact-mock-service.log',
            '--pact-dir', '/pacts',
            '--pact-specification-version=2.0.0',
            '--consumer', 'consumer',
            '--provider', 'provider'])

        self.mock_Popen.return_value.communicate.assert_called_once_with()

    def test_start_no_ssl(self):
        pact = Pact(Consumer('consumer'), Provider('provider'),
                    log_dir='/logs', pact_dir='/pacts')
        pact.start_service()

        self.mock_Popen.assert_called_once_with([
            MOCK_SERVICE_PATH, 'start',
            '--host=localhost',
            '--port=1234',
            '--log', '/logs/pact-mock-service.log',
            '--pact-dir', '/pacts',
            '--pact-specification-version=2.0.0',
            '--consumer', 'consumer',
            '--provider', 'provider'])

        self.mock_Popen.return_value.communicate.assert_called_once_with()

    def test_start_with_ssl(self):
        pact = Pact(Consumer('consumer'), Provider('provider'),
                    log_dir='/logs', pact_dir='/pacts',
                    ssl=True, sslcert='/ssl.cert', sslkey='/ssl.key')
        pact.start_service()

        self.mock_Popen.assert_called_once_with([
            MOCK_SERVICE_PATH, 'start',
            '--host=localhost',
            '--port=1234',
            '--log', '/logs/pact-mock-service.log',
            '--pact-dir', '/pacts',
            '--pact-specification-version=2.0.0',
            '--consumer', 'consumer',
            '--provider', 'provider',
            '--ssl',
            '--sslcert', '/ssl.cert',
            '--sslkey', '/ssl.key'])

        self.mock_Popen.return_value.communicate.assert_called_once_with()

    def test_stop(self):
        pact = Pact(Consumer('consumer'), Provider('provider'))
        pact.stop_service()

        self.mock_Popen.assert_called_once_with(
            [MOCK_SERVICE_PATH, 'stop', '--port=1234'])
        self.mock_Popen.return_value.communicate.assert_called_once_with()

    def test_stop_fails(self):
        self.mock_Popen.return_value.returncode = 1
        pact = Pact(Consumer('consumer'), Provider('provider'))
        with self.assertRaises(RuntimeError):
            pact.stop_service()

        self.mock_Popen.assert_called_once_with(
            [MOCK_SERVICE_PATH, 'stop', '--port=1234'])
        self.mock_Popen.return_value.communicate.assert_called_once_with()


class PactVerifyTestCase(PactTestCase):
    def setUp(self):
        super(PactVerifyTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_requests = patch('requests.api.request').start()
        self.target = Pact(self.consumer, self.provider)
        (self.target
         .given('I am creating a new pact using the Pact class')
         .upon_receiving('a specific request to the server')
         .with_request('GET', '/path')
         .will_respond_with(200, body='success'))
        self.get_verification_call = call(
            'get', 'http://localhost:1234/interactions/verification',
            allow_redirects=True,
            headers={'X-Pact-Mock-Service': 'true'},
            params=None)

        self.post_publish_pacts_call = call(
            'post', 'http://localhost:1234/pact',
            data=None,
            headers={'X-Pact-Mock-Service': 'true'},
            json={'pact_dir': os.getcwd(),
                  'consumer': {'name': 'TestConsumer'},
                  'provider': {'name': 'TestProvider'}})

    def test_success(self):
        self.mock_requests.side_effect = iter([Mock(status_code=200)] * 2)
        self.target.verify()

        self.assertEqual(self.mock_requests.call_count, 2)
        self.mock_requests.assert_has_calls([
            self.get_verification_call, self.post_publish_pacts_call])

    def test_error_verifying_interactions(self):
        self.mock_requests.side_effect = iter([
            Mock(status_code=500, content='verification error')])

        with self.assertRaises(AssertionError) as e:
            self.target.verify()

        self.assertEqual(str(e.exception), 'verification error')
        self.assertEqual(self.mock_requests.call_count, 1)
        self.mock_requests.assert_has_calls([
            self.get_verification_call])

    def test_error_writing_pacts_to_file(self):
        self.mock_requests.side_effect = iter([
            Mock(status_code=200),
            Mock(status_code=500, content='error writing pact to file')])

        with self.assertRaises(AssertionError) as e:
            self.target.verify()

        self.assertEqual(str(e.exception), 'error writing pact to file')
        self.assertEqual(self.mock_requests.call_count, 2)
        self.mock_requests.assert_has_calls([
            self.get_verification_call, self.post_publish_pacts_call])


class PactContextManagerTestCase(PactTestCase):
    def setUp(self):
        super(PactContextManagerTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_setup = patch.object(
            pact.Pact, 'setup', autospec=True).start()

        self.mock_verify = patch.object(
            pact.Pact, 'verify', autospec=True).start()

    def test_successful(self):
        pact = Pact(self.consumer, self.provider)
        with pact:
            pass

        self.mock_setup.assert_called_once_with(pact)
        self.mock_verify.assert_called_once_with(pact)

    def test_context_raises_error(self):
        pact = Pact(self.consumer, self.provider)
        with self.assertRaises(RuntimeError):
            with pact:
                raise RuntimeError

        self.mock_setup.assert_called_once_with(pact)
        self.assertFalse(self.mock_verify.called)


class FromTermsTestCase(TestCase):
    def test_json(self):
        with self.assertRaises(NotImplementedError):
            FromTerms().json()


class RequestTestCase(TestCase):
    def test_sparse(self):
        target = Request('GET', '/path')
        result = target.json()
        self.assertEqual(result, {
            'method': 'GET',
            'path': '/path'})

    def test_all_options(self):
        target = Request(
            'POST', '/path',
            body='the content',
            headers={'Accept': 'application/json'},
            query='term=test')

        result = target.json()
        self.assertEqual(result, {
            'method': 'POST',
            'path': '/path',
            'body': 'the content',
            'headers': {'Accept': 'application/json'},
            'query': 'term=test'})


class ResponseTestCase(TestCase):
    def test_sparse(self):
        target = Response(200)
        result = target.json()
        self.assertEqual(result, {'status': 200})

    def test_all_options(self):
        target = Response(
            202, headers={'Content-Type': 'application/json'}, body='the body')

        result = target.json()
        self.assertEqual(result, {
            'status': 202,
            'body': 'the body',
            'headers': {'Content-Type': 'application/json'}})
