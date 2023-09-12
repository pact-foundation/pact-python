"""Constant values for the pact-python package."""
import os
from pathlib import Path


def broker_client_exe() -> str:
    """Get the appropriate executable name for this platform."""
    if os.name == "nt":
        return "pact-broker.bat"
    return "pact-broker"


def message_exe() -> str:
    """Get the appropriate executable name for this platform."""
    if os.name == "nt":
        return "pact-message.bat"
    return "pact-message"


def mock_service_exe() -> str:
    """Get the appropriate executable name for this platform."""
    if os.name == "nt":
        return "pact-mock-service.bat"
    return "pact-mock-service"


def provider_verifier_exe() -> str:
    """Get the appropriate provider executable name for this platform."""
    if os.name == "nt":
        return "pact-provider-verifier.bat"
    return "pact-provider-verifier"


ROOT_DIR = Path(__file__).parent.resolve()
BROKER_CLIENT_PATH = ROOT_DIR / "bin" / broker_client_exe()
MESSAGE_PATH = ROOT_DIR / "bin" / message_exe()
MOCK_SERVICE_PATH = ROOT_DIR / "bin" / mock_service_exe()
VERIFIER_PATH = ROOT_DIR / "bin" / provider_verifier_exe()
