import pytest

# CLI arguments supported, correct as of Pact FFI 0.0.2.
@pytest.fixture
def cli_options():
    return [
        "loglevel",
        "file",
        "dir",
        "url",
        "broker-url",
        "hostname",
        "port",
        "scheme",
        "provider-name",
        "state-change-url",
        "filter-description",
        "filter-state",
        "filter-no-state",
        "filter-consumer",
        "user",
        "password",
        "token",
        "provider-version",
        "build-url",
        "provider-tags",
        "base-path",
        "consumer-version-tags",
        "consumer-version-selectors",
        "include-wip-pacts-since",
        "request-timeout",
    ]


@pytest.fixture
def cli_flags():
    return ["state-change-as-query", "state-change-teardown", "publish", "disable-ssl-verification", "enable-pending"]


@pytest.fixture
def simple_pact_opts():
    return [
        "./pacts/consumer-provider.json",
        "./pacts/consumer-provider2.json",
        "--provider=provider",
        "--provider-base-url=http://localhost",
    ]


@pytest.fixture
def all_url_opts():
    return [
        "./pacts/consumer-provider.json",
        "./pacts/consumer-provider2.json",
        "--provider-base-url=http://localhost",
        "--pact-url=./pacts/consumer-provider3.json",
        "--pact-urls=./pacts/consumer-provider4.json",
        "--provider=provider",
        "--timeout=30",
        "--verbose",
    ]


@pytest.fixture
def simple_verify_call():
    return ["./pacts/consumer-provider.json", "./pacts/consumer-provider2.json"]


@pytest.fixture
def all_verify_call():
    return [
        "./pacts/consumer-provider.json",
        "./pacts/consumer-provider2.json",
        "./pacts/consumer-provider3.json",
        "./pacts/consumer-provider4.json",
    ]
