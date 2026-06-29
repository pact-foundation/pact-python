"""Test the values in exported constants."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import sysconfig
import time
from pathlib import Path
from unittest.mock import patch

import pytest

import pact_cli


def bin_to_sitepackages(exec_path: str | Path) -> Path:
    """
    Compute the expected site-packages directory for a Pact executable.

    Args:
        exec_path:
            Path to the binary whose site-packages root should be derived.

    Returns:
        Path to the site-packages directory associated with the executable.
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
    Assert that a resolved path exists in ``sys.path``.

    This performs normalization on case-insensitive filesystems to avoid
    comparison errors.

    Args:
        p:
            Path that should be discoverable via `sys.path`.
    """
    if os.name == "nt":
        assert str(p).lower() in (path.lower() for path in sys.path)
    else:
        assert str(p) in sys.path


@pytest.mark.parametrize(
    ("constant", "expected"),
    [
        pytest.param("BROKER_CLIENT_PATH", "pact-broker", id="pact-broker"),
        pytest.param("BROKER_PATH", "pact-broker", id="pact-broker"),
        pytest.param("MESSAGE_PATH", "pact-message", id="pactmessage"),
        pytest.param(
            "MOCK_SERVER_PATH", "pact_mock_server_cli", id="pact_mock_server_cli"
        ),
        pytest.param("MOCK_SERVICE_PATH", "pact-mock-service", id="pact-mock-service"),
        pytest.param("PACTFLOW_PATH", "pactflow", id="pactflow"),
        pytest.param("PACT_PATH", "pact", id="pact"),
        pytest.param("PLUGIN_CLI_PATH", "pact-plugin-cli", id="pact-plugin-cli"),
        pytest.param("STUB_SERVER_PATH", "pact-stub-server", id="pact-stub-server"),
        pytest.param("STUB_SERVICE_PATH", "pact-stub-service", id="pact-stub-service"),
        pytest.param("VERIFIER_CLI_PATH", "pact_verifier_cli", id="pact_verifier_cli"),
        pytest.param(
            "VERIFIER_PATH", "pact-provider-verifier", id="pact-provider-verifier"
        ),
    ],
)
def test_constants_are_valid_executable_paths(constant: str, expected: str) -> None:
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
        pytest.param("pact-stub-server", id="pact-stub-server"),
        pytest.param("pact-stub-service", id="pact-stub-service"),
        pytest.param("pact_mock_server_cli", id="pact_mock_server_cli"),
        pytest.param("pact_verifier_cli", id="pact_verifier_cli"),
        pytest.param("pactflow", id="pactflow"),
    ],
)
def test_cli_exec_wrapper(executable: str) -> None:
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


def test_cli_exec_wrapper_for_mock_service() -> None:
    """
    Same as `test_cli_exec_wrapper` for the `pact-mock-server`.

    The Pact mock service is a long running service, as it is expected to run a
    mock service which can be tested against. The test pattern above doesn't
    work, and instead, we spawn the process, wait a bit, terminate it, and then
    check the output.
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
    time.sleep(2)
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
        pytest.param("pact-stub-server", id="pact-stub-server"),
        pytest.param("pact-stub-service", id="pact-stub-service"),
        pytest.param("pact_mock_server_cli", id="pact_mock_server_cli"),
        pytest.param("pact_verifier_cli", id="pact_verifier_cli"),
        pytest.param("pactflow", id="pactflow"),
    ],
)
def test_exec_directly(executable: str) -> None:
    """
    Invoke ``pact_cli._exec`` directly to confirm ``execv`` receives the command.
    """
    cmd: str
    args: list[str]

    with (
        patch.object(sys, "argv", new=[executable, "--help"]),
        patch("os.execve") as mock_execve,
    ):
        pact_cli._exec()  # noqa: SLF001
    mock_execve.assert_called_once()
    cmd, args, env = mock_execve.call_args[0]
    assert (os.sep + executable) in cmd
    assert args == [cmd, "--help"]
    assert env

    patch.object(sys, "argv", new=[executable])
    with (
        patch.object(sys, "argv", new=[executable]),
        patch("os.execve") as mock_execve,
    ):
        pact_cli._exec()  # noqa: SLF001
    mock_execve.assert_called_once()
    cmd, args, env = mock_execve.call_args[0]
    assert (os.sep + executable) in cmd
    assert args == [cmd]
    assert env


def test_deprecated_command_warns_with_replacement(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ruby commands with a Rust equivalent print a hint to stderr."""
    with (
        patch.object(sys, "argv", new=["pact-broker", "--help"]),
        patch("os.execve"),
    ):
        pact_cli._exec()  # noqa: SLF001
    captured = capsys.readouterr()
    assert "deprecated" in captured.err
    assert "pact broker" in captured.err


def test_deprecated_command_warns_without_replacement(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ruby commands without a Rust equivalent print a generic warning."""
    with (
        patch.object(sys, "argv", new=["pact-message", "--help"]),
        patch("os.execve"),
    ):
        pact_cli._exec()  # noqa: SLF001
    captured = capsys.readouterr()
    assert "deprecated" in captured.err
    assert "Use " not in captured.err  # no replacement hint


def test_pact_command_does_not_warn(capsys: pytest.CaptureFixture[str]) -> None:
    """The Rust pact binary does not trigger any deprecation warning."""
    with (
        patch.object(sys, "argv", new=["pact", "--help"]),
        patch("os.execve"),
    ):
        pact_cli._exec()  # noqa: SLF001
    captured = capsys.readouterr()
    assert "deprecated" not in captured.err


def test_find_executable_resolves_via_sysconfig(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Bundled binaries are found via the install location, not just `__file__`.

    This reproduces the cross-checkout failure: a virtual environment is reused
    across multiple checkouts, so the module-relative `bin` directory (derived
    from `__file__`) points at a location that no longer contains the binary.
    The binary remains discoverable through the install's `site-packages`
    location reported by `sysconfig`.
    """
    # The module-relative bin directory exists but does not contain the binary.
    empty_bin = tmp_path / "stale" / "pact_cli" / "bin"
    empty_bin.mkdir(parents=True)
    monkeypatch.setattr(pact_cli, "_BIN_DIR", empty_bin)
    monkeypatch.setattr(pact_cli, "_USE_SYSTEM_BINS", False)

    # The binary is only present in the install's site-packages bin directory.
    site_packages = tmp_path / "site-packages"
    real_bin = site_packages / "pact_cli" / "bin"
    real_bin.mkdir(parents=True)
    name = "pact.exe" if os.name == "nt" else "pact"
    binary = real_bin / name
    binary.write_text("")
    binary.chmod(0o755)

    monkeypatch.setattr(
        sysconfig,
        "get_path",
        lambda key, *_args, **_kwargs: (
            str(site_packages) if key in ("platlib", "purelib") else None
        ),
    )
    # Ensure the binary is not discoverable on PATH.
    monkeypatch.setenv("PATH", str(tmp_path / "nonexistent"))

    found = pact_cli._find_executable("pact")  # noqa: SLF001
    assert found is not None
    assert Path(found).resolve() == binary.resolve()
