"""
Locate and provide paths to bundled or system Pact CLI executables.

This module exists solely to bundle and distribute the Pact CLI tools as a
Python package. It does not provide any substantive functionality beyond
locating the Pact CLI executables and providing their paths for use in Python
code.

The module exposes constants for the absolute paths to the Pact CLI executables (such as
`pact-broker`, `pact-message`, `pact-mock-service`, and `pact-provider-verifier`).

By default, the module will use the binaries bundled with the package. If the
environment variable `PACT_USE_SYSTEM_BINS` is set to `TRUE` or `YES`, or if the bundled
binaries are unavailable, it will fall back to using the system-installed Pact CLI tools
if found in the system PATH.

This package is intended for use as a dependency to ensure the Pact CLI is available in
Python environments, such as CI pipelines or local development, without requiring a
separate installation step.

For more information, see the project README or
https://github.com/pact-foundation/pact-python.
"""

from __future__ import annotations

__author__ = "Pact Foundation"
__license__ = "MIT"
__url__ = "https://github.com/pact-foundation/pact-python"

import os
import shutil
import sys
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

from pact_cli.__version__ import (
    __version__ as __version__,
)
from pact_cli.__version__ import (
    __version_tuple__ as __version_tuple__,
)

if TYPE_CHECKING:
    from collections.abc import Container, Mapping

_USE_SYSTEM_BINS = os.getenv("PACT_USE_SYSTEM_BINS", "").upper() in ("TRUE", "YES")
_BIN_DIR = Path(__file__).parent.resolve() / "bin"
_LEGACY_BINS: Container[str] = frozenset((
    "pact-message",
    "pact-mock-service",
    "pact-provider-verifier",
    "pact-stub-service",
))


def _telemetry_env() -> Mapping[str, str]:
    """
    Get environment variables with Pact telemetry data.

    Returns a copy of the current environment with the following two keys added:

    -   `PACT_EXECUTING_LANGUAGE`: Set to "python".
    -   `PACT_EXECUTING_LANGUAGE_VERSION`: Set to the current Python version
        in "major.minor" format.

    Returns:
        Environment dictionary Pact telemetry added.
    """
    env = os.environ.copy()
    env["PACT_EXECUTING_LANGUAGE"] = "python"
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    env["PACT_EXECUTING_LANGUAGE_VERSION"] = version
    return env


def _exec() -> None:
    """
    Execute Pact CLI tools routed through the generated entry points.

    This function is exposed via `pyproject.toml` console scripts and forwards
    the provided command-line arguments to the matching Pact CLI binary.

    Raises:
        SystemExit:
            If the requested command is unknown or an executable cannot be
            located.
    """
    import sys  # noqa: PLC0415

    command = Path(sys.argv[0]).name
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if command not in (
        "pact",
        "pact-broker",
        "pact-message",
        "pact-mock-service",
        "pact-plugin-cli",
        "pact-provider-verifier",
        "pact-stub-server",
        "pact-stub-service",
        "pact_mock_server_cli",
        "pact_verifier_cli",
        "pactflow",
    ):
        print("Unknown command:", command, file=sys.stderr)  # noqa: T201
        sys.exit(1)

    if command in _LEGACY_BINS:
        warnings.warn(
            f"The '{command}' executable is deprecated and will be removed in "
            "a future release. Please migrate to the new Pact CLI tools. "
            "See: <https://github.com/pact-foundation/pact-standalone>",
            DeprecationWarning,
            stacklevel=2,
        )

    if not _USE_SYSTEM_BINS:
        executable = _find_executable(command)
    else:
        # To avoid finding the same executable, we have to process the PATH
        # variable and remove the current executable's directory.
        script_dir = Path(sys.argv[0]).parent.resolve()
        os.environ["PATH"] = os.pathsep.join(
            p
            for p in os.getenv("PATH", "").split(os.pathsep)
            if Path(p).resolve() != script_dir
        )
        executable = _find_executable(command)

    if not executable:
        print(f"Command '{command}' not found.", file=sys.stderr)  # noqa: T201
        sys.exit(1)

    os.execve(executable, [executable, *args], _telemetry_env())  # noqa: S606


def _find_executable(executable: str) -> str | None:
    """
    Find the path to an executable.

    This inspects the environment variable `PACT_USE_SYSTEM_BINS` to determine
    whether to use the bundled Pact binaries or the system ones. Note that if
    the local executables are not found, this will fall back to the system
    executables (if found).

    Args:
        executable:
            The name of the executable to find without the extension.  Python
            will automatically append the correct extension for the current
            platform.

    Returns:
        The absolute path to the executable.

    Warns:
        RuntimeWarning:
            If the executable cannot be found in the system path.
    """
    if _USE_SYSTEM_BINS:
        bin_path = shutil.which(executable)
    else:
        bin_path = shutil.which(executable, path=str(_BIN_DIR))
        if bin_path is None:
            system_path = shutil.which(executable)
            if system_path is not None:
                warnings.warn(
                    f"Bundled {executable} binary not found; "
                    "using system installation instead.",
                    RuntimeWarning,
                    stacklevel=2,
                )
            bin_path = system_path
    if bin_path is None:
        msg = f"Unable to find {executable} binary executable."
        warnings.warn(msg, RuntimeWarning, stacklevel=2)
    return bin_path


PACT_PATH = _find_executable("pact")
"""
Path to the Pact executable
"""
BROKER_PATH = _find_executable("pact-broker")
"""
Path to the Pact Broker executable
"""
BROKER_CLIENT_PATH = _find_executable("pact-broker")
"""
Path to the Pact Broker executable

This value is identical to `BROKER_PATH` and is provided for backward
compatibility.
"""
MESSAGE_PATH = _find_executable("pact-message")
"""
Path to the Pact Message executable
"""
MOCK_SERVICE_PATH = _find_executable("pact-mock-service")
"""
Path to the Pact Mock Service executable
"""
PLUGIN_CLI_PATH = _find_executable("pact-plugin-cli")
"""
Path to the Pact Plugin CLI executable
"""
VERIFIER_PATH = _find_executable("pact-provider-verifier")
"""
Path to the Pact Provider Verifier executable
"""
STUB_SERVER_PATH = _find_executable("pact-stub-server")
"""
Path to the Pact Stub Server executable
"""
STUB_SERVICE_PATH = _find_executable("pact-stub-service")
"""
Path to the Pact Stub Service executable
"""
MOCK_SERVER_PATH = _find_executable("pact_mock_server_cli")
"""
Path to the Pact Mock Server CLI executable
"""
VERIFIER_CLI_PATH = _find_executable("pact_verifier_cli")
"""
Path to the Pact Verifier CLI executable

This is distinct to the `VERIFIER_PATH` which points to the older Ruby-based
CLI.
"""
PACTFLOW_PATH = _find_executable("pactflow")
"""
Path to the PactFlow CLI executable
"""
