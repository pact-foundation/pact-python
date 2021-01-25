"""Constant values for the pact-python package."""
import os
from os.path import join, dirname, normpath


def broker_client_exe():
    """Get the appropriate executable name for this platform."""
    if os.name == 'nt':
        return 'pact-broker.bat'
    else:
        return 'pact-broker'


def message_exe():
    """Get the appropriate executable name for this platform."""
    if os.name == 'nt':
        return 'pact-message.bat'
    else:
        return 'pact-message'


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


BROKER_CLIENT_PATH = normpath(join(
    dirname(__file__), 'bin', 'pact', 'bin', broker_client_exe()))

MESSAGE_PATH = normpath(join(
    dirname(__file__), 'bin', 'pact', 'bin', message_exe()))

MOCK_SERVICE_PATH = normpath(join(
    dirname(__file__), 'bin', 'pact', 'bin', mock_service_exe()))

VERIFIER_PATH = normpath(join(
    dirname(__file__), 'bin', 'pact', 'bin', provider_verifier_exe()))
