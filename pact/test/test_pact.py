from unittest import TestCase

from mock import patch, call, Mock

from .. import Consumer, Provider
from ..pact import Pact, FromTerms, Request, Response


class PactTestCase(TestCase):
    def setUp(self):
        self.consumer = Consumer('TestConsumer')
        self.provider = Provider('TestProvider')

    def test_init_defaults(self):
        target = Pact(self.consumer, self.provider)
        self.assertEqual(target.BASE_URI, 'http://localhost:1234')
        self.assertIs(target.consumer, self.consumer)
        self.assertIs(target.provider, self.provider)
        self.assertIsNone(target._description)
        self.assertIsNone(target._provider_state)
        self.assertIsNone(target._request)
        self.assertIsNone(target._response)
        self.assertIsNone(target._scenario)

    def test_init_custom_mock_service(self):
        target = Pact(
            self.consumer, self.provider, host_name='192.168.1.1', port=8000)

        self.assertEqual(target.BASE_URI, 'http://192.168.1.1:8000')
        self.assertIs(target.consumer, self.consumer)
        self.assertIs(target.provider, self.provider)
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


class PactContextManagerTestCase(TestCase):
    def setUp(self):
        super(PactContextManagerTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_requests = patch('requests.api.request').start()
        self.consumer = Consumer('TestConsumer')
        self.provider = Provider('TestProvider')
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

        self.get_verification_call = call(
            'get', 'http://localhost:1234/interactions/verification',
            allow_redirects=True,
            headers={'X-Pact-Mock-Service': 'true'},
            params=None)

        self.post_publish_pacts_call = call(
            'post', 'http://localhost:1234/pact',
            data=None,
            headers={'X-Pact-Mock-Service': 'true'},
            json={'pact_dir': '/opt/contracts',
                  'consumer': {'name': 'TestConsumer'},
                  'provider': {'name': 'TestProvider'}})

    def test_successful(self):
        self.mock_requests.side_effect = iter([Mock(status_code=200)] * 4)

        with self.target:
            pass

        self.assertEqual(self.mock_requests.call_count, 4)
        self.mock_requests.assert_has_calls([
            self.delete_call, self.post_interactions_call,
            self.get_verification_call, self.post_publish_pacts_call])

    def test_error_deleting_interactions(self):
        self.mock_requests.side_effect = iter([
            Mock(status_code=500, content='deletion error')])

        with self.assertRaises(AssertionError) as e:
            self.target.__enter__()

        self.assertEqual(str(e.exception), 'deletion error')
        self.assertEqual(self.mock_requests.call_count, 1)
        self.mock_requests.assert_has_calls([self.delete_call])

    def test_error_posting_interactions(self):
        self.mock_requests.side_effect = iter([
            Mock(status_code=200),
            Mock(status_code=500, content='post interactions error')])

        with self.assertRaises(AssertionError) as e:
            self.target.__enter__()

        self.assertEqual(str(e.exception), 'post interactions error')
        self.assertEqual(self.mock_requests.call_count, 2)
        self.mock_requests.assert_has_calls(
            [self.delete_call, self.post_interactions_call])

    def test_error_raised(self):
        self.mock_requests.side_effect = TypeError('type error')
        self.target.__exit__(TypeError, 'type error', Mock())
        self.assertFalse(self.mock_requests.called)

    def test_error_verifying_interactions(self):
        self.mock_requests.side_effect = iter([
            Mock(status_code=500, content='verification error')])

        with self.assertRaises(AssertionError) as e:
            self.target.__exit__(None, None, None)

        self.assertEqual(str(e.exception), 'verification error')
        self.assertEqual(self.mock_requests.call_count, 1)
        self.mock_requests.assert_has_calls([
            self.get_verification_call])

    def test_error_writing_pacts_to_file(self):
        self.mock_requests.side_effect = iter([
            Mock(status_code=200),
            Mock(status_code=500, content='error writing pact to file')])

        with self.assertRaises(AssertionError) as e:
            self.target.__exit__(None, None, None)

        self.assertEqual(str(e.exception), 'error writing pact to file')
        self.assertEqual(self.mock_requests.call_count, 2)
        self.mock_requests.assert_has_calls([
            self.get_verification_call, self.post_publish_pacts_call])


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
