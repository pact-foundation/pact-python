"""Test the values in exported constants."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

import pact_cli

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    import pytest_mock


def bin_to_sitepackages(exec_path: str | Path) -> Path:
    """
    Find the expected site-packages directory for the given executable.
    """
    if os.name == "nt":
        return Path(exec_path).parents[1] / "Lib" / "site-packages"
    return (
        Path(exec_path).parents[1]
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    )


def assert_in_sys_path(p: str | Path) -> None:
    """
    Assert that a given path is in sys.path.

    This performs some normalization on platform where the filesystem is
    case-insensitive.
    """
    if os.name == "nt":
        assert str(p).lower() in (path.lower() for path in sys.path)
    else:
        assert str(p) in sys.path


@pytest.mark.parametrize(
    ("constant", "expected"),
    [
        pytest.param("PACT_PATH", "pact", id="pact"),
        pytest.param("BROKER_PATH", "pact-broker", id="pact-broker"),
        pytest.param("BROKER_CLIENT_PATH", "pact-broker", id="pact-broker"),
        pytest.param("MESSAGE_PATH", "pact-message", id="pactmessage"),
        pytest.param("MOCK_SERVICE_PATH", "pact-mock-service", id="pact-message"),
        pytest.param("PLUGIN_CLI_PATH", "pact-plugin-cli", id="pact-plugin-cli"),
        pytest.param(
            "VERIFIER_PATH", "pact-provider-verifier", id="pact-provider-verifier"
        ),
        pytest.param("STUB_SERVICE_PATH", "pact-stub-service", id="pact-stub-service"),
        pytest.param("PACTFLOW_PATH", "pactflow", id="pactflow"),
    ],
)
def test_constants(constant: str, expected: str) -> None:
    """Test the values of constants in pact.constants."""
    value: str = getattr(pact_cli, constant)
    if os.name == "nt":
        # As the Windows filesystem is case insensitive, we must normalize it.
        assert value.lower().endswith((f"{expected}.bat", f"{expected}.exe"))
    else:
        assert value.endswith(expected)


@pytest.mark.parametrize(
    "executable",
    [
        pytest.param("pact", id="pact"),
        pytest.param("pact-broker", id="pact-broker"),
        pytest.param("pact-message", id="pact-message"),
        pytest.param("pact-plugin-cli", id="pact-plugin-cli"),
        pytest.param("pact-provider-verifier", id="pact-provider-verifier"),
        pytest.param("pact-stub-service", id="pact-stub-service"),
        pytest.param("pactflow", id="pactflow"),
    ],
)
def test_exec_wrapper(executable: str) -> None:
    exec_path = shutil.which(executable)
    assert exec_path

    site_packages = bin_to_sitepackages(exec_path)
    assert site_packages.is_dir()
    assert_in_sys_path(site_packages)

    result = subprocess.run(  # noqa: S603
        [exec_path, "--help"],
        check=False,  # Some CLIs return non-zero for --help
        text=True,
        capture_output=True,
    )
    assert "pact" in (result.stdout + result.stderr).lower()

    result = subprocess.run(  # noqa: S603
        [exec_path],
        check=False,  # Some CLIs return non-zero for --help
        text=True,
        capture_output=True,
    )
    assert "pact" in (result.stdout + result.stderr).lower()


def test_exec_wrapper_mock_service() -> None:
    """
    Analogous to test_exec_wrapper, but specifically for pact-mock-service.

    This is necessary because pact-mock-service is a long running service, so we
    spawn the process, terminate it after a delay, and check the output.
    """
    executable = "pact-mock-service"
    exec_path = shutil.which(executable)
    assert exec_path
    site_packages = bin_to_sitepackages(exec_path)
    assert site_packages.is_dir()
    assert_in_sys_path(site_packages)

    process = subprocess.Popen(  # noqa: S603
        [exec_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    time.sleep(1)
    process.terminate()
    process.wait()

    stdout, stderr = process.communicate()
    assert "pact" in (stdout + stderr).lower()


@pytest.mark.parametrize(
    "executable",
    [
        pytest.param("pact", id="pact"),
        pytest.param("pact-broker", id="pact-broker"),
        pytest.param("pact-message", id="pact-message"),
        pytest.param("pact-mock-service", id="pact-mock-service"),
        pytest.param("pact-plugin-cli", id="pact-plugin-cli"),
        pytest.param("pact-provider-verifier", id="pact-provider-verifier"),
        pytest.param("pact-stub-service", id="pact-stub-service"),
        pytest.param("pactflow", id="pactflow"),
    ],
)
def test_exec_directly(executable: str, mocker: pytest_mock.MockerFixture) -> None:
    """
    Test pact_cli._exec with --help, mocking sys.argv and capturing output.
    """
    cmd: str
    args: list[str]

    mocker.patch.object(sys, "argv", new=[executable, "--help"])
    mock_execv: MagicMock = mocker.patch("os.execv")
    pact_cli._exec()  # noqa: SLF001
    mock_execv.assert_called_once()
    cmd, args = mock_execv.call_args[0]
    assert (os.sep + executable) in cmd
    assert args == [cmd, "--help"]

    mocker.patch.object(sys, "argv", new=[executable])
    mock_execv.reset_mock()
    pact_cli._exec()  # noqa: SLF001
    mock_execv.assert_called_once()
    cmd, args = mock_execv.call_args[0]
    assert (os.sep + executable) in cmd
    assert args == [cmd]
