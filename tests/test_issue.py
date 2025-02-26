"""
Tests for user-reported issues.
"""

import os
from pathlib import Path

import pytest

from pact import MessageConsumer, Provider, matchers


def test_github_850_issue() -> None:
    """
    See https://github.com/pact-foundation/pact-python/issues/850.

    User reported an issue with Pact files not being written when using consumer
    and provider names with spaces. A warning was added to the code to alert the
    user that the names should not contain spaces.
    """
    contract = MessageConsumer("My Consumer").has_pact_with(
        Provider("My Provider"),
        pact_dir="pacts",
    )

    # Define os dados do evento
    event_data = {
        "invoice_id": "12345",
        "amount": 100.00,
        "currency": "USD",
        "created": matchers.Format().iso_8601_datetime(),
    }

    # Cria uma mensagem que representa o evento
    contract.given("Create contract").expects_to_receive(
        "An event of contract"
    ).with_content(event_data)

    with contract:
        pass

    pact_file = Path("pacts/my_consumer-my_provider.json")
    # The file should only be created on non-Windows systems
    assert pact_file.exists() == (os.name != "nt")


def test_github_850_fix(recwarn: pytest.WarningsRecorder) -> None:
    """
    See https://github.com/pact-foundation/pact-python/issues/850.

    User reported an issue with Pact files not being written when using consumer
    and provider names with spaces. A warning was added to the code to alert the
    user that the names should not contain spaces.
    """
    MessageConsumer("My Consumer").has_pact_with(
        Provider("My Provider"),
        pact_dir="pacts",
    )

    # Check for warnings
    warnings = [str(warning.message) for warning in recwarn]
    assert any(
        "Consumer name should not contain spaces." in warning for warning in warnings
    )
    assert any(
        "Provider name should not contain spaces." in warning for warning in warnings
    )
