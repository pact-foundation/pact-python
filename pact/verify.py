"""Methods to verify previously created pacts."""
import os
import platform
import sys
from os import listdir
from os.path import isfile, isdir, join

import click

from .constants import VERIFIER_PATH

if sys.version_info.major == 2:
    import subprocess32 as subprocess
else:
    import subprocess


@click.command()
@click.argument('pacts', nargs=-1)
@click.option(
    'base_url', '--provider-base-url',
    help='Base URL of the provider to verify against.',
    required=True)
@click.option(
    'pact_url', '--pact-url',
    help='DEPRECATED: specify pacts as arguments instead.\n'
         'The URI of the pact to verify.'
         ' Can be an HTTP URI, a local file or directory path. '
         ' It can be specified multiple times to verify several pacts.',
    multiple=True)  # Remove in major version 1.0.0
@click.option(
    'pact_urls', '--pact-urls',
    default='',
    help='DEPRECATED: specify pacts as arguments instead.\n'
         'The URI(s) of the pact to verify.'
         ' Can be an HTTP URI(s) or local file path(s).'
         ' Provide multiple URI separated by a comma.',
    multiple=True)  # Remove in major version 1.0.0
@click.option(
    'states_url', '--provider-states-url',
    help='DEPRECATED: URL to fetch the provider states for'
         ' the given provider API.')  # Remove in major version 1.0.0
@click.option(
    'states_setup_url', '--provider-states-setup-url',
    help='URL to send PUT requests to setup a given provider state.')
@click.option(
    'username', '--pact-broker-username',
    help='Username for Pact Broker basic authentication.')
@click.option(
    'password', '--pact-broker-password',
    envvar='PACT_BROKER_PASSWORD',
    help='Password for Pact Broker basic authentication. Can also be specified'
         ' via the environment variable PACT_BROKER_PASSWORD')
@click.option(
    'timeout', '-t', '--timeout',
    default=30,
    help='The duration in seconds we should wait to confirm verification'
         ' process was successful. Defaults to 30.',
    type=int)
@click.option(
    'provider_app_version', '-a', '--provider-app-version',
    help='The provider application version, '
         'required for publishing verification results'
    )
@click.option(
    'publish_verification_results', '-r', '--publish-verification-results',
    default=False,
    help='Publish verification results to the broker',
    is_flag=True)
@click.option(
    '--verbose/--no-verbose',
    default=False,
    help='Toggle verbose logging, defaults to False.')
def main(pacts, base_url, pact_url, pact_urls, states_url,
         states_setup_url, username, password, timeout, provider_app_version,
         publish_verification_results, verbose):
    """
    Verify one or more contracts against a provider service.

    Minimal example:

        pact-verifier --provider-base-url=http://localhost:8080 ./pacts
    """  # NOQA
    error = click.style('Error:', fg='red')
    warning = click.style('Warning:', fg='yellow')
    all_pact_urls = list(pacts) + list(pact_url)
    for urls in pact_urls:  # Remove in major version 1.0.0
        all_pact_urls.extend(p for p in urls.split(',') if p)

    if len(pact_urls) > 1:
        click.echo(
            warning
            + ' Multiple --pact-urls arguments are deprecated. '
              'Please provide a comma separated list of pacts to --pact-urls, '
              'or multiple --pact-url arguments.')

    if not all_pact_urls:
        click.echo(
            error
            + ' You must supply at least one pact file or directory to verify')
        raise click.Abort()

    all_pact_urls = expand_directories(all_pact_urls)
    missing_files = [path for path in all_pact_urls if not path_exists(path)]
    if missing_files:
        click.echo(
            error
            + ' The following Pact files could not be found:\n'
            + '\n'.join(missing_files))
        raise click.Abort()

    options = {
        '--provider-base-url': base_url,
        '--provider-states-setup-url': states_setup_url,
        '--broker-username': username,
        '--broker-password': password
    }
    command = [VERIFIER_PATH]
    command.extend(all_pact_urls)
    command.extend(['{}={}'.format(k, v) for k, v in options.items() if v])

    if publish_verification_results:
        if not provider_app_version:
            click.echo(
                error
                + 'Provider application version is required '
                + 'to publish verification results to broker'
            )
            raise click.Abort()
        command.extend(["--provider-app-version",
                        provider_app_version,
                        "--publish-verification-results"])

    if verbose:
        command.extend(['--verbose'])

    env = os.environ.copy()
    env['PACT_INTERACTION_RERUN_COMMAND'] = rerun_command()
    p = subprocess.Popen(command, bufsize=1, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, universal_newlines=True)

    sanitize_logs(p, verbose)
    sys.exit(p.returncode)


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


def rerun_command():
    """
    Create a rerun command template for failed interactions.

    :rtype: str
    """
    is_windows = 'windows' in platform.platform().lower()
    if is_windows:
        return (
            'cmd.exe /v /c "'
            'set PACT_DESCRIPTION=<PACT_DESCRIPTION>'
            '& set PACT_PROVIDER_STATE=<PACT_PROVIDER_STATE>'
            '& {command}'
            ' & set PACT_DESCRIPTION='
            ' & set PACT_PROVIDER_STATE="'.format(command=' '.join(sys.argv)))
    else:
        return ("PACT_DESCRIPTION='<PACT_DESCRIPTION>'"
                " PACT_PROVIDER_STATE='<PACT_PROVIDER_STATE>'"
                " {command}".format(command=' '.join(sys.argv)))


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
            and ('vendor/ruby' in line
                 or 'pact-provider-verifier.rb' in line)):
            continue
        else:
            sys.stdout.write(line)


if __name__ == '__main__':
    sys.exit(main())
