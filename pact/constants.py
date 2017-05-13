"""Constant values for the pact-python package."""
import os
from os.path import join, dirname, normpath


def mock_service_exe():
    """Get the appropriate executable name for this platform."""
    if os.name == 'nt':
        return 'pact-mock-service.bat'
    else:
        return 'pact-mock-service'


MOCK_SERVICE_PATH = normpath(join(
    dirname(__file__), 'bin', 'mock-service', 'bin', mock_service_exe()))
