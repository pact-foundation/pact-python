from unittest import TestCase
import unittest
from mock import patch

from pact.verifier import Verifier
from pact.verify_wrapper import VerifyWrapper

PACT_FILE = 'test.pact'

class VerifierTestCase(TestCase):

    def setUp(self):
        super(VerifierTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.verifier = Verifier(provider='test_provider',
                                 provider_base_url="http://localhost:8888")

        self.mock_wrapper = patch.object(
            VerifyWrapper, 'call_verify', spec=True).start()

    @patch('pact.verifier.path_exists', return_value=True)
    @patch('pact.verifier.sanitize_logs')
    def test_verifier_with_provider_and_files(self, mock_sanitize_logs, mock_path_exists):
        self.mock_wrapper.return_value = (True, 'some logs')

        output, _ = self.verifier.verify_pacts('path/to/pact1',
                                               'path/to/pact2')

        self.assertTrue(output)
        self.assertEqual(self.mock_wrapper.call_count, 1)
        args, kwargs = self.mock_wrapper.call_args
        self.assertEquals('path/to/pact1', args[0])
        self.assertEquals('path/to/pact2', args[1])
        self.assertDictEqual({'provider': 'test_provider',
                              'provider_base_url': 'http://localhost:8888'},
                             kwargs)

    @patch('pact.verifier.sanitize_logs')
    def test_verifier_with_broker(self, mock_sanitize_logs):
        pact_broker_username = 'broker_username'
        pact_broker_password = 'broker_password'
        self.mock_wrapper.return_value = (True, 'ddf')

        output, _ = self.verifier.verify_with_broker(broker_username=pact_broker_username,
                                                     broker_password=pact_broker_password,
                                                     broker_url='http://broker')

        self.assertTrue(output)
        self.assertEqual(self.mock_wrapper.call_count, 1)
        args, kwargs = self.mock_wrapper.call_args

        self.assertEquals(len(args), 0)
        self.assertDictEqual({
            'provider': 'test_provider',
            'provider_base_url': 'http://localhost:8888',
            'broker_username': pact_broker_username,
            'broker_password': pact_broker_password,
            'broker_url': 'http://broker',
        },
            kwargs)

    @patch('pact.verifier.path_exists', return_value=False)
    def test_raises_error_on_missing_pact_files(self, mock_path_exists):
        self.assertRaises(Exception,
                          self.verifier.verify_pacts,
                          'path/to/pact1', 'path/to/pact2')

        mock_path_exists.assert_called_with(
            'path/to/pact2')

    def test_validate_on_publish_results(self):
        self.assertRaises(Exception, self.verifier.verify_pacts, 'path/to/pact1', publish=True)

    @patch('pact.verifier.path_exists', return_value=True)
    @patch('pact.verifier.sanitize_logs')
    @unittest.skip("demonstrating skipping")
    def test_publish_on_success(self, mock_path_exists, mock_sanitize_logs):
        self.mock_wrapper.return_value = (True, 'some logs')

        result = self.verifier.verify_pacts('path/to/pact1', publish=True, publish_version='1.0.0')
        print(result)  # todo

    @patch('pact.verifier.path_exists', return_value=True)
    @patch('pact.verifier.sanitize_logs')
    @patch('pact.verifier.expand_directories', return_value='./pacts/consumer-provider.json')
    def test_expand_directories_called(self, mock_expand_dirs, mock_sanitize_logs, mock_path_exists):
        self.mock_wrapper.return_value = (True, 'some logs')

        output, _ = self.verifier.verify_pacts('path/to/pact1',
                                               'path/to/pact2')

        mock_expand_dirs.assert_called_once()

    @patch('pact.verifier.path_exists', return_value=True)
    @patch('pact.verifier.sanitize_logs')
    @patch('pact.verifier.expand_directories', return_value='./pacts/consumer-provider.json')
    @patch('pact.verifier.rerun_command')
    @unittest.skip('should be in wrapper now')
    def test_rerun_command_called(self, mock_rerun_cmd, mock_expand_dirs, mock_sanitize_logs, mock_path_exists):
        self.mock_wrapper.return_value = (True, 'some logs')

        output, _ = self.verifier.verify_pacts('path/to/pact1',
                                               'path/to/pact2')

        mock_rerun_cmd.assert_called_once()
