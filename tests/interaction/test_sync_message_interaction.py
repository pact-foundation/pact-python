"""
Pact Sync Message Interaction unit tests.
"""

from __future__ import annotations

import re
from unittest.mock import MagicMock

import pytest

from pact import Pact


@pytest.fixture
def pact() -> Pact:
    """
    Fixture for a Pact instance.
    """
    return Pact("consumer", "provider").with_specification("V4")


def test_str(pact: Pact) -> None:
    interaction = pact.upon_receiving("a basic request", "Sync")
    assert str(interaction) == "SyncMessageInteraction(a basic request)"


def test_repr(pact: Pact) -> None:
    interaction = pact.upon_receiving("a basic request", "Sync")
    assert (
        re.match(
            r"^SyncMessageInteraction\(InteractionHandle\(\d+\)\)$",
            repr(interaction),
        )
        is not None
    )


def test_with_metadata_with_positional_dict(pact: Pact) -> None:
    (
        pact.upon_receiving("with_metadatadict", "Sync")
        .with_body("request", content_type="text/plain")
        .with_metadata({"foo": "bar"})
        .will_respond_with()
        .with_body("response", content_type="text/plain")
    )
    handler = MagicMock()
    handler.return_value = "response"
    pact.verify(handler, "Sync")
    handler.assert_called_once()
    assert "foo" in handler.call_args[0][1]
    assert handler.call_args[0][1]["foo"] == "bar"


def test_with_metadata_with_keyword_args(pact: Pact) -> None:
    (
        pact.upon_receiving("with_metadata_kwargs", "Sync")
        .with_body("request", content_type="text/plain")
        .with_metadata(foo="bar")
        .will_respond_with()
        .with_body("response", content_type="text/plain")
    )
    handler = MagicMock()
    handler.return_value = "response"
    pact.verify(handler, "Sync")
    handler.assert_called_once()
    assert "foo" in handler.call_args[0][1]
    assert handler.call_args[0][1]["foo"] == "bar"


def test_with_metadata_with_mixed_args(pact: Pact) -> None:
    (
        pact.upon_receiving("with_metadata_mixed", "Sync")
        .with_body("request", content_type="text/plain")
        .with_metadata({"foo": {"bar": 1.23}}, metadata=123)
        .will_respond_with()
        .with_body("response", content_type="text/plain")
    )
    handler = MagicMock()
    handler.return_value = "response"
    pact.verify(handler, "Sync")
    handler.assert_called_once()
    assert "foo" in handler.call_args[0][1]
    assert handler.call_args[0][1]["foo"] == {"bar": 1.23}
    assert "metadata" in handler.call_args[0][1]
    assert handler.call_args[0][1]["metadata"] == 123


def test_with_metadata_with_part(pact: Pact) -> None:
    (
        pact.upon_receiving("with_metadata_part", "Sync")
        .with_body("request", content_type="text/plain")
        .will_respond_with()
        .with_body("response", content_type="text/plain")
        .with_metadata({"foo": {"bar": 1.23}}, "Request", metadata=123)
    )
    handler = MagicMock()
    handler.return_value = "response"
    pact.verify(handler, "Sync")
    handler.assert_called_once()
    assert "foo" in handler.call_args[0][1]
    assert handler.call_args[0][1]["foo"] == {"bar": 1.23}
    assert "metadata" in handler.call_args[0][1]
    assert handler.call_args[0][1]["metadata"] == 123
