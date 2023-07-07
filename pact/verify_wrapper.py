"""Wrapper to verify previously created pacts."""

from pact.constants import VERIFIER_PATH
from pact.pact_exception import PactException
import sys
import os
import platform

import subprocess
from os.path import isdir, join, isfile
from os import listdir
from urllib.parse import urlparse


def is_url(path):
    """Determine if a string is a valid url.

    Can be provided a URL or local path. URLs always result in a True.

    :param path: The path to check.
    :type path: str
    :return: True if url otherwise False.
    :rtype: bool
    """
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def capture_logs(process, verbose):
    """Capture logs from ruby process."""
    result = ''
    for line in process.stdout:
        result = result + line + '\n'

    return result


def path_exists(path):
    """
    Determine if a particular path exists.

    Can be provided a URL or local path. URLs always result in a True. Local
    paths are True only if a file exists at that location.

    :param path: The path to check.
    :type path: str
    :return: True if the path exists and is a file, otherwise False.
    :rtype: bool
    """
    if path.startswith('http://') or path.startswith('https://'):
        return True

    return isfile(path)

def sanitize_logs(process, verbose):
    """
    Print the logs from a process while removing Ruby stack traces.

    :param process: The Ruby pact verifier process.
    :type process: subprocess.Popen
    :param verbose: Flag to toggle more verbose logging.
    :type verbose: bool
    :rtype: None
    """
    for line in process.stdout:
        if (not verbose and line.lstrip().startswith('#')
                and ('vendor/ruby' in line or 'pact-provider-verifier.rb' in line)):
            continue
        else:
            sys.stdout.write(line)

def expand_directories(paths):
    """
    Iterate over paths and expand any that are directories into file paths.

    :param paths: A list of file paths to expand.
    :type paths: list
    :return: A list of file paths with any directory paths replaced with the
        JSON files in those directories.
    :rtype: list
    """
    paths_ = []
    for path in paths:
        if path.startswith('http://') or path.startswith('https://'):
            paths_.append(path)
        elif isdir(path):
            paths_.extend(
                [join(path, p) for p in listdir(path) if p.endswith('.json')])
        else:
            paths_.append(path)

    # Ruby pact verifier expects forward slashes regardless of OS
    return [p.replace('\\', '/') for p in paths_]


def rerun_command():
    """
    Create a rerun command template for failed interactions.

    :rtype: str
    """
    is_windows = 'windows' in platform.platform().lower()
    command = ''
    if is_windows:
        command = (
            'cmd.exe /v /c "'
            'set PACT_DESCRIPTION=<PACT_DESCRIPTION>'
            '& set PACT_PROVIDER_STATE=<PACT_PROVIDER_STATE>'
            '& {command}'
            ' & set PACT_DESCRIPTION='
            ' & set PACT_PROVIDER_STATE="'.format(command=' '.join(sys.argv)))
    else:
        command = ("PACT_DESCRIPTION='<PACT_DESCRIPTION>'"
                   " PACT_PROVIDER_STATE='<PACT_PROVIDER_STATE>'"
                   " {command}".format(command=' '.join(sys.argv)))

    env = os.environ.copy()
    env['PACT_INTERACTION_RERUN_COMMAND'] = command
    return env

class VerifyWrapper(object):
    """A Pact Verifier Wrapper."""

    def _broker_present(self, **kwargs):
        if kwargs.get('broker_url') is None:
            return False
        return True

    def _validate_input(self, pacts, **kwargs):
        if len(pacts) == 0 and not self._broker_present(**kwargs):
            raise PactException('Pact urls or Pact broker required')

    def verify( # noqa: max-complexity: 15
            self, *pacts, provider_base_url, provider, enable_pending=False,
            include_wip_pacts_since=None, **kwargs
    ):
        """Call verify method."""
        verbose = kwargs.get('verbose', False)
        # if pacts:
        #     self._validate_input(pacts, **kwargs)

        provider_app_version = kwargs.get('provider_app_version')
        provider_version_branch = kwargs.get('provider_version_branch')
        publish_verification_results = kwargs.get('publish_verification_results', False)
        options = {
            '--provider-base-url': provider_base_url,
            '--provider': provider,
            '--broker-username': kwargs.get('broker_username', None),
            '--broker-password': kwargs.get('broker_password', None),
            '--broker-token': kwargs.get('broker_token', None),
            '--pact-broker-base-url': kwargs.get('broker_url', None),
            '--provider-states-setup-url': kwargs.get('provider_states_setup_url'),
            '--log-dir': kwargs.get('log_dir'),
            '--log-level': kwargs.get('log_level')
        }

        command = [VERIFIER_PATH]
        local_file = False
        all_pact_urls = False
        if pacts:
            all_pact_urls = expand_directories(list(pacts))
            for pact_url in all_pact_urls:
                if not is_url(pact_url):
                    local_file = True

            command.extend(all_pact_urls)

        command.extend(['{}={}'.format(k, v) for k, v in options.items() if v])

        if not all_pact_urls and not kwargs.get('broker_url', None):
            raise PactException('Pact urls or Pact broker required')

        if publish_verification_results is True and local_file:
            raise PactException('Cannot publish verification results for local files')

        if (provider_app_version):
            command.extend(["--provider-app-version", provider_app_version])

        if publish_verification_results is True and not local_file:
            command.extend(['--publish-verification-results'])

        if verbose:
            command.extend(['--verbose'])

        if provider_version_branch:
            command.extend(["--provider-version-branch={}".format(provider_version_branch)])

        headers = kwargs.get('custom_provider_headers', [])
        for header in headers:
            command.extend(['{}={}'.format('--custom-provider-header', header)])

        if not all_pact_urls:
            if enable_pending:
                command.append('--enable-pending')
            else:
                command.append('--no-enable-pending')
            if include_wip_pacts_since:
                command.extend(['--include-wip-pacts-since={}'.format(include_wip_pacts_since)])
            for tag in kwargs.get('provider_tags', []):
                command.extend(["--provider-version-tag={}".format(tag)])
            for selector in kwargs.get('consumer_selectors', []):
                command.extend(["--consumer-version-selector={}".format(selector)])
            for tag in kwargs.get('consumer_tags', []):
                command.extend(["--consumer-version-tag={}".format(tag)])

        env = rerun_command()
        result = subprocess.Popen(command, bufsize=1, env=env, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, universal_newlines=True)

        sanitize_logs(result, verbose)
        result.wait()
        logs = capture_logs(result, verbose)

        return result.returncode, logs

    def version(self):
        """Publish version info."""
        return '0.0.0'
