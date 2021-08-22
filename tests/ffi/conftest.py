import pytest


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
