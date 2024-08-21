"""
Pact Async Message Interaction unit tests.
"""

from __future__ import annotations

import re

import pytest

from pact.v3 import Pact


@pytest.fixture
def pact() -> Pact:
    """
    Fixture for a Pact instance.
    """
    return Pact("consumer", "provider")


def test_str(pact: Pact) -> None:
    interaction = pact.upon_receiving("a basic request", "Async")
    assert str(interaction) == "AsyncMessageInteraction(a basic request)"


def test_repr(pact: Pact) -> None:
    interaction = pact.upon_receiving("a basic request", "Async")
    assert (
        re.match(
            r"^AsyncMessageInteraction\(InteractionHandle\(\d+\)\)$",
            repr(interaction),
        )
        is not None
    )
