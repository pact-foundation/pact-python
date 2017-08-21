"""Constant values for the pact-python package."""
import os
from os.path import join, dirname, normpath


def mock_service_exe():
    """Get the appropriate executable name for this platform."""
    if os.name == 'nt':
        return 'pact-mock-service.bat'
    else:
        return 'pact-mock-service'


def provider_verifier_exe():
    """Get the appropriate provider executable name for this platform."""
    if os.name == 'nt':
        return 'pact-provider-verifier.bat'
    else:
        return 'pact-provider-verifier'


MOCK_SERVICE_PATH = normpath(join(
    dirname(__file__), 'bin', 'pact', 'bin', mock_service_exe()))

VERIFIER_PATH = normpath(join(
    dirname(__file__), 'bin', 'pact', 'bin', provider_verifier_exe()))
