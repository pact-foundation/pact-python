import os
from mock import patch, Mock
from unittest import TestCase
from pathlib import Path

from pact.message_provider import MessageProvider
from pact import message_provider as message_provider

class MessageProviderTestCase(TestCase):
    def _mock_response(
            self,
            status=200,
            content="fake response",
            raise_for_status=None):

        mock_resp = Mock()
        mock_resp.raise_for_status = Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status

        mock_resp.status_code = status
        mock_resp.text = content
        return mock_resp

    def message_handler(self):
        return {'success': True}

    def setUp(self):
        self.provider = MessageProvider(
            provider='DocumentService',
            consumer='DetectContentLambda',
            message_providers={
                'a document created successfully': self.message_handler
            }
        )

    def test_init(self):
        self.assertIsInstance(self.provider, MessageProvider)
        self.assertEqual(self.provider.provider, 'DocumentService')
        self.assertEqual(self.provider.consumer, 'DetectContentLambda')
        self.assertEqual(self.provider.pact_dir, os.getcwd())
        self.assertEqual(self.provider.version, '3.0.0')
        self.assertEqual(self.provider.proxy_host, 'localhost')
        self.assertEqual(self.provider.proxy_port, '5000')

    @patch('pact.Verifier.verify_pacts', return_value=(0, 'logs'))
    def test_verify(self, mock_verify_pacts):
        self.provider.verify()

        assert mock_verify_pacts.call_count == 1
        mock_verify_pacts.assert_called_with(f'{self.provider.pact_dir}/{self.provider._pact_file()}', verbose=False)

class MessageProviderContextManagerTestCase(MessageProviderTestCase):
    def setUp(self):
        super(MessageProviderContextManagerTestCase, self).setUp()

    @patch('pact.MessageProvider._start_proxy', return_value=0)
    @patch('pact.MessageProvider._stop_proxy', return_value=0)
    def test_successful(self, mock_start_proxy, mock_stop_proxy):
        with self.provider:
            pass

        mock_start_proxy.assert_called_once()
        mock_stop_proxy.assert_called_once()

    @patch('pact.MessageProvider._wait_for_server_start', side_effect=RuntimeError('boom!'))
    @patch('pact.MessageProvider._start_proxy', return_value=0)
    @patch('pact.MessageProvider._stop_proxy', return_value=0)
    def test_stop_proxy_on_runtime_error(self, mock_stop_proxy, mock_start_proxy, mock_wait_for_server_start,):
        with self.provider:
            pass

        mock_start_proxy.assert_called_once()
        mock_stop_proxy.assert_called_once()

class StartProxyTestCase(MessageProviderTestCase):
    def setUp(self):
        super(StartProxyTestCase, self).setUp()
    @patch.object(Path, 'exists', return_value=True)
    @patch('pact.MessageProvider._setup_states')
    @patch('pact.MessageProvider._wait_for_server_start')
    @patch.object(message_provider, 'Popen')
    def test_start_proxy_successfully(self, mock_popen, mock_wait_for_server_start, mock_setup_states, mock_path_exist):
        self.provider._start_proxy()

        mock_wait_for_server_start.assert_called_once()
        mock_setup_states.assert_called_once()
        mock_popen.assert_called_once()

    @patch.object(Path, 'exists', return_value=False)
    @patch('pact.MessageProvider._setup_states')
    @patch('pact.MessageProvider._wait_for_server_start')
    @patch.object(message_provider, 'Popen')
    def test_pact_files_do_not_exist(self, mock_popen, mock_wait_for_server_start, mock_setup_states, mock_path_exist):
        with self.assertRaises(FileNotFoundError):
            self.provider._start_proxy()

        mock_wait_for_server_start.assert_not_called()
        mock_setup_states.assert_not_called()
        mock_popen.assert_not_called()

class StopProxyTestCase(MessageProviderTestCase):
    def setUp(self):
        super(StopProxyTestCase, self).setUp()

    @patch('requests.post')
    def test_shutdown_successfully(self, mock_requests):
        mock_requests.return_value = self._mock_response(content="success")
        self.provider._stop_proxy()
        mock_requests.assert_called_once_with('http://localhost:5000/shutdown', verify=False)

class SetupStateTestCase(MessageProviderTestCase):
    def setUp(self):
        super(SetupStateTestCase, self).setUp()

    @patch('requests.post')
    def test_shutdown_successfully(self, mock_requests):
        mock_requests.return_value = self._mock_response(status=201)
        self.provider._setup_states()
        expected_payload = {
            'messageHandlers': {
                'a document created successfully': self.message_handler()
            }
        }
        mock_requests.assert_called_once_with('http://localhost:5000/setup', verify=False, json=expected_payload)

class WaitForServerStartTestCase(MessageProviderTestCase):
    def setUp(self):
        super(WaitForServerStartTestCase, self).setUp()

    @patch.object(message_provider.requests, 'Session')
    @patch.object(message_provider, 'Retry')
    @patch.object(message_provider, 'HTTPAdapter')
    @patch('pact.MessageProvider._stop_proxy')
    def test_wait_for_server_start_success(self, mock_stop_proxy, mock_HTTPAdapter, mock_Retry, mock_Session):
        mock_Session.return_value.get.return_value.status_code = 200
        self.provider._wait_for_server_start()

        session = mock_Session.return_value
        session.mount.assert_called_once_with(
            'http://', mock_HTTPAdapter.return_value)
        session.get.assert_called_once_with(f'{self.provider._proxy_url()}/health', verify=False)
        mock_HTTPAdapter.assert_called_once_with(
            max_retries=mock_Retry.return_value)
        mock_Retry.assert_called_once_with(total=9, backoff_factor=0.5)
        mock_stop_proxy.assert_not_called()

    @patch.object(message_provider.requests, 'Session')
    @patch.object(message_provider, 'Retry')
    @patch.object(message_provider, 'HTTPAdapter')
    @patch('pact.MessageProvider._stop_proxy')
    def test_wait_for_server_start_failure(self, mock_stop_proxy, mock_HTTPAdapter, mock_Retry, mock_Session):
        mock_Session.return_value.get.return_value.status_code = 500

        with self.assertRaises(RuntimeError):
            self.provider._wait_for_server_start()

        session = mock_Session.return_value
        session.mount.assert_called_once_with(
            'http://', mock_HTTPAdapter.return_value)
        session.get.assert_called_once_with(f'{self.provider._proxy_url()}/health', verify=False)
        mock_HTTPAdapter.assert_called_once_with(
            max_retries=mock_Retry.return_value)
        mock_Retry.assert_called_once_with(total=9, backoff_factor=0.5)
        mock_stop_proxy.assert_called_once()
