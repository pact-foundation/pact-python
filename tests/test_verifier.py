"""
Unit tests for the pact.verifier module.

These tests perform only very basic checks to ensure that the FFI module is
working correctly. They are not intended to test the Verifier API much, as
that is handled by the compatibility suite.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from pact.verifier import Verifier

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


@pytest.mark.parametrize(
    ("selector_calls", "expected_selectors"),
    [
        pytest.param(
            [{"consumer": "test-consumer"}],
            [{"consumer": "test-consumer"}],
            id="single_parameter",
        ),
        pytest.param(
            [{"consumer": "test-consumer", "branch": "main", "latest": True}],
            [{"consumer": "test-consumer", "branch": "main", "latest": True}],
            id="multiple_parameters",
        ),
        pytest.param(
            [{"deployed_or_released": True, "fallback_tag": "latest"}],
            [{"deployedOrReleased": True, "fallbackTag": "latest"}],
            id="camelcase_conversion",
        ),
        pytest.param(
            [
                {"branch": "main", "latest": True},
                {"branch": "feature-branch", "latest": True},
                {"deployed": True},
            ],
            [
                {"branch": "main", "latest": True},
                {"branch": "feature-branch", "latest": True},
                {"deployed": True},
            ],
            id="multiple_selectors",
        ),
        pytest.param(
            [
                {
                    "consumer": "test-consumer",
                    "tag": "v1.0",
                    "fallback_tag": "latest",
                    "latest": True,
                    "deployed_or_released": True,
                    "deployed": True,
                    "released": True,
                    "environment": "staging",
                    "main_branch": True,
                    "branch": "feature-123",
                    "matching_branch": True,
                    "fallback_branch": "develop",
                }
            ],
            [
                {
                    "consumer": "test-consumer",
                    "tag": "v1.0",
                    "fallbackTag": "latest",
                    "latest": True,
                    "deployedOrReleased": True,
                    "deployed": True,
                    "released": True,
                    "environment": "staging",
                    "mainBranch": True,
                    "branch": "feature-123",
                    "matchingBranch": True,
                    "fallbackBranch": "develop",
                }
            ],
            id="all_parameters",
        ),
        pytest.param(
            [
                {
                    "consumer": "test-consumer",
                    "branch": "main",
                    "tag": None,
                    "latest": None,
                }
            ],
            [{"consumer": "test-consumer", "branch": "main"}],
            id="none_values_excluded",
        ),
    ],
)
def test_consumer_version(
    verifier: Verifier,
    selector_calls: list[dict[str, Any]],
    expected_selectors: list[dict[str, Any]],
) -> None:
    """Test consumer_version with various parameter combinations and selector counts."""
    with patch("pact_ffi.verifier_broker_source_with_selectors") as mock_ffi:
        selector_builder = verifier.broker_source(
            "http://localhost:8080",
            selector=True,
        )

        # Call consumer_version for each set of parameters
        for params in selector_calls:
            selector_builder.consumer_version(**params)

        selector_builder.build()
        # We call the hook explicitly to trigger the FFI call
        assert verifier._broker_source_hook is not None  # noqa: SLF001
        verifier._broker_source_hook()  # noqa: SLF001

        # Verify FFI was called with correct selectors
        mock_ffi.assert_called_once()
        selectors = [json.loads(s) for s in mock_ffi.call_args[0][9]]

        assert len(selectors) == len(expected_selectors)
        for actual, expected in zip(selectors, expected_selectors, strict=True):
            assert actual == expected
            # For None value test case, verify excluded keys
            if "tag" not in expected and "latest" not in expected:
                assert "tag" not in actual
                assert "latest" not in actual
