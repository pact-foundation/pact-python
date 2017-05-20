"""Methods to verify previously created pacts."""
import sys
from os.path import isfile

import click

from .constants import VERIFIER_PATH

if sys.version_info.major == 2:
    import subprocess32 as subprocess
else:
    import subprocess


@click.command()
@click.option(
    'base_url', '--provider-base-url',
    help='Base URL of the provider to verify against.',
    required=True)
@click.option(
    'pact_urls', '--pact-urls',
    help='The URI of the pact to verify.'
         ' Can be an HTTP URI or a local file path.'
         ' It can be specified multiple times to verify several pacts.',
    multiple=True,
    required=True)
@click.option(
    'states_url', '--provider-states-url',
    help='URL to fetch the provider states for the given provider API.')
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
def main(base_url, pact_urls, states_url, states_setup_url, username,
         password, timeout):
    """
    Verify one or more contracts against a provider service.

    Minimal example:

        pact-verifier --provider-base-url=http://localhost:8080 --pact-urls=./pacts
    """  # NOQA
    error = click.style('Error:', fg='red')
    if bool(states_url) != bool(states_setup_url):
        click.echo(
            error
            + ' To use provider states you must provide both'
              ' --provider-states-url and --provider-states-setup-url.')
        raise click.Abort()

    missing_files = [path for path in pact_urls if not path_exists(path)]
    if missing_files:
        click.echo(
            error
            + ' The following Pact files could not be found:\n'
            + '\n'.join(missing_files))
        raise click.Abort()

    options = {
        '--provider-base-url': base_url,
        '--pact-urls': ','.join(pact_urls),
        '--provider-states-url': states_url,
        '--provider-states-setup-url': states_setup_url,
        '--pact-broker-username': username,
        '--pact-broker-password': password
    }

    command = [VERIFIER_PATH] + [
        '{}={}'.format(k, v) for k, v in options.items() if v]

    p = subprocess.Popen(command)
    p.communicate(timeout=timeout)
    sys.exit(p.returncode)


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


if __name__ == '__main__':
    sys.exit(main())
