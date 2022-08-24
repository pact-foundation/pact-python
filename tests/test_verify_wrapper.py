import os
from unittest import TestCase

from mock import patch, Mock, call

from pact.constants import VERIFIER_PATH
from pact.verify_wrapper import VerifyWrapper, PactException, path_exists, sanitize_logs, expand_directories, rerun_command
from pact import verify_wrapper


from subprocess import PIPE, Popen

class VerifyWrapperTestCase(TestCase):
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
        super(VerifyWrapperTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_Popen = patch.object(
            verify_wrapper.subprocess, 'Popen', spec=verify_wrapper.subprocess.Popen,
            stdout=['6 interactions, 0 failures']).start()

        self.mock_Popen.return_value.communicate.return_value = self.locale

        self.mock_rerun_command = patch.object(
            verify_wrapper, 'rerun_command', autospec=True).start()

        self.default_call = [
            './pacts/consumer-provider.json',
            './pacts/consumer-provider2.json',
            '--no-enable-pending',
            '--provider=test_provider',
            '--provider-base-url=http://localhost']

        self.broker_call = [
            '--provider=test_provider',
            '--provider-base-url=http://localhost',
            '--pact-broker-base-url=http://broker',
            '--broker-username=username',
            '--broker-password=pwd',
            '--broker-token=token',
            '--consumer-version-tag=prod',
            '--consumer-version-tag=dev',
            '--no-enable-pending',
            '--provider-version-tag=dev',
            '--provider-version-tag=qa',
            '--provider-version-branch=provider-branch']

    def assertProcess(self, *expected):
        self.assertEqual(self.mock_Popen.call_count, 1)
        process_call = self.mock_Popen.mock_calls[0]

        actual = process_call[1][0]
        self.assertEqual(actual[0], VERIFIER_PATH)
        self.assertEqual(len(actual), len(expected) + 1)
        self.assertEqual(set(actual[1:]), set(expected))
        self.assertEqual(set(expected), set(actual[1:]))
        self.assertEqual(
            process_call[2]['env'],
            self.mock_rerun_command.return_value)
        self.assertTrue(self.mock_Popen.called)

    def test_pact_urls_or_broker_required(self):
        self.mock_Popen.return_value.returncode = 2
        wrapper = VerifyWrapper()

        with self.assertRaises(PactException) as context:
            wrapper.call_verify(provider='provider', provider_base_url='http://localhost')

        self.assertTrue('Pact urls or Pact broker required' in context.exception.message)

    def test_broker_without_authentication_can_be_used(self):
        self.mock_Popen.return_value.returncode = 0
        wrapper = VerifyWrapper()
        wrapper.call_verify(
            provider='provider', provider_base_url='http://localhost', broker_url='http://broker.example.com'
        )
        self.assertProcess(*[
            '--no-enable-pending',
            '--pact-broker-base-url=http://broker.example.com',
            '--provider-base-url=http://localhost',
            '--provider=provider',
        ])

    def test_pact_urls_provided(self):
        self.mock_Popen.return_value.returncode = 0
        wrapper = VerifyWrapper()

        result, output = wrapper.call_verify('./pacts/consumer-provider.json',
                                             './pacts/consumer-provider2.json',
                                             provider='test_provider',
                                             provider_base_url='http://localhost')

        self.assertProcess(*self.default_call)
        self.assertEqual(result, 0)

    @patch("pact.verify_wrapper.isfile", return_value=True)
    def test_all_url_options(self, mock_isfile):
        self.mock_Popen.return_value.returncode = 0
        wrapper = VerifyWrapper()

        result, output = wrapper.call_verify('./pacts/consumer-provider5.json',
                                             './pacts/consumer-provider3.json',
                                             provider_base_url='http://localhost',
                                             provider_states_setup_url='http://localhost/provider-states/set',
                                             provider='provider',
                                             provider_app_version='1.2.3',
                                             custom_provider_headers=['Authorization: Basic cGFj', 'CustomHeader: somevalue'],
                                             log_dir='tmp/logs/pact.test.log',
                                             log_level='INFO',
                                             timeout=60,
                                             verbose=True,
                                             enable_pending=True,
                                             include_wip_pacts_since='2018-01-01')

        self.assertEqual(result, 0)
        self.mock_Popen.return_value.wait.assert_called_once_with()
        self.assertEqual(self.mock_Popen.call_count, 1)
        self.assertProcess(
            './pacts/consumer-provider5.json',
            './pacts/consumer-provider3.json',
            '--custom-provider-header=Authorization: Basic cGFj',
            '--custom-provider-header=CustomHeader: somevalue',
            '--provider-base-url=http://localhost',
            '--provider-states-setup-url=http://localhost/provider-states/set',
            '--provider=provider',
            '--provider-app-version', '1.2.3',
            '--log-dir=tmp/logs/pact.test.log',
            '--log-level=INFO',
            '--verbose',
            '--enable-pending',
            '--include-wip-pacts-since=2018-01-01',
        )

    def test_uses_broker_if_no_pacts_and_provider_required(self):
        self.mock_Popen.return_value.returncode = 0
        wrapper = VerifyWrapper()

        result, output = wrapper.call_verify(provider='test_provider',
                                             provider_base_url='http://localhost',
                                             broker_username='username',
                                             broker_password='pwd',
                                             broker_token='token',
                                             broker_url='http://broker',
                                             consumer_tags=['prod', 'dev'],
                                             provider_tags=['dev', 'qa'],
                                             provider_version_branch='provider-branch')

        self.assertProcess(*self.broker_call)
        self.assertEqual(result, 0)

    @patch('pact.verify_wrapper.path_exists', return_value=True)
    @patch('pact.verify_wrapper.sanitize_logs')
    @patch('pact.verify_wrapper.expand_directories', return_value='./pacts/consumer-provider.json')
    @patch('pact.verify_wrapper.rerun_command')
    def test_rerun_command_called(self, mock_rerun_cmd, mock_expand_dirs, mock_sanitize_logs, mock_path_exists):
        self.mock_Popen.return_value.returncode = 0
        wrapper = VerifyWrapper()

        result, output = wrapper.call_verify('path/to/pact1',
                                             'path/to/pact2',
                                             provider_base_url='http://localhost',
                                             provider='provider')

        mock_rerun_cmd.assert_called_once()

    @patch('pact.verify_wrapper.path_exists', return_value=True)
    @patch('pact.verify_wrapper.sanitize_logs')
    @patch('pact.verify_wrapper.expand_directories', return_value='./pacts/consumer-provider.json')
    @patch('pact.verify_wrapper.rerun_command')
    def test_sanitize_called(self, mock_rerun_cmd, mock_expand_dirs, mock_sanitize_logs, mock_path_exists):
        self.mock_Popen.return_value.returncode = 0
        wrapper = VerifyWrapper()

        result, output = wrapper.call_verify('path/to/pact1',
                                             'path/to/pact2',
                                             provider_base_url='http://localhost',
                                             provider='provider')

        mock_sanitize_logs.assert_called_with(self.mock_Popen.return_value, False)

    @patch('pact.verify_wrapper.path_exists', return_value=True)
    @patch('pact.verify_wrapper.sanitize_logs')
    def test_publishing_with_version(self, mock_sanitize_logs, mock_path_exists):
        self.mock_Popen.return_value.returncode = 0
        wrapper = VerifyWrapper()

        result, output = wrapper.call_verify('./pacts/consumer-provider.json',
                                             './pacts/consumer-provider2.json',
                                             provider='test_provider',
                                             provider_base_url='http://localhost',
                                             provider_app_version='1.2.3',
                                             publish_verification_results=True)

        self.default_call.extend(['--provider-app-version', '1.2.3', '--publish-verification-results'])

        self.assertProcess(*self.default_call)
        self.assertEqual(result, 0)

    @patch('pact.verify_wrapper.path_exists', return_value=True)
    @patch('pact.verify_wrapper.sanitize_logs')
    @patch('pact.verify_wrapper.expand_directories', return_value='./pacts/consumer-provider.json')
    @patch('pact.verify_wrapper.rerun_command')
    def test_expand_dirs_called(self, mock_rerun_cmd, mock_expand_dirs, mock_sanitize_logs, mock_path_exists):
        self.mock_Popen.return_value.returncode = 0
        wrapper = VerifyWrapper()

        result, output = wrapper.call_verify('path/to/pact1',
                                             'path/to/pact2',
                                             provider_base_url='http://localhost',
                                             provider='provider')

        mock_expand_dirs.assert_called_with(['path/to/pact1',
                                             'path/to/pact2'])


class path_existsTestCase(TestCase):
    def test_path_exists(self):
        self.assertTrue(path_exists('README.md'))

    def test_path_not_exists(self):
        self.assertFalse(path_exists('not_a_real_file'))

    def test_path_exists_valid_for_http(self):
        self.assertTrue(path_exists('http://someurl'))

    def test_path_exists_valid_for_https(self):
        self.assertTrue(path_exists('https://someurl'))


class sanitize_logsTestCase(TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        self.process = Mock(Popen, stdout=[
            'Actual: {"username":123,"id":"100","groups":["users","admins"]}',
            '# /Users/auser/dev/pact-python/pact/bin/pact/lib/vendor'
            '/ruby/2.2.0/gems/pact-provider-verifier-1.6.0/lib/pact/provider'
            '_verifier/cli/custom_thor.rb:17:in `start\'',
            '# /Users/auser/dev/pact-python/pact/bin/pact/lib/app'
            '/pact-provider-verifier.rb:2:in `<main>\''
        ])

    @patch('pact.verify_wrapper.sys.stdout.write')
    def test_verbose(self, mock_write):
        sanitize_logs(self.process, True)
        mock_write.assert_has_calls([
            call('Actual: {"username":123,"id":"100","groups":'
                 '["users","admins"]}'),
            call('# /Users/auser/dev/pact-python/pact/bin/pact/lib'
                 '/vendor/ruby/2.2.0/gems/pact-provider-verifier-1.6.0/lib'
                 '/pact/provider_verifier/cli/custom_thor.rb:17:in `start\''),
            call('# /Users/auser/dev/pact-python/pact/bin/pact/lib'
                 '/app/pact-provider-verifier.rb:2:in `<main>\'')
        ])

    @patch('pact.verify_wrapper.sys.stdout.write')
    def test_terse(self, mock_write):
        sanitize_logs(self.process, False)
        mock_write.assert_called_once_with(
            'Actual: {"username":123,"id":"100","groups":["users","admins"]}')


class expand_directoriesTestCase(TestCase):
    def setUp(self):
        super(expand_directoriesTestCase, self).setUp()

        def posix_join(*args):
            return '/'.join(args)

        self.addCleanup(patch.stopall)
        self.mock_isdir = patch.object(verify_wrapper, 'isdir', autospec=True).start()
        self.mock_join = patch.object(
            verify_wrapper, 'join', new=posix_join).start()
        self.mock_listdir = patch.object(
            verify_wrapper, 'listdir', autospec=True).start()

    def test_directory(self):
        self.mock_isdir.return_value = True
        self.mock_listdir.return_value = [
            'consumer-provider.json',
            'consumer2-provider.json',
            'unrelated-file.txt']

        result = expand_directories(['/tmp'])
        self.assertEqual(result, [
            '/tmp/consumer-provider.json',
            '/tmp/consumer2-provider.json',
        ])

    def test_file(self):
        self.mock_isdir.return_value = False
        result = expand_directories(['/tmp/consumer-provider.json'])
        self.assertEqual(result, ['/tmp/consumer-provider.json'])

    def test_uri(self):
        result = expand_directories(['http://broker'])
        self.assertEqual(result, ['http://broker'])

    def test_windows_directories(self):
        self.mock_isdir.return_value = True
        self.mock_listdir.return_value = [
            'consumer-provider.json',
            'consumer2-provider.json',
            'unrelated-file.txt']

        result = expand_directories(['C:\\tmp'])
        self.assertEqual(result, [
            'C:/tmp/consumer-provider.json',
            'C:/tmp/consumer2-provider.json',
        ])


class rerun_commandTestCase(TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        self.mock_platform = patch.object(
            verify_wrapper.platform, 'platform', autospec=True).start()

    @patch.object(verify_wrapper.sys, 'argv', new=[
        'pact-verifier', '--pact-url=./consumer-provider.json'])
    def test_posix(self):
        self.mock_platform.return_value = 'linux'
        result = rerun_command()
        self.assertEqual(
            result['PACT_INTERACTION_RERUN_COMMAND'],
            "PACT_DESCRIPTION='<PACT_DESCRIPTION>'"
            " PACT_PROVIDER_STATE='<PACT_PROVIDER_STATE>'"
            " pact-verifier --pact-url=./consumer-provider.json")

    @patch.object(verify_wrapper.sys, 'argv', new=[
        'pact-verifier.exe', '--pact-url=./consumer-provider.json'])
    def test_windows(self):
        self.mock_platform.return_value = 'Windows'
        result = rerun_command()
        self.assertEqual(
            result['PACT_INTERACTION_RERUN_COMMAND'],
            "cmd.exe /v /c \""
            "set PACT_DESCRIPTION=<PACT_DESCRIPTION>"
            "& set PACT_PROVIDER_STATE=<PACT_PROVIDER_STATE>"
            "& pact-verifier.exe"
            " --pact-url=./consumer-provider.json"
            " & set PACT_DESCRIPTION="
            " & set PACT_PROVIDER_STATE=\"")

    @patch('pact.verify_wrapper.os.environ')
    def test_env_copied(self, mock_env):
        mock_env.copy.return_value = {'foo': 'bar'}
        self.mock_platform.return_value = 'linux'

        result = rerun_command()
        self.assertEqual(result['foo'], 'bar')
