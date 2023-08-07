"""Classes and methods to verify Contracts (V3 implementation)."""

import os
from typing import NamedTuple
from pact.ffi.native_verifier import NativeVerifier
from urllib.parse import urlparse
from pact.ffi.verifier import VerifyResult
from pact.pact_exception import PactException

from pact.verify_wrapper import is_url

class CustomHeader(NamedTuple):
    """Custom header to send in the Pact Verifier request."""

    name: str
    value: str

class VerifierV3(object):
    """A Pact V3 Verifier."""

    def __init__(self, provider, provider_base_url, **kwargs):
        """Create a new Verifier.

        Args:
            provider ([String]): provider name
            provider_base_url ([String]): provider url

        """
        self.provider = provider
        self.provider_base_url = provider_base_url
        self.native_verifier = NativeVerifier()
        self.verifier_handle = self.native_verifier.new()

    def __str__(self):
        """Return string representation.

        Returns:
            [String]: verifier description.

        """
        return 'V3 Verifier for {} with url {}'.format(self.provider, self.provider_base_url)

    def verify_pacts(self,  # noqa: max-complexity: 18
                     provider_app_version: str or None = None,
                     provider_branch: str or None = None,
                     broker_username: str or None = None,
                     broker_password: str or None = None,
                     broker_token: str or None = None,
                     broker_url: str or None = None,
                     provider_states_setup_url: str or None = None,
                     state_change_as_query: bool or None = False,
                     state_change_teardown: bool or None = False,
                     provider_tags: [str] or None = None,
                     consumer_version_selectors: [str] or None = None,
                     consumer_version_tags: [str] or None = None,
                     request_timeout: int = 300,
                     filter_description: str or None = None,
                     filter_state: str or None = None,
                     filter_no_state: bool or None = False,
                     build_url: str or None = None,
                     disable_ssl_verification: bool or None = False,
                     enable_pending: bool or None = False,
                     include_wip_pacts_since: str or None = None,
                     no_pacts_is_error: bool or None = False,
                     provider_transport: str or None = None,
                     publish_verification_results: bool or None = False,
                     sources: [str] or None = None,
                     consumer_filters: [str] or None = None,
                     add_custom_header: [CustomHeader] or None = None,
                     **kwargs):
        """Verify the pacts against the provider.

        Args:
            broker_username ([String]): broker username
            broker_password ([String]): broker password
            broker_url ([String]): url of broker
            enable_pending ([Boolean]): enable pending pacts
            include_wip_pacts_since ([String]): include wip pacts since
            publish_version ([String]): publish version
            pacts ([String]): pacts to verify

        Returns:
          success: True if no failures

        """
        if not sources and not broker_url:
            raise PactException('Pact sources or pact_broker_url required')

        # Processing provider base url / scheme and port etc from user provided provider_base_url
        parsed_provider_base_url = urlparse(self.provider_base_url)
        provider_scheme = 'http' if parsed_provider_base_url.scheme is None else parsed_provider_base_url.scheme
        provider_hostname = parsed_provider_base_url.path.split(
            "/")[0] if parsed_provider_base_url.scheme is None else parsed_provider_base_url.netloc.split(":")[0]
        provider_path = parsed_provider_base_url.path.split("/")[1] if parsed_provider_base_url.scheme is None else parsed_provider_base_url.path
        try:
            provider_port = int(parsed_provider_base_url.path.split(":")[1])
        except IndexError:
            try:
                provider_port = int(parsed_provider_base_url.netloc.split(":")[1])
            except IndexError:
                provider_port = 8000

        self.native_verifier.set_provider_info(self.verifier_handle, self.provider, provider_scheme, provider_hostname, provider_port, provider_path)

        if filter_state is not None or filter_description is not None:
            self.native_verifier.set_filter_info(
                self.verifier_handle,
                filter_description if filter_description is not None else '',
                filter_state if filter_state is not None else '',
                filter_no_state,
            )

        if publish_verification_results is True:
            self.native_verifier.set_publish_options(
                self.verifier_handle,
                provider_app_version,
                build_url,
                provider_tags,
                provider_branch
            )

        self.native_verifier.set_no_pacts_is_error(self.verifier_handle, no_pacts_is_error)

        if consumer_filters is not None:
            self.native_verifier.set_consumer_filters(self.verifier_handle, consumer_filters)

        # Processing pact sources

        if broker_url is not None and sources is None and (consumer_version_selectors is None
                                                           and consumer_version_tags is None
                                                           and enable_pending is False
                                                           and include_wip_pacts_since is None):
            # This will fetch all the pact files from the broker that match the provider name.
            # NOTE - Ordering is important here, you need to have called pactffi_set_provider_info
            # to the provider name to be set
            print('Fetch via broker source matching provider name')
            self.native_verifier.broker_source(
                self.verifier_handle,
                broker_url,
                broker_username,
                broker_password,
                broker_token,
            )
        elif sources is None:
            print('Fetch pacts dynamically from broker')
            self.native_verifier.broker_source_with_selectors(
                self.verifier_handle,
                broker_url,
                broker_username,
                broker_password,
                broker_token,
                enable_pending,
                include_wip_pacts_since,
                provider_tags,
                provider_branch,
                consumer_version_selectors,
                consumer_version_tags,
            )
        # Add a file, directory or url source (and include broker creds if provided)
        if sources is not None:
            for source in sources:
                if os.path.isdir(source):
                    self.native_verifier.add_directory_source(self.verifier_handle, source)
                elif is_url(source):
                    self.native_verifier.url_source(self.verifier_handle, source, broker_username, broker_password, broker_token)
                else:
                    self.native_verifier.add_file_source(self.verifier_handle, source)

        self.native_verifier.set_verification_options(self.verifier_handle, disable_ssl_verification, request_timeout)

        if provider_states_setup_url is not None:
            self.native_verifier.set_provider_state(self.verifier_handle, provider_states_setup_url, state_change_teardown, state_change_as_query)

        if add_custom_header is not None:
            for header in add_custom_header:
                self.native_verifier.add_custom_header(self.verifier_handle, header['name'], header['value'])

        result = self.native_verifier.execute(self.verifier_handle)
        logs = self.native_verifier.logs(self.verifier_handle)
        return VerifyResult(result, logs)
