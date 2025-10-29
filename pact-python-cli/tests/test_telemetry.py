"""Tests for telemetry environment variables."""

from __future__ import annotations

import sys
from unittest.mock import patch

from pact_cli import _telemetry_env


def test_telemetry_env_sets_language() -> None:
    env = _telemetry_env()
    assert env["PACT_EXECUTING_LANGUAGE"] == "python"


def test_telemetry_env_sets_version() -> None:
    env = _telemetry_env()
    expected_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    assert env["PACT_EXECUTING_LANGUAGE_VERSION"] == expected_version


def test_telemetry_env_preserves_existing_env() -> None:
    mock_env = {"EXISTING_VAR": "existing_value", "PATH": "/usr/bin"}
    with patch("os.environ", mock_env):
        env = _telemetry_env()
        assert env["EXISTING_VAR"] == "existing_value"
        assert env["PATH"] == "/usr/bin"
        assert "PACT_EXECUTING_LANGUAGE" in env
        assert "PACT_EXECUTING_LANGUAGE_VERSION" in env


def test_telemetry_env_returns_copy() -> None:
    env1 = _telemetry_env()
    env2 = _telemetry_env()
    assert env1 is not env2
