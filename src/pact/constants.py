"""
Constant values for the pact-python package.

This will default to the bundled Pact binaries bundled with the package, but
should these be unavailable or the environment variable `PACT_USE_SYSTEM_BINS` is
set to `TRUE` or `YES`, the system Pact binaries will be used instead.
"""
import os
import shutil
import warnings
from pathlib import Path

_USE_SYSTEM_BINS = os.getenv("PACT_USE_SYSTEM_BINS", "").upper() in ("TRUE", "YES")
_BIN_DIR = Path(__file__).parent.resolve() / "bin"


def _find_executable(executable: str) -> str:
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
        bin_path = shutil.which(executable, path=_BIN_DIR) or shutil.which(executable)
    if bin_path is None:
        msg = f"Unable to find {executable} binary executable."
        warnings.warn(msg, RuntimeWarning, stacklevel=2)
    return bin_path or ""


BROKER_CLIENT_PATH = _find_executable("pact-broker")
MESSAGE_PATH = _find_executable("pact-message")
MOCK_SERVICE_PATH = _find_executable("pact-mock-service")
VERIFIER_PATH = _find_executable("pact-provider-verifier")
