"""
Pact unit tests.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal

import pytest

from pact.v3 import Pact
from pact.v3.ffi import PactSpecification

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture()
def pact() -> Pact:
    """
    Fixture for a Pact instance.
    """
    return Pact("consumer", "provider")


def test_init(pact: Pact) -> None:
    assert pact.consumer == "consumer"
    assert pact.provider == "provider"
    assert str(pact) == "consumer -> provider"
    assert repr(pact).startswith("<Pact:")
    assert repr(pact).endswith(">")


def test_empty_consumer() -> None:
    with pytest.raises(ValueError, match="Consumer name cannot be empty"):
        Pact("", "provider")


def test_empty_provider() -> None:
    with pytest.raises(ValueError, match="Provider name cannot be empty"):
        Pact("consumer", "")


def test_serve(pact: Pact) -> None:
    with pact.serve() as srv:
        assert srv.port > 0
        assert srv.host == "localhost"
        assert str(srv).startswith("http://localhost")
        assert srv.url.scheme == "http"
        assert srv.url.host == "localhost"
        assert srv.url.path == "/"
        assert srv / "foo" == srv.url / "foo"
        assert str(srv / "foo") == f"http://localhost:{srv.port}/foo"


@pytest.mark.skip(reason="TODO: implement")
def test_using_plugin(pact: Pact) -> None:
    pact.using_plugin("core/transport/http")


def test_metadata(pact: Pact) -> None:
    pact.with_metadata("test", {"version": "1.2.3", "hash": "abcdef"})


def test_invalid_interaction(pact: Pact) -> None:
    with pytest.raises(ValueError, match="Invalid interaction type: .*"):
        pact.upon_receiving("a basic request", "Invalid")  # type: ignore[call-overload]


@pytest.mark.parametrize(
    "interaction_type",
    [
        "HTTP",
        "Sync",
        "Async",
    ],
)
def test_interactions_iter(
    pact: Pact,
    interaction_type: Literal[
        "HTTP",
        "Sync",
        "Async",
    ],
) -> None:
    interactions = pact.interactions(interaction_type)
    assert interactions is not None
    for _interaction in interactions:
        # This should be an empty list and therefore the error should never be
        # raised.
        msg = "Should not be reached"
        raise RuntimeError(msg)


def test_write_file(pact: Pact, temp_dir: Path) -> None:
    pact.write_file(temp_dir)
    outfile = temp_dir / "consumer-provider.json"
    assert outfile.exists()
    assert outfile.is_file()

    data = json.load(outfile.open("r"))
    assert data["consumer"]["name"] == "consumer"
    assert data["provider"]["name"] == "provider"
    assert len(data["interactions"]) == 0


@pytest.mark.parametrize(
    "version",
    [
        "1",
        "1.1",
        "2",
        "3",
        "4",
        "V1",
        "V1.1",
        "V2",
        "V3",
        "V4",
    ],
)
def test_specification(pact: Pact, version: str) -> None:
    pact.with_specification(version)
    assert pact.specification == PactSpecification.from_str(version)


def test_server_log(pact: Pact) -> None:
    with pact.serve() as srv:
        assert srv.logs is not None
