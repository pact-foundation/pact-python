"""
Pact Async Message Interaction unit tests.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

import pytest

from pact import Pact

if TYPE_CHECKING:
    from pathlib import Path


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


def test_add_external_reference(pact: Pact, tmp_path: Path) -> None:
    (
        pact
        .upon_receiving("an async message with an external reference", "Async")
        .add_external_reference(
            "GitHub",
            "PR-456",
            "https://github.com/org/repo/pull/456",
        )
        .with_body({"event": "user.created"})
    )
    pact.write_file(tmp_path)
    data = json.load((tmp_path / "consumer-provider.json").open())
    references = data["interactions"][0]["comments"]["references"]
    assert references["GitHub"]["PR-456"] == "https://github.com/org/repo/pull/456"
