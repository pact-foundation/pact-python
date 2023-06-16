from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


# CLI option arguments supported, correct as of Pact FFI 0.0.2.
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
        "provider-branch",
        "base-path",
        "consumer-version-tags",
        "consumer-version-selectors",
        "include-wip-pacts-since",
        "request-timeout",
    ]


# CLI flag arguments supported, correct as of Pact FFI 0.0.2.
@pytest.fixture
def cli_flags():
    return ["state-change-as-query", "state-change-teardown", "publish", "disable-ssl-verification", "enable-pending"]


@pytest.fixture
def pacts_dir():
    """Find the correct pacts dir, depending on where the tests are run from"""
    relative = "../examples/pacts/" if Path.cwd().name == "tests" else "examples/pacts"
    return Path.cwd().joinpath(relative)


@pytest.fixture
def pact_consumer_one_pact_provider_one_path(pacts_dir):
    """Provide the full path to a JSON pact for tests"""
    pact = pacts_dir.joinpath("pact-consumer-one-pact-provider-one.json")
    assert pact.is_file()
    return str(pact)
