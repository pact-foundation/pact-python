import os
import sys
from unittest import TestCase

from click.testing import CliRunner
from mock import patch

from .. import verify
from ..constants import VERIFIER_PATH

if sys.version_info.major == 2:
    from subprocess32 import PIPE, Popen, TimeoutExpired
else:
    from subprocess import PIPE, Popen, TimeoutExpired


class mainTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # In Python 3 Click makes a call to locale to determine how the
        # terminal wants to handle unicode. Because we mock Popen to avoid
        # calling the real verifier, we need to get the actual result of
        # locale to provide it to Click during the test run.
        cls.locale = Popen(
            ['locale', '-a'], stdout=PIPE, stderr=PIPE).communicate()[0]

    def setUp(self):
        super(mainTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_Popen = patch.object(
            verify.subprocess, 'Popen', spec=verify.subprocess.Popen).start()
        self.mock_Popen.return_value.communicate.return_value = self.locale

        self.mock_isfile = patch.object(
            verify, 'isfile', autospec=True).start()

        self.runner = CliRunner()
        self.default_call = [
            '--provider-base-url=http://localhost',
            '--pact-urls=./pacts/consumer-provider.json']

        self.default_opts = [
            '--provider-base-url=http://localhost',
            '--pact-urls=./pacts/consumer-provider.json']

    def assertProcess(self, *expected):
        self.assertEqual(self.mock_Popen.call_count, 1)
        actual = self.mock_Popen.mock_calls[0][1][0]
        self.assertEqual(actual[0], VERIFIER_PATH)
        self.assertEqual(len(set(actual)), len(expected) + 1)
        self.assertEqual(set(actual[1:]), set(expected))

    def test_provider_base_url_is_required(self):
        result = self.runner.invoke(verify.main, [])
        self.assertEqual(result.exit_code, 2)
        self.assertIn(b'--provider-base-url', result.output_bytes)
        self.assertFalse(self.mock_Popen.called)

    def test_pact_urls_are_required(self):
        result = self.runner.invoke(
            verify.main, ['--provider-base-url=http://localhost'])
        self.assertEqual(result.exit_code, 2)
        self.assertIn(b'--pact-urls', result.output_bytes)
        self.assertFalse(self.mock_Popen.called)

    def test_local_pact_urls_must_exist(self):
        self.mock_isfile.return_value = False
        result = self.runner.invoke(verify.main, self.default_opts)
        self.assertEqual(result.exit_code, 1)
        self.assertIn(b'./pacts/consumer-provider.json', result.output_bytes)
        self.assertFalse(self.mock_Popen.called)

    def test_must_provide_both_provide_states_options(self):
        result = self.runner.invoke(verify.main, [
            '--provider-base-url=http://localhost',
            '--pact-urls=./pacts/consumer-provider.json',
            '--provider-states-url=http://localhost/provider-state'
        ])
        self.assertEqual(result.exit_code, 1)
        self.assertIn(b'--provider-states-url', result.output_bytes)
        self.assertIn(b'--provider-states-setup-url', result.output_bytes)
        self.assertFalse(self.mock_Popen.called)

    def test_verification_timeout(self):
        self.mock_Popen.return_value.communicate.side_effect = TimeoutExpired(
            [], 30)

        result = self.runner.invoke(verify.main, self.default_opts)
        self.assertEqual(result.exit_code, -1)
        self.assertIsInstance(result.exception, TimeoutExpired)
        self.assertProcess(*self.default_call)
        self.mock_Popen.return_value.communicate.assert_called_once_with(
            timeout=30)

    def test_failed_verification(self):
        self.mock_Popen.return_value.returncode = 3
        result = self.runner.invoke(verify.main, self.default_opts)
        self.assertEqual(result.exit_code, 3)
        self.assertProcess(*self.default_call)
        self.mock_Popen.return_value.communicate.assert_called_once_with(
            timeout=30)

    def test_successful_verification(self):
        self.mock_Popen.return_value.returncode = 0
        result = self.runner.invoke(verify.main, self.default_opts)
        self.assertEqual(result.exit_code, 0)
        self.assertProcess(*self.default_call)
        self.mock_Popen.return_value.communicate.assert_called_once_with(
            timeout=30)

    @patch.dict(os.environ, {'PACT_BROKER_PASSWORD': 'pwd'})
    def test_password_from_env_var(self):
        self.mock_Popen.return_value.returncode = 0
        result = self.runner.invoke(verify.main, self.default_opts)
        self.assertEqual(result.exit_code, 0)
        self.assertProcess(*self.default_call + ['--pact-broker-password=pwd'])
        self.mock_Popen.return_value.communicate.assert_called_once_with(
            timeout=30)

    def test_all_options(self):
        self.mock_Popen.return_value.returncode = 0
        result = self.runner.invoke(verify.main, [
            '--provider-base-url=http://localhost',
            '--pact-urls=./pacts/consumer-provider.json',
            '--provider-states-url=http=//localhost/provider-states',
            '--provider-states-setup-url=http://localhost/provider-states/set',
            '--pact-broker-username=user',
            '--pact-broker-password=pass',
            '--timeout=60'
        ])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.mock_Popen.call_count, 1)
        self.assertProcess(
            '--provider-base-url=http://localhost',
            '--pact-urls=./pacts/consumer-provider.json',
            '--provider-states-url=http=//localhost/provider-states',
            '--provider-states-setup-url=http://localhost/provider-states/set',
            '--pact-broker-username=user',
            '--pact-broker-password=pass')
        self.mock_Popen.return_value.communicate.assert_called_once_with(
            timeout=60)


class path_existsTestCase(TestCase):
    def setUp(self):
        super(path_existsTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_isfile = patch.object(
            verify, 'isfile', autospec=True).start()

    def test_http(self):
        result = verify.path_exists('http://localhost')
        self.assertIs(result, True)
        self.assertFalse(self.mock_isfile.called)

    def test_https(self):
        result = verify.path_exists('https://example.com')
        self.assertIs(result, True)
        self.assertFalse(self.mock_isfile.called)

    def test_file_does_exist(self):
        self.mock_isfile.return_value = True
        result = verify.path_exists('./pacts/consumer-provider.json')
        self.assertIs(result, True)
        self.mock_isfile.assert_called_once_with(
            './pacts/consumer-provider.json')

    def test_file_does_not_exist(self):
        self.mock_isfile.return_value = False
        result = verify.path_exists('./pacts/consumer-provider.json')
        self.assertIs(result, False)
        self.mock_isfile.assert_called_once_with(
            './pacts/consumer-provider.json')
