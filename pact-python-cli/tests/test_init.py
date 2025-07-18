"""Test the values in exported constants."""

import os

import pytest

import pact_cli


@pytest.mark.parametrize(
    ("constant", "expected"),
    [
        pytest.param("PACT_PATH", "pact", id="pact"),
        pytest.param("BROKER_PATH", "pact-broker", id="pact-broker"),
        pytest.param("BROKER_CLIENT_PATH", "pact-broker", id="pact-broker"),
        pytest.param("MESSAGE_PATH", "pact-message", id="pactmessage"),
        pytest.param("MOCK_SERVICE_PATH", "pact-mock-service", id="pact-message"),
        pytest.param("PLUGIN_CLI_PATH", "pact-plugin-cli", id="pact-plugin-cli"),
        pytest.param("VERIFIER_PATH", "pact-provider-verifier", id="pact-verifier"),
        pytest.param("PUBLISH_PATH", "pact-publish", id="pact-publish"),
        pytest.param("STUB_SERVICE_PATH", "pact-stub-service", id="pact-stub-service"),
        pytest.param("PACTFLOW_PATH", "pactflow", id="pactflow"),
    ],
)
def test_constants(constant: str, expected: str) -> None:
    """Test the values of constants in pact.constants."""
    value = getattr(pact_cli, constant)
    if os.name == "nt":
        # As the Windows filesystem is case insensitive, we must normalize it.
        assert value.lower().endswith(f"{expected}.bat")
    else:
        assert value.endswith(expected)
