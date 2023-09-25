"""Test the values in pact.constants."""

import os


def test_broker_client() -> None:
    """Test the value of BROKER_CLIENT_PATH on POSIX."""
    import pact.constants

    if os.name == "nt":
        # As the Windows filesystem is case insensitive, we must normalize it.
        assert pact.constants.BROKER_CLIENT_PATH.lower().endswith("pact-broker.bat")
    else:
        assert pact.constants.BROKER_CLIENT_PATH.endswith("pact-broker")


def test_message() -> None:
    """Test the value of MESSAGE_PATH on POSIX."""
    import pact.constants

    if os.name == "nt":
        # As the Windows filesystem is case insensitive, we must normalize it.
        assert pact.constants.MESSAGE_PATH.lower().endswith("pact-message.bat")
    else:
        assert pact.constants.MESSAGE_PATH.endswith("pact-message")


def test_mock_service() -> None:
    """Test the value of MOCK_SERVICE_PATH on POSIX."""
    import pact.constants

    if os.name == "nt":
        # As the Windows filesystem is case insensitive, we must normalize it.
        assert pact.constants.MOCK_SERVICE_PATH.lower().endswith(
            "pact-mock-service.bat",
        )
    else:
        assert pact.constants.MOCK_SERVICE_PATH.endswith("pact-mock-service")


def test_verifier() -> None:
    """Test the value of VERIFIER_PATH on POSIX."""
    import pact.constants

    if os.name == "nt":
        # As the Windows filesystem is case insensitive, we must normalize it.
        assert pact.constants.VERIFIER_PATH.lower().endswith(
            "pact-provider-verifier.bat",
        )
    else:
        assert pact.constants.VERIFIER_PATH.endswith("pact-provider-verifier")
