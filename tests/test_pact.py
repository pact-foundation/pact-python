import os
from subprocess import Popen
from unittest import TestCase

from mock import patch, call, Mock
from psutil import Process

from pact.consumer import Consumer, Provider
from pact.matchers import Term
from pact.constants import MOCK_SERVICE_PATH, BROKER_CLIENT_PATH
from pact.pact import Pact, FromTerms, Request, Response
from pact import pact as pact


class PactTestCase(TestCase):
    def setUp(self):
        self.consumer = Consumer('TestConsumer')
        self.provider = Provider('TestProvider')

    def test_init_defaults(self):
        target = Pact(self.consumer, self.provider)
        self.assertIs(target.broker_base_url, None)
        self.assertIs(target.broker_username, None)
        self.assertIs(target.broker_password, None)
        self.assertIs(target.consumer, self.consumer)
        self.assertIs(target.cors, False)
        self.assertEqual(target.host_name, 'localhost')
        self.assertEqual(target.log_dir, os.getcwd())
        self.assertEqual(target.pact_dir, os.getcwd())
        self.assertEqual(target.port, 1234)
        self.assertIs(target.provider, self.provider)
        self.assertIs(target.publish_to_broker, False)
        self.assertIs(target.ssl, False)
        self.assertIsNone(target.sslcert)
        self.assertIsNone(target.sslkey)
        self.assertEqual(target.uri, 'http://localhost:1234')
        self.assertEqual(target.version, '2.0.0')
        self.assertEqual(len(target._interactions), 0)

    def test_init_custom_mock_service(self):
        target = Pact(
            self.consumer, self.provider, host_name='192.168.1.1', port=8000,
            log_dir='/logs', ssl=True, sslcert='/ssl.cert', sslkey='/ssl.pem',
            cors=True, pact_dir='/pacts', version='3.0.0',
            file_write_mode='merge')

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
        self.assertEqual(target.file_write_mode, 'merge')
        self.assertEqual(len(target._interactions), 0)

    def test_init_publish_to_broker(self):
        target = Pact(
            self.consumer, self.provider, publish_to_broker=True,
            broker_base_url='http://localhost', broker_username='username',
            broker_password='password', broker_token='token')

        self.assertEqual(target.broker_base_url, 'http://localhost')
        self.assertEqual(target.broker_username, 'username')
        self.assertEqual(target.broker_password, 'password')
        self.assertEqual(target.broker_token, 'token')
        self.assertIs(target.publish_to_broker, True)

    def test_definition_sparse(self):
        target = Pact(self.consumer, self.provider)
        (target
         .given('I am creating a new pact using the Pact class')
         .upon_receiving('a specific request to the server')
         .with_request('GET', '/path')
         .will_respond_with(200, body='success'))

        self.assertEqual(len(target._interactions), 1)

        self.assertEqual(
            target._interactions[0]['provider_state'],
            'I am creating a new pact using the Pact class')

        self.assertEqual(
            target._interactions[0]['description'],
            'a specific request to the server')

        self.assertEqual(target._interactions[0]['request'],
                         {'path': '/path', 'method': 'GET'})
        self.assertEqual(target._interactions[0]['response'],
                         {'status': 200, 'body': 'success'})

    def test_definition_without_given(self):
        target = Pact(self.consumer, self.provider)
        (target
            .upon_receiving('a specific request to the server')
            .with_request('GET', '/path')
            .will_respond_with(200, body='success'))

        self.assertEqual(len(target._interactions), 1)

        self.assertIsNone(
            target._interactions[0].get('provider_state'))

        self.assertEqual(
            target._interactions[0]['description'],
            'a specific request to the server')

        self.assertEqual(target._interactions[0]['request'],
                         {'path': '/path', 'method': 'GET'})
        self.assertEqual(target._interactions[0]['response'],
                         {'status': 200, 'body': 'success'})

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
            target._interactions[0]['provider_state'],
            'I am creating a new pact using the Pact class')

        self.assertEqual(
            target._interactions[0]['description'],
            'a specific request to the server')

        self.assertEqual(target._interactions[0]['request'], {
            'path': '/path',
            'method': 'GET',
            'body': {'key': 'value'},
            'headers': {'Accept': 'application/json'},
            'query': {'search': 'test'}})
        self.assertEqual(target._interactions[0]['response'], {
            'status': 200,
            'body': 'success',
            'headers': {'Content-Type': 'application/json'}})

    def test_definition_multiple_interactions(self):
        target = Pact(self.consumer, self.provider)
        (target
         .given('I am creating a new pact using the Pact class')
         .upon_receiving('a specific request to the server')
         .with_request('GET', '/foo')
         .will_respond_with(200, body='success')
         .given('I am creating another new pact using the Pact class')
         .upon_receiving('a different request to the server')
         .with_request('GET', '/bar')
         .will_respond_with(200, body='success'))

        self.assertEqual(len(target._interactions), 2)

        self.assertEqual(
            target._interactions[1]['provider_state'],
            'I am creating a new pact using the Pact class')
        self.assertEqual(
            target._interactions[0]['provider_state'],
            'I am creating another new pact using the Pact class')

        self.assertEqual(
            target._interactions[1]['description'],
            'a specific request to the server')
        self.assertEqual(
            target._interactions[0]['description'],
            'a different request to the server')

        self.assertEqual(target._interactions[1]['request'],
                         {'path': '/foo', 'method': 'GET'})
        self.assertEqual(target._interactions[0]['request'],
                         {'path': '/bar', 'method': 'GET'})

        self.assertEqual(target._interactions[1]['response'],
                         {'status': 200, 'body': 'success'})
        self.assertEqual(target._interactions[0]['response'],
                         {'status': 200, 'body': 'success'})

    def test_definition_multiple_interactions_without_given(self):
        target = Pact(self.consumer, self.provider)
        (target
         .upon_receiving('a specific request to the server')
         .with_request('GET', '/foo')
         .will_respond_with(200, body='success')
         .upon_receiving('a different request to the server')
         .with_request('GET', '/bar')
         .will_respond_with(200, body='success'))

        self.assertEqual(len(target._interactions), 2)

        self.assertIsNone(
            target._interactions[1].get('provider_state'))
        self.assertIsNone(
            target._interactions[0].get('provider_state'))

        self.assertEqual(
            target._interactions[1]['description'],
            'a specific request to the server')
        self.assertEqual(
            target._interactions[0]['description'],
            'a different request to the server')

        self.assertEqual(target._interactions[1]['request'],
                         {'path': '/foo', 'method': 'GET'})
        self.assertEqual(target._interactions[0]['request'],
                         {'path': '/bar', 'method': 'GET'})

        self.assertEqual(target._interactions[1]['response'],
                         {'status': 200, 'body': 'success'})
        self.assertEqual(target._interactions[0]['response'],
                         {'status': 200, 'body': 'success'})


class PactPublishTestCase(PactTestCase):
    def setUp(self):
        super(PactPublishTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_Popen = patch.object(pact, 'Popen', autospec=True).start()
        self.mock_Popen.return_value.returncode = 0
        self.mock_fnmatch = patch.object(
            pact.fnmatch, 'filter', autospec=True).start()
        self.mock_fnmatch.return_value = ['TestConsumer-TestProvider.json']
        self.mock_platform = patch.object(
            pact.platform, 'platform', autospec=True).start()

    def test_publish_fails(self):
        self.mock_Popen.return_value.returncode = 1
        pact = Pact(self.consumer, self.provider,
                    publish_to_broker=True,
                    broker_base_url="http://localhost")

        with self.assertRaises(RuntimeError):
            pact.publish()

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=0.0.0',
            '--broker-base-url=http://localhost',
            'TestConsumer-TestProvider.json'])

    def test_publish_without_broker_url(self):
        pact = Pact(self.consumer, self.provider, publish_to_broker=True)

        with self.assertRaises(RuntimeError):
            pact.publish()

    def text_publish_with_broker_url_environment_variable(self):
        pact = Pact(self.consumer, self.provider, publish_to_broker=True)
        os.environ["PACT_BROKER_BASE_URL"] = "http://localhost"

        pact.publish()
        del os.environ["PACT_BROKER_BASE_URL"]

    def test_default_publish(self):
        pact = Pact(self.consumer, self.provider,
                    publish_to_broker=True,
                    broker_base_url="http://localhost")

        pact.publish()

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=0.0.0',
            '--broker-base-url=http://localhost',
            'TestConsumer-TestProvider.json'])

    def test_basic_authenticated_publish(self):
        pact = Pact(self.consumer, self.provider,
                    publish_to_broker=True,
                    broker_base_url='http://localhost',
                    broker_username='username',
                    broker_password='password')

        pact.publish()

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=0.0.0',
            '--broker-base-url=http://localhost',
            '--broker-username=username',
            '--broker-password=password',
            'TestConsumer-TestProvider.json'])

    def test_token_authenticated_publish(self):
        pact = Pact(self.consumer, self.provider,
                    publish_to_broker=True,
                    broker_base_url='http://localhost',
                    broker_token='token')

        pact.publish()

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=0.0.0',
            '--broker-base-url=http://localhost',
            '--broker-token=token',
            'TestConsumer-TestProvider.json'])

    def test_git_tagged_publish(self):
        pact = Pact(Consumer('TestConsumer', tag_with_git_branch=True),
                    self.provider,
                    publish_to_broker=True,
                    broker_base_url='http://localhost')

        pact.publish()

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=0.0.0',
            '--broker-base-url=http://localhost',
            'TestConsumer-TestProvider.json',
            '--tag-with-git-branch'])

    def test_manual_tagged_publish(self):
        pact = Pact(Consumer('TestConsumer', tags=['tag1', 'tag2']),
                    self.provider,
                    publish_to_broker=True,
                    broker_base_url='http://localhost')

        pact.publish()

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=0.0.0',
            '--broker-base-url=http://localhost',
            'TestConsumer-TestProvider.json',
            '-t', 'tag1',
            '-t', 'tag2'])

    def test_versioned_publish(self):
        pact = Pact(Consumer('TestConsumer', version="1.0.0"),
                    self.provider,
                    publish_to_broker=True,
                    broker_base_url='http://localhost')

        pact.publish()

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=1.0.0',
            '--broker-base-url=http://localhost',
            'TestConsumer-TestProvider.json'])

    def test_publish_after_stop_service(self):
        self.mock_platform.return_value = 'Linux'
        pact = Pact(self.consumer, self.provider,
                    publish_to_broker=True, broker_base_url="http://localhost")
        mock_publish = patch.object(pact, 'publish', autospec=True).start()
        pact._process = Mock(spec=Popen, pid=999, returncode=0)

        pact.stop_service()

        mock_publish.assert_called_once_with()


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
                                headers={'X-Pact-Mock-Service': 'true'},
                                verify=False)

        self.put_interactions_call = call(
            'put', 'http://localhost:1234/interactions',
            data=None,
            headers={'X-Pact-Mock-Service': 'true'},
            verify=False,
            json={'interactions': [{
                'response': {'status': 200, 'body': 'success'},
                'request': {'path': '/path', 'method': 'GET'},
                'description': 'a specific request to the server',
                'provider_state': 'I am creating a new pact using the '
                                  'Pact class'}]})

    def test_error_deleting_interactions(self):
        self.mock_requests.side_effect = iter([
            Mock(status_code=500, text='deletion error')])

        with self.assertRaises(AssertionError) as e:
            self.target.setup()

        self.assertEqual(str(e.exception), 'deletion error')
        self.assertEqual(self.mock_requests.call_count, 1)
        self.mock_requests.assert_has_calls([self.delete_call])

    def test_error_posting_interactions(self):
        self.mock_requests.side_effect = iter([
            Mock(status_code=200),
            Mock(status_code=500, text='post interactions error')])

        with self.assertRaises(AssertionError) as e:
            self.target.setup()

        self.assertEqual(str(e.exception), 'post interactions error')
        self.assertEqual(self.mock_requests.call_count, 2)
        self.mock_requests.assert_has_calls(
            [self.delete_call, self.put_interactions_call])

    def test_successful(self):
        self.mock_requests.side_effect = iter([Mock(status_code=200)] * 4)
        self.target.setup()

        self.assertEqual(self.mock_requests.call_count, 2)
        self.mock_requests.assert_has_calls([
            self.delete_call, self.put_interactions_call])


class PactStartShutdownServerTestCase(TestCase):
    def setUp(self):
        super(PactStartShutdownServerTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_Popen = patch.object(pact, 'Popen', autospec=True).start()
        self.mock_Popen.return_value.returncode = 0
        self.mock_Process = patch.object(
            pact.psutil, 'Process', autospec=True).start()
        self.mock_platform = patch.object(
            pact.platform, 'platform', autospec=True).start()
        self.mock_wait_for_server_start = patch.object(
            pact.Pact, '_wait_for_server_start', autospec=True).start()
        self.mock_Pid_exists = patch.object(
            pact.psutil, 'pid_exists', autospec=True).start()

    def test_start_fails(self):
        self.mock_Popen.return_value.returncode = 1
        self.mock_wait_for_server_start.side_effect = RuntimeError
        pact = Pact(Consumer('consumer'), Provider('provider'),
                    log_dir='/logs', pact_dir='/pacts')

        with self.assertRaises(RuntimeError):
            pact.start_service()

        self.mock_Popen.assert_called_once_with([
            MOCK_SERVICE_PATH, 'service',
            '--host=localhost',
            '--port=1234',
            '--log', '/logs/pact-mock-service.log',
            '--pact-dir', '/pacts',
            '--pact-file-write-mode', 'overwrite',
            '--pact-specification-version=2.0.0',
            '--consumer', 'consumer',
            '--provider', 'provider'])

    def test_start_no_ssl(self):
        pact = Pact(Consumer('consumer'), Provider('provider'),
                    log_dir='/logs', pact_dir='/pacts')
        pact.start_service()

        self.mock_Popen.assert_called_once_with([
            MOCK_SERVICE_PATH, 'service',
            '--host=localhost',
            '--port=1234',
            '--log', '/logs/pact-mock-service.log',
            '--pact-dir', '/pacts',
            '--pact-file-write-mode', 'overwrite',
            '--pact-specification-version=2.0.0',
            '--consumer', 'consumer',
            '--provider', 'provider'])

    def test_start_with_ssl(self):
        pact = Pact(Consumer('consumer'), Provider('provider'),
                    log_dir='/logs', pact_dir='/pacts',
                    ssl=True, sslcert='/ssl.cert', sslkey='/ssl.key')
        pact.start_service()

        self.mock_Popen.assert_called_once_with([
            MOCK_SERVICE_PATH, 'service',
            '--host=localhost',
            '--port=1234',
            '--log', '/logs/pact-mock-service.log',
            '--pact-dir', '/pacts',
            '--pact-file-write-mode', 'overwrite',
            '--pact-specification-version=2.0.0',
            '--consumer', 'consumer',
            '--provider', 'provider',
            '--ssl',
            '--sslcert', '/ssl.cert',
            '--sslkey', '/ssl.key'])

    def test_stop_posix(self):
        self.mock_platform.return_value = 'Linux'
        pact = Pact(Consumer('consumer'), Provider('provider'))
        pact._process = Mock(spec=Popen, pid=999, returncode=0)
        pact.stop_service()

        pact._process.terminate.assert_called_once_with()
        pact._process.communicate.assert_called_once_with()
        self.assertFalse(self.mock_Process.called)

    def test_stop_windows(self):
        self.mock_platform.return_value = 'Windows'
        ruby_exe = Mock(spec=Process)
        self.mock_Process.return_value.children.return_value = [ruby_exe]
        self.mock_Pid_exists.return_value = False
        pact = Pact(Consumer('consumer'), Provider('provider'))
        pact._process = Mock(spec=Popen, pid=999)
        pact.stop_service()

        self.assertFalse(pact._process.terminate.called)
        self.assertFalse(pact._process.communicate.called)
        self.mock_Process.assert_called_once_with(999)
        self.mock_Process.return_value.children.assert_called_once_with(
            recursive=True)
        ruby_exe.terminate.assert_called_once_with()
        self.mock_Process.return_value.wait.assert_called_once_with()
        self.mock_Pid_exists.assert_called_once_with(999)

    def test_stop_fails_posix(self):
        self.mock_platform.return_value = 'Linux'
        self.mock_Popen.return_value.returncode = 1
        pact = Pact(Consumer('consumer'), Provider('provider'))
        pact._process = Mock(spec=Popen, pid=999, returncode=1)
        with self.assertRaises(RuntimeError):
            pact.stop_service()

        pact._process.terminate.assert_called_once_with()
        pact._process.communicate.assert_called_once_with()

    def test_stop_fails_windows(self):
        self.mock_platform.return_value = 'Windows'
        self.mock_Popen.return_value.returncode = 15
        self.mock_Pid_exists.return_value = True

        pact = Pact(Consumer('consumer'), Provider('provider'))
        pact._process = Mock(spec=Popen, pid=999, returncode=15)
        with self.assertRaises(RuntimeError):
            pact.stop_service()

        self.assertFalse(pact._process.terminate.called)
        self.assertFalse(pact._process.communicate.called)
        self.mock_Process.assert_called_once_with(999)
        self.mock_Process.return_value.children.assert_called_once_with(
            recursive=True)
        self.mock_Process.return_value.wait.assert_called_once_with()
        self.mock_Pid_exists.assert_called_once_with(999)


class PactWaitForServerStartTestCase(TestCase):
    def setUp(self):
        super(PactWaitForServerStartTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_HTTPAdapter = patch.object(
            pact, 'HTTPAdapter', autospec=True).start()
        self.mock_Retry = patch.object(pact, 'Retry', autospec=True).start()
        self.mock_Session = patch.object(
            pact.requests, 'Session', autospec=True).start()

    def test_wait_for_server_start_success(self):
        self.mock_Session.return_value.get.return_value.status_code = 200
        pact = Pact(Consumer('consumer'), Provider('provider'))
        pact._process = Mock(spec=Popen)
        pact._wait_for_server_start()

        session = self.mock_Session.return_value
        session.mount.assert_called_once_with(
            'http://', self.mock_HTTPAdapter.return_value)
        session.get.assert_called_once_with(
            'http://localhost:1234',
            headers={'X-Pact-Mock-Service': 'true'},
            allow_redirects=False,
            verify=False)
        self.mock_HTTPAdapter.assert_called_once_with(
            max_retries=self.mock_Retry.return_value)
        self.mock_Retry.assert_called_once_with(total=9, backoff_factor=0.1)
        self.assertFalse(pact._process.communicate.called)
        self.assertFalse(pact._process.terminate.called)

    def test_wait_for_server_start_failure(self):
        self.mock_Session.return_value.get.return_value.status_code = 500
        pact = Pact(Consumer('consumer'), Provider('provider'))
        pact._process = Mock(spec=Popen)
        with self.assertRaises(RuntimeError):
            pact._wait_for_server_start()

        session = self.mock_Session.return_value
        session.mount.assert_called_once_with(
            'http://', self.mock_HTTPAdapter.return_value)
        session.get.assert_called_once_with(
            'http://localhost:1234',
            headers={'X-Pact-Mock-Service': 'true'},
            allow_redirects=False,  # can cause problems in CI otherwise
            verify=False)
        self.mock_HTTPAdapter.assert_called_once_with(
            max_retries=self.mock_Retry.return_value)
        self.mock_Retry.assert_called_once_with(total=9, backoff_factor=0.1)
        pact._process.communicate.assert_called_once_with()
        pact._process.terminate.assert_called_once_with()


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
            verify=False,
            params=None)

        self.post_publish_pacts_call = call(
            'post', 'http://localhost:1234/pact',
            data=None,
            headers={'X-Pact-Mock-Service': 'true'},
            verify=False,
            json=None)

    def test_success(self):
        self.mock_requests.side_effect = iter([Mock(status_code=200)] * 2)
        self.target.verify()

        self.assertEqual(self.mock_requests.call_count, 2)
        self.mock_requests.assert_has_calls([
            self.get_verification_call, self.post_publish_pacts_call])

    def test_error_verifying_interactions(self):
        self.mock_requests.side_effect = iter([
            Mock(status_code=500, text='verification error')])

        with self.assertRaises(AssertionError) as e:
            self.target.verify()

        self.assertEqual(str(e.exception), 'verification error')
        self.assertEqual(self.mock_requests.call_count, 1)
        self.mock_requests.assert_has_calls([
            self.get_verification_call])

    def test_error_writing_pacts_to_file(self):
        self.mock_requests.side_effect = iter([
            Mock(status_code=200),
            Mock(status_code=500, text='error writing pact to file')])

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

    def test_falsey_body(self):
        target = Request('GET', '/path', body=[])
        result = target.json()
        self.assertEqual(result, {
            'method': 'GET',
            'path': '/path',
            'body': []})

    def test_matcher_in_path_gets_converted(self):
        target = Request('GET', Term('\/.+', '/test-path'))  # noqa: W605
        result = target.json()
        self.assertTrue(isinstance(result['path'], dict))


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

    def test_falsey_body(self):
        target = Response(200, body=[])
        result = target.json()
        self.assertEqual(result, {'status': 200, 'body': []})
