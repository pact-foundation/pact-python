"""
Unit tests for the pact.v3.verifier module.

These tests perform only very basic checks to ensure that the FFI module is
working correctly. They are not intended to test the Verifier API much, as
that is handled by the compatibility suite.
"""

import re
from pathlib import Path

import pytest

from pact.v3.verifier import Verifier

ASSETS_DIR = Path(__file__).parent / "assets"


@pytest.fixture
def verifier() -> Verifier:
    return Verifier("Tester")


def test_str_repr(verifier: Verifier) -> None:
    assert str(verifier) == "Verifier(Tester)"
    assert re.match(
        r"<Verifier: Tester, handle=VerifierHandle\(0x[0-9a-f]+\)>",
        repr(verifier),
    )


def test_set_provider_info(verifier: Verifier) -> None:
    url = "http://localhost:8888/api"
    verifier.add_transport(url=url)
    verifier.verify()


def test_add_provider_transport(verifier: Verifier) -> None:
    # HTTP
    verifier.add_transport(
        protocol="http",
        port=1234,
        path="/api",
        scheme="http",
    )

    # HTTPS
    verifier.add_transport(
        protocol="http",
        port=4321,
        path="/api",
        scheme="https",
    )

    # message
    verifier.add_transport(
        protocol="message",
    )

    # gRPC
    verifier.add_transport(
        protocol="grpc",
        port=1234,
    )


def test_set_filter(verifier: Verifier) -> None:
    verifier.filter("test_filter")
    verifier.filter("test_filter", state="test_value")
    verifier.filter("no_state", no_state=True)


def test_set_state(verifier: Verifier) -> None:
    verifier.state_handler("test_state", body=True)


def test_disable_ssl_verification(verifier: Verifier) -> None:
    verifier.disable_ssl_verification()


def test_set_request_timeout(verifier: Verifier) -> None:
    verifier.set_request_timeout(1000)


def test_set_coloured_output(verifier: Verifier) -> None:
    verifier.set_coloured_output(enabled=True)
    verifier.set_coloured_output(enabled=False)


def test_set_error_on_empty_pact(verifier: Verifier) -> None:
    verifier.set_error_on_empty_pact(enabled=True)
    verifier.set_error_on_empty_pact(enabled=False)


def test_set_publish_options(verifier: Verifier) -> None:
    verifier.set_publish_options(
        version="1.0.0",
        url="http://localhost:8080/build/1234",
        branch="main",
        tags=["main", "test", "prod"],
    )


def test_filter_consumers(verifier: Verifier) -> None:
    verifier.filter_consumers("consumer1")
    verifier.filter_consumers("consumer1", "consumer2")


def test_add_custom_header(verifier: Verifier) -> None:
    verifier.add_custom_header("Authorization", "Bearer: 1234")


def test_add_custom_headers(verifier: Verifier) -> None:
    verifier.add_custom_headers({
        "Authorization": "Bearer: 1234",
        "Content-Type": "application/json",
    })


def test_add_source(verifier: Verifier) -> None:
    # URL
    verifier.add_source("http://localhost:8080/pact.json")

    # File
    verifier.add_source(ASSETS_DIR / "pacts" / "basic.json")

    # Directory
    verifier.add_source(ASSETS_DIR / "pacts")


def test_broker_source(verifier: Verifier) -> None:
    verifier.broker_source("http://localhost:8080")
    verifier.broker_source(
        "http://localhost:8080",
        username="user",
        password="password",  # noqa: S106
    )
    verifier.broker_source(
        "http://localhost:8080",
        token="1234",  # noqa: S106
    )


def test_broker_source_selector(verifier: Verifier) -> None:
    (
        verifier.broker_source("http://localhost:8080", selector=True)
        .consumer_tags("main", "test")
        .provider_tags("main", "test")
        .consumer_versions('{"latest": true}')
        .build()
    )


def test_verify(verifier: Verifier) -> None:
    verifier.add_transport(url="http://localhost:8080")
    verifier.verify()


def test_logs(verifier: Verifier) -> None:
    logs = verifier.logs
    assert logs == ""


def test_output(verifier: Verifier) -> None:
    output = verifier.output()
    assert output == ""
