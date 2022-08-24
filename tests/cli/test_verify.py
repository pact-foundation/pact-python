import os
from unittest import TestCase

from click.testing import CliRunner
from mock import patch

from pact.cli import verify

from subprocess import PIPE, Popen


class mainTestCase(TestCase):
    """ use traceback.print_exception(*result.exc_info) to debug """

    @classmethod
    def setUpClass(cls):
        # In Python 3 Click makes a call to locale to determine how the
        # terminal wants to handle unicode. Because we mock Popen to avoid
        # calling the real verifier, we need to get the actual result of
        # locale to provide it to Click during the test run.
        if os.name == 'nt':
            cls.locale = ''  # pragma: no cover
        else:
            cls.locale = Popen(
                ['locale', '-a'], stdout=PIPE, stderr=PIPE).communicate()[0]

    def setUp(self):
        super(mainTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.runner = CliRunner()

        self.simple_pact_opts = [
            './pacts/consumer-provider.json',
            './pacts/consumer-provider2.json',
            '--provider=provider',
            '--provider-base-url=http://localhost']

        self.all_url_opts = [
            './pacts/consumer-provider.json',
            './pacts/consumer-provider2.json',
            '--provider-base-url=http://localhost',
            '--pact-url=./pacts/consumer-provider3.json',
            '--pact-urls=./pacts/consumer-provider4.json',
            '--provider=provider',
            '--timeout=30',
            '--verbose'
        ]

        self.simple_verify_call = [
            './pacts/consumer-provider.json',
            './pacts/consumer-provider2.json'
        ]

        self.all_verify_call = [
            './pacts/consumer-provider.json',
            './pacts/consumer-provider2.json',
            './pacts/consumer-provider3.json',
            './pacts/consumer-provider4.json'
        ]

    def assertVerifyCalled(self, mock_wrapper, *expected, **e2):
        self.assertEqual(mock_wrapper.call_count, 1)

        mock_wrapper.assert_called_once_with(*expected, **e2)

    def test_provider_base_url_is_required(self):
        result = self.runner.invoke(verify.main, [])

        self.assertEqual(result.exit_code, 2)
        self.assertIn('--provider-base-url', result.output)

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    def test_pact_urls_or_broker_are_required(self, mock_wrapper):
        result = self.runner.invoke(
            verify.main, ['--provider-base-url=http://localhost'])

        self.assertEqual(result.exit_code, 1)
        self.assertIn('at least one', result.output)
        mock_wrapper.assert_not_called()

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    def test_broker_url_but_no_provider_required(self, mock_wrapper):
        result = self.runner.invoke(
            verify.main, ['--provider-base-url=http://localhost',
                          '--pact-broker-url=http://broker'])

        mock_wrapper.assert_not_called()
        self.assertEqual(result.exit_code, 1)

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    @patch("pact.verify_wrapper.isfile", return_value=True)
    def test_wrapper_error_code_returned(self, mock_isfile, mock_wrapper):
        mock_wrapper.return_value = 8, None  # rnd number to indicate retval returned

        result = self.runner.invoke(verify.main, self.all_url_opts)

        self.assertFalse(mock_wrapper.call_verify.called)
        self.assertEqual(result.exit_code, 8)

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    @patch("pact.verify_wrapper.isfile", return_value=True)
    def test_successful_verification(self, mock_isfile, mock_wrapper):
        mock_wrapper.return_value = 0, None  # rnd number to indicate retval returned

        result = self.runner.invoke(verify.main, self.all_url_opts)

        self.assertEqual(result.exit_code, 0)
        self.assertVerifyCalled(mock_wrapper,
                                *self.all_verify_call,
                                provider='provider',
                                provider_base_url='http://localhost',
                                timeout=30,
                                verbose=True,
                                enable_pending=False,
                                publish_verification_results=False,
                                include_wip_pacts_since=None)

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    @patch("pact.verify_wrapper.isfile", return_value=True)
    def test_broker_url_and_provider_required(self, mock_isfile, mock_wrapper):
        mock_wrapper.return_value = 0, None

        result = self.runner.invoke(verify.main, self.all_url_opts)

        mock_wrapper.assert_called()
        self.assertEqual(result.exit_code, 0)

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    @patch("pact.verify_wrapper.isfile", return_value=True)
    def test_pact_url_param_supported(self, mock_isfile, mock_wrapper):
        mock_wrapper.return_value = 0, None
        result = self.runner.invoke(
            verify.main, ['--provider-base-url=http://localhost',
                          '--provider=provider',
                          '--pact-url=./pacts/consumer-provider.json',
                          '--pact-url=./pacts/consumer-provider2.json'])

        mock_wrapper.assert_called_with('./pacts/consumer-provider.json',
                                        './pacts/consumer-provider2.json',
                                        provider='provider',
                                        provider_base_url='http://localhost',
                                        timeout=30,
                                        verbose=False,
                                        enable_pending=False,
                                        publish_verification_results=False,
                                        include_wip_pacts_since=None)
        self.assertEqual(result.exit_code, 0)

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    @patch("pact.verify_wrapper.isfile", return_value=True)
    def test_pact_urls_param_supported(self, mock_isfile, mock_wrapper):
        mock_wrapper.return_value = 0, None
        result = self.runner.invoke(verify.main, [
            '--provider-base-url=http://localhost',
            '--provider=provider',
            '--pact-urls=./pacts/consumer-provider.json',
            '--pact-urls=./pacts/consumer-provider2.json'
        ])

        self.assertEqual(result.exit_code, 0)

        mock_wrapper.assert_called_with(*self.simple_verify_call,
                                        provider='provider',
                                        provider_base_url='http://localhost',
                                        timeout=30,
                                        verbose=False,
                                        enable_pending=False,
                                        publish_verification_results=False,
                                        include_wip_pacts_since=None)
        self.assertEqual(result.exit_code, 0)

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    @patch("pact.verify_wrapper.isfile", return_value=False)
    def test_local_pact_urls_must_exist(self, mock_isfile, mock_wrapper):
        mock_wrapper.return_value = 0, None

        result = self.runner.invoke(verify.main, self.all_url_opts)
        self.assertEqual(result.exit_code, 1)
        self.assertIn('./pacts/consumer-provider.json', result.output)
        mock_wrapper.call_verify.assert_not_called

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    @patch("pact.verify_wrapper.isfile", return_value=True)
    def test_failed_verification(self, mock_isfile, mock_wrapper):
        mock_wrapper.return_value = 3, None
        result = self.runner.invoke(verify.main, self.simple_pact_opts)

        self.assertEqual(result.exit_code, 3)
        mock_wrapper.assert_called_with(*self.simple_verify_call,
                                        provider='provider',
                                        provider_base_url='http://localhost',
                                        timeout=30,
                                        verbose=False,
                                        enable_pending=False,
                                        publish_verification_results=False,
                                        include_wip_pacts_since=None)

    @patch.dict(os.environ, {'PACT_BROKER_PASSWORD': 'pwd',
                             'PACT_BROKER_USERNAME': 'broker_user',
                             'PACT_BROKER_BASE_URL': 'http://broker/'})
    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    @patch("pact.verify_wrapper.isfile", return_value=True)
    def test_broker_creds_from_env_var(self, mock_isfile, mock_wrapper):
        mock_wrapper.return_value = 0, None

        result = self.runner.invoke(verify.main, self.simple_pact_opts)

        self.assertEqual(result.exit_code, 0)
        # self.assertVerifyCalled(mock_wrapper, *self.default_call + ['--broker-password=pwd'])
        self.assertVerifyCalled(mock_wrapper, *self.simple_verify_call,
                                provider='provider',
                                provider_base_url='http://localhost',
                                broker_password='pwd',
                                broker_username='broker_user',
                                broker_url='http://broker/',
                                timeout=30,
                                verbose=False,
                                enable_pending=False,
                                publish_verification_results=False,
                                include_wip_pacts_since=None)

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    @patch("pact.verify_wrapper.isfile", return_value=True)
    def test_all_url_options(self, mock_isfile, mock_wrapper):
        mock_wrapper.return_value = 0, None
        result = self.runner.invoke(verify.main, [
            './pacts/consumer-provider5.json',
            '--provider-base-url=http://localhost',
            '--pact-urls=./pacts/consumer-provider.json,'
            './pacts/consumer-provider2.json',
            '--pact-url=./pacts/consumer-provider3.json',
            '--pact-url=./pacts/consumer-provider4.json',
            '--custom-provider-header=Authorization: Basic cGFj',
            '--custom-provider-header=CustomHeader: somevalue',
            '--provider-states-setup-url=http://localhost/provider-states/set',
            '--pact-broker-username=user',
            '--pact-broker-password=pass',
            '--pact-broker-token=token',
            '--pact-broker-url=http://localhost/docker',
            '--provider=provider',
            '--provider-app-version=1.2.3',
            '--log-dir=tmp/logs/pact.test.log',
            '--log-level=INFO',
            '--timeout=60',
            '--verbose',
            '--enable-pending',
        ])
        self.assertEqual(result.exit_code, 0, result.output)

        self.assertEqual(mock_wrapper.call_count, 1)
        self.assertVerifyCalled(mock_wrapper, './pacts/consumer-provider5.json',
                                './pacts/consumer-provider3.json',
                                './pacts/consumer-provider4.json',
                                './pacts/consumer-provider.json',
                                './pacts/consumer-provider2.json',
                                provider='provider',
                                provider_base_url='http://localhost',
                                broker_password='pass',
                                broker_username='user',
                                broker_token='token',
                                broker_url='http://localhost/docker',
                                provider_app_version='1.2.3',
                                custom_provider_headers=['Authorization: Basic cGFj', 'CustomHeader: somevalue'],
                                provider_states_setup_url='http://localhost/provider-states/set',
                                log_dir='tmp/logs/pact.test.log',
                                log_level='INFO',
                                timeout=60,
                                verbose=True,
                                enable_pending=True,
                                publish_verification_results=False,
                                include_wip_pacts_since=None)

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    def test_all_broker_options(self, mock_wrapper):
        mock_wrapper.return_value = 0, None
        result = self.runner.invoke(verify.main, [
            '--pact-broker-url=http://localhost/broker',
            '--consumer-version-tag=prod',
            '--consumer-version-tag=dev',
            '--consumer-version-selector={"tag": "master", "latest": true}',
            '--consumer-version-selector={"tag": "staging", "latest": true}',
            '--provider-version-tag=dev',
            '--provider-version-tag=qa',
            '--provider-base-url=http://localhost',
            '--provider=provider',
            '--provider-states-setup-url=http://localhost/provider-states/set',
            '--pact-broker-username=user',
            '--pact-broker-password=pass',
            '--pact-broker-token=token',
            '--publish-verification-results',
            '--provider-app-version=1.2.3',
            '--timeout=60',
            '--publish-verification-results',
            '--verbose',
            '--enable-pending',
            '--include-wip-pacts-since=2018-01-01',
            '--provider-version-branch=provider-branch'
        ])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(mock_wrapper.call_count, 1)
        self.assertVerifyCalled(mock_wrapper,
                                provider='provider',
                                provider_base_url='http://localhost',
                                broker_password='pass',
                                broker_username='user',
                                broker_token='token',
                                broker_url='http://localhost/broker',
                                consumer_tags=['prod', 'dev'],
                                consumer_selectors=['{"tag": "master", "latest": true}',
                                                    '{"tag": "staging", "latest": true}'],
                                provider_tags=['dev', 'qa'],
                                provider_app_version='1.2.3',
                                publish_verification_results=True,
                                provider_states_setup_url='http://localhost/provider-states/set',
                                timeout=60,
                                verbose=True,
                                enable_pending=True,
                                include_wip_pacts_since='2018-01-01',
                                provider_version_branch='provider-branch')

    @patch("pact.verify_wrapper.isfile", return_value=True)
    def test_publishing_missing_version(self, mock_isfile):
        result = self.runner.invoke(verify.main, [
            '--pact-urls=./pacts/consumer-provider.json',
            '--provider-base-url=http://localhost',
            '--publish-verification-results'
        ])
        self.assertEqual(result.exit_code, 1)
        self.assertIn(
            'Provider application version is required', result.output)

    @patch('pact.cli.verify.path_exists', return_value=True)
    def test_file_does_not_exist_errors(self, mock_path_exists):
        mock_path_exists.return_value = False
        result = self.runner.invoke(verify.main, [
            '--pact-urls=./pacts/consumer-provider.json',
            '--provider-base-url=http://localhost',
            '--publish-verification-results'
        ])

        self.assertEqual(result.exit_code, 1)
        self.assertIn(
            'The following Pact files could not be found:', result.output)
        self.assertIn(
            './pacts/consumer-provider.json', result.output)
        mock_path_exists.assert_called_once_with(
            './pacts/consumer-provider.json')

    @patch('pact.cli.verify.path_exists', return_value=True)
    @patch('pact.cli.verify.expand_directories', return_value='./pacts/consumer-provider.json')
    def test_expand_directories_called(self, mock_expand_dirs, mock_path_exists):
        mock_expand_dirs.return_value = ['foo']

        self.runner.invoke(verify.main, [
            '--pact-urls=./pacts/consumer-provider.json',
            '--provider-base-url=http://localhost'
        ])

        mock_expand_dirs.assert_called_once()
        mock_path_exists.assert_called_once_with('foo')
