"""Methods to verify previously created pacts."""
import sys

from pact.verify_wrapper import path_exists, expand_directories, VerifyWrapper

import click


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
    default=[],
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
    help='URL to send POST requests to setup a given provider state.')
@click.option(
    'username', '--pact-broker-username',
    envvar='PACT_BROKER_USERNAME',
    help='Username for Pact Broker basic authentication. Can also be specified'
         ' via the environment variable PACT_BROKER_USERNAME.')
@click.option(
    'broker_base_url', '--pact-broker-url',
    default='',
    envvar='PACT_BROKER_BASE_URL',
    help='Base URl for the Pact Broker instance to publish pacts to. Can also be specified'
         ' via the environment variable PACT_BROKER_BASE_URL.')
@click.option(
    'consumer_version_tag', '--consumer-version-tag',
    default=[],
    multiple=True,
    help='Retrieve the latest pacts with this consumer version tag. '
         'Used in conjunction with --provider. May be specified multiple times.')
@click.option(
    'consumer_version_selector', '--consumer-version-selector',
    default=[],
    multiple=True,
    help='Retrieve the latest pacts with this consumer version selector. '
         'Used in conjunction with --provider. May be specified multiple times.')
@click.option(
    'provider_version_tag', '--provider-version-tag',
    default=[],
    multiple=True,
    help='Tag to apply to the provider application version. '
         'May be specified multiple times.')
@click.option(
    'password', '--pact-broker-password',
    envvar='PACT_BROKER_PASSWORD',
    help='Password for Pact Broker basic authentication. Can also be specified'
         ' via the environment variable PACT_BROKER_PASSWORD.')
@click.option(
    'token', '--pact-broker-token',
    envvar='PACT_BROKER_TOKEN',
    help='Bearer token for Pact Broker authentication. Can also be specified'
         ' via the environment variable PACT_BROKER_TOKEN.')
@click.option(
    'provider', '--provider',
    default='',
    help='Retrieve the latest pacts for this provider.')
@click.option(
    'headers', '--custom-provider-header',
    envvar='CUSTOM_PROVIDER_HEADER',
    multiple=True,
    help='Header to add to provider state set up and '
         'pact verification requests. '
         'eg \'Authorization: Basic cGFjdDpwYWN0\'. '
         'May be specified multiple times.')
@click.option(
    'timeout', '-t', '--timeout',
    default=30,
    help='The duration in seconds we should wait to confirm that the verification'
         ' process was successful. Defaults to 30.',
    type=int)
@click.option(
    'provider_app_version', '-a', '--provider-app-version',
    help='The provider application version. '
         'Required for publishing verification results.')
@click.option(
    'publish_verification_results', '-r', '--publish-verification-results',
    default=False,
    help='Publish verification results to the broker.',
    is_flag=True)
@click.option(
    '--verbose/--no-verbose',
    default=False,
    help='Toggle verbose logging, defaults to False.')
@click.option(
    'log_dir', '--log-dir',
    help='The directory for the pact.log file.')
@click.option(
    'log_level', '--log-level',
    help='The logging level.')
@click.option(
    'enable_pending', '--enable-pending',
    default=False,
    help='Allow pacts which are in pending state to be verified without causing the '
         'overall task to fail. For more information, see https://pact.io/pending',
    is_flag=True)
@click.option(
    'include_wip_pacts_since', '--include-wip-pacts-since',
    default=None,
    help='Automatically include the pending pacts in the verification step. '
         'For more information, see https://docs.pact.io/pact_broker/advanced_topics/wip_pacts/',)
def main(pacts, base_url, pact_url, pact_urls, states_url, states_setup_url,
         username, broker_base_url, consumer_version_tag, consumer_version_selector,
         provider_version_tag, password, token, provider, headers, timeout,
         provider_app_version, publish_verification_results, verbose, log_dir,
         log_level, enable_pending, include_wip_pacts_since):
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
            + 'Please provide a comma separated list of pacts to --pact-urls, '
            + 'or multiple --pact-url arguments.')

    if not all_pact_urls and broker_not_provided(broker_base_url, provider):
        click.echo(
            error
            + ' You must supply at least one pact file or directory '
            + 'to verify OR a Pact Broker and Provider.')
        raise click.Abort()

    all_pact_urls = expand_directories(all_pact_urls)

    missing_files = [path for path in all_pact_urls if not path_exists(path)]
    if missing_files:
        click.echo(
            error
            + ' The following Pact files could not be found:\n'
            + '\n'.join(missing_files))
        raise click.Abort()

    if publish_verification_results:
        validate_publish(error, provider_app_version)

    options = {
        'broker_password': password,
        'broker_username': username,
        'broker_token': token,
        'broker_url': broker_base_url,
        'log_dir': log_dir,
        'log_level': log_level,
        'provider_app_version': provider_app_version,
        'custom_provider_headers': list(headers),
        'publish_verification_results': publish_verification_results,
        'timeout': timeout,
        'verbose': verbose,
        'consumer_tags': list(consumer_version_tag),
        'consumer_selectors': list(consumer_version_selector),
        'provider_tags': list(provider_version_tag),
        'provider_states_setup_url': states_setup_url,
    }

    options = dict(filter(lambda item: item[1] is not None, options.items()))
    options = dict(filter(lambda item: item[1] != '', options.items()))
    options = dict(filter(lambda item: is_empty_list(item), options.items()))

    success, logs = VerifyWrapper().call_verify(*all_pact_urls,
                                                provider=provider,
                                                provider_base_url=base_url,
                                                enable_pending=enable_pending,
                                                include_wip_pacts_since=include_wip_pacts_since,
                                                **options)
    sys.exit(success)


def validate_publish(error, provider_app_version):
    """Publish results to broker."""
    if not provider_app_version:
        click.echo(
            error
            + 'Provider application version is required '
            + 'to publish verification results to broker'
        )
        raise click.Abort()


def broker_not_provided(broker_base_url, provider):
    """Check if broker not provided."""
    return (broker_base_url == '' or provider == '')


def is_empty_list(item):
    """Util for is empty lists."""
    return (not isinstance(item[1], list)) or (len(item[1]) != 0)


if __name__ == '__main__':
    sys.exit(main())
