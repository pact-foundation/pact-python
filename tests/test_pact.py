"""
Pact unit tests.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal

import pytest

import pact_ffi
from pact import Pact
from pact_ffi import PactSpecification

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
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
        assert srv.port is not None
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
    with pytest.raises(
        ValueError,
        match=r"Invalid interaction type: .*",
    ):
        pact.upon_receiving("a basic request", "Invalid")  # type: ignore[call-overload]


@pytest.mark.parametrize(
    "interaction_type",
    [
        "HTTP",
        "Sync",
        "Async",
        "All",
    ],
)
def test_interactions_iter(
    pact: Pact,
    interaction_type: Literal[
        "HTTP",
        "Sync",
        "Async",
        "All",
    ],
) -> None:
    interactions = pact.interactions(interaction_type)
    assert interactions is not None
    for _interaction in interactions:
        # This should be an empty list and therefore the error should never be
        # raised.
        msg = "Should not be reached"
        raise RuntimeError(msg)


def test_write_file(pact: Pact, tmp_path: Path) -> None:
    pact.write_file(tmp_path)
    outfile = tmp_path / "consumer-provider.json"
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


def test_interactions_all_with_mixed_types(pact: Pact) -> None:
    pact.with_specification("V4")
    pact.upon_receiving("a request", "HTTP").with_request("GET", "/").will_respond_with(
        200
    )
    pact.upon_receiving("a message", "Async").with_body("{}")
    pact.upon_receiving("a sync message", "Sync").with_body(
        "request"
    ).will_respond_with().with_body("response")

    http_count = sum(1 for _ in pact.interactions("HTTP"))
    async_count = sum(1 for _ in pact.interactions("Async"))
    sync_count = sum(1 for _ in pact.interactions("Sync"))
    all_interactions = list(pact.interactions("All"))
    all_count = len(all_interactions)

    assert http_count == 1
    assert async_count == 1
    assert sync_count == 1
    assert all_count == 3

    # Verify the interactions can be iterated multiple times
    all_interactions_second = list(pact.interactions("All"))
    assert len(all_interactions_second) == 3

    # Verify each interaction type is represented in "All"
    http_found = False
    async_found = False
    sync_found = False

    for interaction in pact.interactions("All"):
        # Check string representation works
        str(interaction)
        repr(interaction)

        if isinstance(interaction, pact_ffi.SynchronousHttp):
            http_found = True
        elif isinstance(interaction, pact_ffi.AsynchronousMessage):
            async_found = True
        elif isinstance(interaction, pact_ffi.SynchronousMessage):
            sync_found = True

    assert http_found
    assert async_found
    assert sync_found


def test_interactions_all_with_only_http(pact: Pact) -> None:
    pact.with_specification("V4")
    pact.upon_receiving("request 1", "HTTP").with_request("GET", "/").will_respond_with(
        200
    )
    pact.upon_receiving("request 2", "HTTP").with_request(
        "POST", "/"
    ).will_respond_with(201)

    all_interactions = list(pact.interactions("All"))
    assert len(all_interactions) == 2


def test_interactions_all_with_only_async(pact: Pact) -> None:
    pact.with_specification("V4")
    pact.upon_receiving("message 1", "Async").with_body("{}")
    pact.upon_receiving("message 2", "Async").with_body("{}")

    all_interactions = list(pact.interactions("All"))
    assert len(all_interactions) == 2


def test_interactions_all_with_only_sync(pact: Pact) -> None:
    pact.with_specification("V4")
    pact.upon_receiving("sync 1", "Sync").with_body(
        "req1"
    ).will_respond_with().with_body("resp1")
    pact.upon_receiving("sync 2", "Sync").with_body(
        "req2"
    ).will_respond_with().with_body("resp2")

    all_interactions = list(pact.interactions("All"))
    assert len(all_interactions) == 2


def test_interactions_all_empty(pact: Pact) -> None:
    pact.with_specification("V4")
    all_interactions = list(pact.interactions("All"))
    assert len(all_interactions) == 0


def test_interactions_all_multiple_of_each_type(pact: Pact) -> None:
    """Test All iterator with multiple interactions of each type."""
    pact.with_specification("V4")

    # Create multiple HTTP interactions
    pact.upon_receiving("http 1", "HTTP").with_request("GET", "/1").will_respond_with(
        200
    )
    pact.upon_receiving("http 2", "HTTP").with_request("GET", "/2").will_respond_with(
        200
    )

    # Create multiple Async interactions
    pact.upon_receiving("async 1", "Async").with_body("{}")
    pact.upon_receiving("async 2", "Async").with_body("{}")

    # Create multiple Sync interactions
    pact.upon_receiving("sync 1", "Sync").with_body("r1").will_respond_with().with_body(
        "s1"
    )
    pact.upon_receiving("sync 2", "Sync").with_body("r2").will_respond_with().with_body(
        "s2"
    )

    # Count all interactions
    all_count = sum(1 for _ in pact.interactions("All"))
    assert all_count == 6

    # Verify we can iterate again
    all_count_second = sum(1 for _ in pact.interactions("All"))
    assert all_count_second == 6
