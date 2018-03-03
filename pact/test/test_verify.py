import os
import sys
from unittest import TestCase

from click.testing import CliRunner
from mock import patch, Mock, call

from .. import verify
from ..constants import VERIFIER_PATH

if sys.version_info.major == 2:
    from subprocess32 import PIPE, Popen
else:
    from subprocess import PIPE, Popen


class mainTestCase(TestCase):
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
        self.mock_Popen = patch.object(
            verify.subprocess, 'Popen', spec=verify.subprocess.Popen,
            stdout=['6 interactions, 0 failures']).start()

        self.mock_Popen.return_value.communicate.return_value = self.locale

        self.mock_isfile = patch.object(
            verify, 'isfile', autospec=True).start()

        self.mock_rerun_command = patch.object(
            verify, 'rerun_command', autospec=True).start()

        self.runner = CliRunner()
        self.default_call = [
            './pacts/consumer-provider.json',
            './pacts/consumer-provider2.json',
            './pacts/consumer-provider3.json',
            '--provider-base-url=http://localhost']

        self.default_opts = [
            '--provider-base-url=http://localhost',
            '--pact-url=./pacts/consumer-provider.json',
            '--pact-urls=./pacts/consumer-provider2.json,'
            './pacts/consumer-provider3.json']

    def assertProcess(self, *expected):
        self.assertEqual(self.mock_Popen.call_count, 1)
        call = self.mock_Popen.mock_calls[0]
        actual = call[1][0]
        self.assertEqual(actual[0], VERIFIER_PATH)
        self.assertEqual(len(set(actual)), len(expected) + 1)
        self.assertEqual(set(actual[1:]), set(expected))
        self.assertEqual(
            call[2]['env']['PACT_INTERACTION_RERUN_COMMAND'],
            self.mock_rerun_command.return_value)

    def test_provider_base_url_is_required(self):
        result = self.runner.invoke(verify.main, [])
        self.assertEqual(result.exit_code, 2)
        self.assertIn(b'--provider-base-url', result.output_bytes)
        self.assertFalse(self.mock_Popen.called)

    def test_pact_urls_are_required(self):
        result = self.runner.invoke(
            verify.main, ['--provider-base-url=http://localhost'])

        self.assertEqual(result.exit_code, 1)
        self.assertIn(b'at least one', result.output_bytes)
        self.assertFalse(self.mock_Popen.called)

    def test_local_pact_urls_must_exist(self):
        self.mock_isfile.return_value = False
        result = self.runner.invoke(verify.main, self.default_opts)
        self.assertEqual(result.exit_code, 1)
        self.assertIn(b'./pacts/consumer-provider.json', result.output_bytes)
        self.assertFalse(self.mock_Popen.called)

    def test_failed_verification(self):
        self.mock_Popen.return_value.returncode = 3
        result = self.runner.invoke(verify.main, self.default_opts)
        self.assertEqual(result.exit_code, 3)
        self.assertProcess(*self.default_call)

    def test_successful_verification(self):
        self.mock_Popen.return_value.returncode = 0
        result = self.runner.invoke(verify.main, self.default_opts)
        self.assertEqual(result.exit_code, 0)
        self.assertProcess(*self.default_call)

    @patch.dict(os.environ, {'PACT_BROKER_PASSWORD': 'pwd'})
    def test_password_from_env_var(self):
        self.mock_Popen.return_value.returncode = 0
        result = self.runner.invoke(verify.main, self.default_opts)
        self.assertEqual(result.exit_code, 0)
        self.assertProcess(*self.default_call + ['--broker-password=pwd'])

    def test_all_options(self):
        self.mock_Popen.return_value.returncode = 0
        result = self.runner.invoke(verify.main, [
            './pacts/consumer-provider5.json',
            '--provider-base-url=http://localhost',
            '--pact-urls=./pacts/consumer-provider.json,'
            './pacts/consumer-provider2.json',
            '--pact-url=./pacts/consumer-provider3.json',
            '--pact-url=./pacts/consumer-provider4.json',
            '--provider-states-setup-url=http://localhost/provider-states/set',
            '--pact-broker-username=user',
            '--pact-broker-password=pass',
            '--publish-verification-results',
            '--provider-app-version=1.2.3',
            '--timeout=60',
            '--verbose'
        ])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(self.mock_Popen.call_count, 1)
        self.assertProcess(
            './pacts/consumer-provider5.json',
            './pacts/consumer-provider3.json',
            './pacts/consumer-provider4.json',
            './pacts/consumer-provider.json',
            './pacts/consumer-provider2.json',
            '--provider-base-url=http://localhost',
            '--provider-states-setup-url=http://localhost/provider-states/set',
            '--broker-username=user',
            '--broker-password=pass',
            '--publish-verification-results',
            '--provider-app-version', '1.2.3',
            '--verbose')

    def test_deprecated_pact_urls(self):
        self.mock_Popen.return_value.returncode = 0
        result = self.runner.invoke(verify.main, [
            '--provider-base-url=http://localhost',
            '--pact-urls=./pacts/consumer-provider.json',
            '--pact-urls=./pacts/consumer-provider2.json'
        ])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            b'Multiple --pact-urls arguments are deprecated.',
            result.output_bytes)
        self.assertEqual(self.mock_Popen.call_count, 1)
        self.assertProcess(
            './pacts/consumer-provider.json',
            './pacts/consumer-provider2.json',
            '--provider-base-url=http://localhost')

    def test_publishing_missing_version(self):
        result = self.runner.invoke(verify.main, [
            '--pact-urls=./pacts/consumer-provider.json',
            '--provider-base-url=http://localhost',
            '--publish-verification-results'
        ])
        self.assertEqual(result.exit_code, 1)
        self.assertIn(
            b'Provider application version is required', result.output_bytes)
        self.assertFalse(self.mock_Popen.return_value.communicate.called)


class expand_directoriesTestCase(TestCase):
    def setUp(self):
        super(expand_directoriesTestCase, self).setUp()

        def posix_join(*args):
            return '/'.join(args)

        self.addCleanup(patch.stopall)
        self.mock_isdir = patch.object(verify, 'isdir', autospec=True).start()
        self.mock_join = patch.object(
            verify, 'join', new=posix_join).start()
        self.mock_listdir = patch.object(
            verify, 'listdir', autospec=True).start()

    def test_directory(self):
        self.mock_isdir.return_value = True
        self.mock_listdir.return_value = [
            'consumer-provider.json',
            'consumer2-provider.json',
            'unrelated-file.txt']

        result = verify.expand_directories(['/tmp'])
        self.assertEqual(result, [
            '/tmp/consumer-provider.json',
            '/tmp/consumer2-provider.json',
        ])

    def test_file(self):
        self.mock_isdir.return_value = False
        result = verify.expand_directories(['/tmp/consumer-provider.json'])
        self.assertEqual(result, ['/tmp/consumer-provider.json'])

    def test_uri(self):
        result = verify.expand_directories(['http://broker'])
        self.assertEqual(result, ['http://broker'])

    def test_windows_directories(self):
        self.mock_isdir.return_value = True
        self.mock_listdir.return_value = [
            'consumer-provider.json',
            'consumer2-provider.json',
            'unrelated-file.txt']

        result = verify.expand_directories(['C:\\tmp'])
        self.assertEqual(result, [
            'C:/tmp/consumer-provider.json',
            'C:/tmp/consumer2-provider.json',
        ])


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


class rerun_commandTestCase(TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        self.mock_platform = patch.object(
            verify.platform, 'platform', autospec=True).start()

    @patch.object(verify.sys, 'argv', new=[
        'pact-verifier', '--pact-url=./consumer-provider.json'])
    def test_posix(self):
        self.mock_platform.return_value = 'linux'
        result = verify.rerun_command()
        self.assertEqual(
            result, "PACT_DESCRIPTION='<PACT_DESCRIPTION>'"
                    " PACT_PROVIDER_STATE='<PACT_PROVIDER_STATE>'"
                    " pact-verifier --pact-url=./consumer-provider.json")

    @patch.object(verify.sys, 'argv', new=[
        'pact-verifier.exe', '--pact-url=./consumer-provider.json'])
    def test_windows(self):
        self.mock_platform.return_value = 'Windows'
        result = verify.rerun_command()
        self.assertEqual(
            result, "cmd.exe /v /c \""
                    "set PACT_DESCRIPTION=<PACT_DESCRIPTION>"
                    "& set PACT_PROVIDER_STATE=<PACT_PROVIDER_STATE>"
                    "& pact-verifier.exe"
                    " --pact-url=./consumer-provider.json"
                    " & set PACT_DESCRIPTION="
                    " & set PACT_PROVIDER_STATE=\"")


class sanitize_logsTestCase(TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        self.mock_write = patch.object(
            verify.sys.stdout, 'write', autospec=True).start()

        self.process = Mock(Popen, stdout=[
            'Actual: {"username":123,"id":"100","groups":["users","admins"]}',
            '# /Users/matthewbalvanz/dev/pact-python/pact/bin/pact/lib/vendor'
            '/ruby/2.2.0/gems/pact-provider-verifier-1.6.0/lib/pact/provider'
            '_verifier/cli/custom_thor.rb:17:in `start\'',
            '# /Users/matthewbalvanz/dev/pact-python/pact/bin/pact/lib/app'
            '/pact-provider-verifier.rb:2:in `<main>\''
        ])

    def test_verbose(self):
        verify.sanitize_logs(self.process, True)
        self.mock_write.assert_has_calls([
            call('Actual: {"username":123,"id":"100","groups":'
                 '["users","admins"]}'),
            call('# /Users/matthewbalvanz/dev/pact-python/pact/bin/pact/lib'
                 '/vendor/ruby/2.2.0/gems/pact-provider-verifier-1.6.0/lib'
                 '/pact/provider_verifier/cli/custom_thor.rb:17:in `start\''),
            call('# /Users/matthewbalvanz/dev/pact-python/pact/bin/pact/lib'
                 '/app/pact-provider-verifier.rb:2:in `<main>\'')
        ])

    def test_terse(self):
        verify.sanitize_logs(self.process, False)
        self.mock_write.assert_called_once_with(
            'Actual: {"username":123,"id":"100","groups":["users","admins"]}')
