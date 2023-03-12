"""Classes and methods to verify Contracts."""
import json

from pact.verify_wrapper import VerifyWrapper, path_exists, expand_directories


class Verifier(object):
    """A Pact Verifier."""

    def __init__(self, provider, provider_base_url, **kwargs):
        """Create a new Verifier.

        Args:
            provider ([String]): provider name
            provider_base_url ([String]): provider url

        """
        self.provider = provider
        self.provider_base_url = provider_base_url

    def __str__(self):
        """Return string representation.

        Returns:
            [String]: verifier description.

        """
        return 'Verifier for {} with url {}'.format(self.provider, self.provider_base_url)

    def validate_publish(self, **kwargs):
        """Validate publish has a version."""
        if (kwargs.get('publish') is not None) and (kwargs.get('publish_version') is None):
            # do something
            raise Exception()

    def verify_pacts(
            self,
            *pacts,
            enable_pending=False,
            include_wip_pacts_since=None,
            **kwargs
    ):
        """Verify pacts from the provider.

        Example:

        >>> from pact import Verifier
        >>>
        >>> PROVIDER_URL = f'http://127.0.0.1:5001'
        >>>
        >>> verifier = Verifier(
        ...   provider='AcmeAPI',
        ...   provider_base_url=PROVIDER_URL
        ... )
        >>>
        >>> result, _ = verifier.verify_pacts(
        ...   'consumer-provider.json',
        ...   enable_pending=True,
        ... )
        >>>
        >>> assert result == 0

        :param pacts: List of pact to verify. Every pact in that list can be
            an HTTP URI or a local file.
        :type pacts: str
        :param enable_pending: Allow pacts which are in pending state to be
            verified without causing the overall task to fail.
        :type enable_pending: bool
        :param include_wip_pacts_since: Allow pacts that don't match given
            consumer selectors (or tags) to  be verified, without causing the
            overall task to fail
        :type include_wip_pacts_since: str or None
        :return: Returns a tuple of two elements. The first indicates the
            status of the operation, so that 0 means success, and the second
            contains the logs of the operation.
        :rtype: tuple
        """
        self.validate_publish(**kwargs)

        missing_pacts = [path for path in pacts if not path_exists(path)]
        if missing_pacts:
            raise Exception("Missing pact files: {}".format(
                ', '.join(missing_pacts))
            )

        pacts = expand_directories(list(pacts))
        options = self.extract_params(**kwargs)

        return_code, logs = VerifyWrapper().call_verify(
            *pacts,
            provider=self.provider,
            provider_base_url=self.provider_base_url,
            enable_pending=enable_pending,
            include_wip_pacts_since=include_wip_pacts_since,
            **options
        )

        return return_code, logs

    def verify_with_broker(
            self,
            *pacts,
            enable_pending=False,
            include_wip_pacts_since=None,
            **kwargs
    ):
        """Use Broker to verify.

        Example:

        >>> from pact import Verifier
        >>>
        >>> PROVIDER_URL = f'http://127.0.0.1:5001'
        >>>
        >>> verifier = Verifier(
        ...   provider='AcmeAPI',
        ...   provider_base_url=PROVIDER_URL
        ... )
        >>>
        >>> result, _ = verifier.verify_with_broker(
        ...   'https://broker/consumer-provider.json',
        ...   enable_pending=True,
        ...   broker_username='pactbroker',
        ...   broker_password='pactbroker',
        ...   broker_url='http://localhost',
        ... )
        >>>
        >>> assert result == 0

        :param pacts: List of pact to verify. Every pact in that list can be
            an HTTP URI or a local file.
        :type pacts: str
        :param enable_pending: Allow pacts which are in pending state to be
            verified without causing the overall task to fail.
        :type enable_pending: bool
        :param include_wip_pacts_since: Allow pacts that don't match given
            consumer selectors (or tags) to  be verified, without causing the
            overall task to fail
        :type include_wip_pacts_since: str or None
        :keyword str broker_username: Pact Broker basic auth username.
        :keyword str broker_password: Pact Broker basic auth password.
        :keyword str broker_token: Pact Broker bearer token.
        :keyword str broker_url: Base URL of the Pact Broker from which to
            retrieve the pacts.
        :raises Exception: [ErrorDescription]
        :return: Returns a tuple of two elements. The first indicates the
            status of the operation, so that 0 means success, and the second
            contains the logs of the operation.
        :rtype: tuple
        """
        self.validate_publish(**kwargs)

        options = {
            'broker_password': kwargs.get('broker_password', None),
            'broker_username': kwargs.get('broker_username', None),
            'broker_token': kwargs.get('broker_token', None),
            'broker_url': kwargs.get('broker_url', None),
        }

        missing_pacts = [path for path in pacts if not path_exists(path)]
        if missing_pacts:
            raise Exception("Missing pact files: {}".format(
                ', '.join(missing_pacts))
            )

        pacts = expand_directories(list(pacts))
        options.update(self.extract_params(**kwargs))

        return_code, logs = VerifyWrapper().call_verify(
            *pacts,
            provider=self.provider,
            provider_base_url=self.provider_base_url,
            enable_pending=enable_pending,
            include_wip_pacts_since=include_wip_pacts_since,
            **options
        )

        return return_code, logs

    def extract_params(self, **kwargs):
        """Extract params."""
        log_dir = kwargs.get('log_dir', None)
        log_level = kwargs.get('log_level', 'INFO')
        headers = kwargs.get('headers', [])
        timeout = kwargs.get('timeout', None)
        consumer_tags = kwargs.get('consumer_tags', [])
        provider_tags = kwargs.get('provider_tags', [])
        states_setup_url = kwargs.get('provider_states_setup_url', None)
        verbose = kwargs.get('verbose', False)
        provider_app_version = kwargs.get('publish_version', None)
        publish_verification_results = kwargs.get('publish_verification_results', None)
        raw_consumer_selectors = kwargs.get('consumer_version_selectors', [])
        consumer_selectors = self._build_consumer_selectors(raw_consumer_selectors)
        provider_version_branch = kwargs.get('provider_version_branch')

        options = {
            'log_dir': log_dir,
            'log_level': log_level,
            'provider_app_version': provider_app_version,
            'custom_provider_headers': list(headers),
            'timeout': timeout,
            'consumer_tags': list(consumer_tags),
            'provider_tags': list(provider_tags),
            'provider_states_setup_url': states_setup_url,
            'verbose': verbose,
            'consumer_selectors': consumer_selectors,
            'publish_verification_results': publish_verification_results,
            'provider_version_branch': provider_version_branch
        }
        return self.filter_empty_options(**options)

    def _build_consumer_selectors(self, consumer_selectors):
        """
        Build the consumer_selectors list.

        Turn each dict in the consumer_selectors list into a string with a
        json object, as expected by VerifyWrapper.
        """
        return [json.dumps(selector) for selector in consumer_selectors]

    def filter_empty_options(self, **kwargs):
        """Filter out empty options."""
        kwargs = dict(filter(lambda item: item[1] is not None, kwargs.items()))
        kwargs = dict(filter(lambda item: item[1] != '', kwargs.items()))
        kwargs = dict(filter(lambda item: self.is_empty_list(item), kwargs.items()))
        return kwargs

    def is_empty_list(self, item):
        """Util for is empty lists."""
        return (not isinstance(item[1], list)) or (len(item[1]) != 0)
