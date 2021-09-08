import typing
from dataclasses import dataclass, field

@dataclass
class VerifierArgs:
    """Auto-generated class, containing the arguments available to the pact verifier."""

    # Log level (defaults to warn)
    loglevel: typing.Optional[str] = None

    # URL of the pact broker to fetch pacts from to verify (requires the provider name parameter)
    broker_url: typing.Optional[str] = None

    # Provider hostname (defaults to localhost)
    hostname: typing.Optional[str] = None

    # Provider port (defaults to protocol default 80/443)
    port: typing.Optional[str] = None

    # Provider URI scheme (defaults to http)
    scheme: typing.Optional[str] = None

    # Provider name (defaults to provider)
    provider_name: typing.Optional[str] = None

    # URL to post state change requests to
    state_change_url: typing.Optional[str] = None

    # Only validate interactions whose descriptions match this filter
    filter_description: typing.Optional[str] = None

    # Only validate interactions whose provider states match this filter
    filter_state: typing.Optional[str] = None

    # Only validate interactions that have no defined provider state
    filter_no_state: typing.Optional[str] = None

    # Username to use when fetching pacts from URLS
    user: typing.Optional[str] = None

    # Password to use when fetching pacts from URLS
    password: typing.Optional[str] = None

    # Bearer token to use when fetching pacts from URLS
    token: typing.Optional[str] = None

    # Provider version that is being verified. This is required when publishing results.
    provider_version: typing.Optional[str] = None

    # URL of the build to associate with the published verification results.
    build_url: typing.Optional[str] = None

    # Provider tags to use when publishing results. Accepts comma-separated values.
    provider_tags: typing.Optional[str] = None

    # Base path to add to all requests
    base_path: typing.Optional[str] = None

    # Consumer tags to use when fetching pacts from the Broker. Accepts comma-separated values.
    consumer_version_tags: typing.Optional[str] = None

    # Consumer version selectors to use when fetching pacts from the Broker. Accepts a JSON string as per https://docs.pact.io/pact_broker/advanced_topics/consumer_version_selectors/
    consumer_version_selectors: typing.Optional[str] = None

    # Allow pacts that don't match given consumer selectors (or tags) to  be verified, without causing the overall task to fail. For more information, see https://pact.io/wip
    include_wip_pacts_since: typing.Optional[str] = None

    # Sets the HTTP request timeout in milliseconds for requests to the target API and for state change requests.
    request_timeout: typing.Optional[str] = None

    # Pact file to verify (can be repeated)
    file: typing.Optional[typing.List[str]] = field(default_factory=list)

    # Directory of pact files to verify (can be repeated)
    dir: typing.Optional[typing.List[str]] = field(default_factory=list)

    # URL of pact file to verify (can be repeated)
    url: typing.Optional[typing.List[str]] = field(default_factory=list)

    # Consumer name to filter the pacts to be verified (can be repeated)
    filter_consumer: typing.Optional[typing.List[str]] = field(default_factory=list)

    # State change request data will be sent as query parameters instead of in the request body
    state_change_as_query: typing.Optional[bool] = None

    # State change teardown requests are to be made after each interaction
    state_change_teardown: typing.Optional[bool] = None

    # Enables publishing of verification results back to the Pact Broker. Requires the broker-url and provider-version parameters.
    publish: typing.Optional[bool] = None

    # Disables validation of SSL certificates
    disable_ssl_verification: typing.Optional[bool] = None

    # Enables Pending Pacts
    enable_pending: typing.Optional[bool] = None
