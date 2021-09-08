import pytest

# CLI arguments supported, correct as of Pact FFI 0.0.2.
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


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
