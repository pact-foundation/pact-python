"""
Pact unit tests.
"""

from __future__ import annotations

import itertools
import json
from typing import TYPE_CHECKING, Literal

import pytest

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


class TestInteractionsIter:
    """
    Collection of for `pact.interactions` iterator tests.
    """

    @staticmethod
    def _interaction_count(
        pact: Pact,
        interaction_type: Literal["HTTP", "Sync", "Async", "All"],
    ) -> int:
        """
        Count the number of interactions for the requested type.

        Args:
            pact:
                Pact instance under test.

            interaction_type:
                Interaction type to count (HTTP, Async, Sync, All).

        Returns:
            Number of interactions that match the provided type.
        """
        return sum(1 for _ in pact.interactions(interaction_type))

    @pytest.mark.parametrize(
        "interaction_type",
        [
            "HTTP",
            "Sync",
            "Async",
            "All",
        ],
    )
    def test_empty(
        self,
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

    @classmethod
    def _add_http_interaction(cls, pact: Pact, id_: int) -> None:
        (
            pact
            .upon_receiving(f"HTTP request {id_}", "HTTP")
            .with_request("GET", f"/{id_}")
            .will_respond_with(200)
        )

    @classmethod
    def _add_async_interaction(cls, pact: Pact, id_: int) -> None:
        (pact.upon_receiving(f"Async message {id_}", "Async").with_body({"count": id_}))

    @classmethod
    def _add_sync_interaction(cls, pact: Pact, id_: int) -> None:
        (
            pact
            .upon_receiving(f"Sync message {id_}", "Sync")
            .with_body(f"request {id_}")
            .will_respond_with()
            .with_body(f"response {id_}")
        )

    @classmethod
    def _add_interactions(cls, pact: Pact, id_: int) -> None:
        cls._add_http_interaction(pact, id_)
        cls._add_async_interaction(pact, id_)
        cls._add_sync_interaction(pact, id_)

    @pytest.mark.parametrize(
        "version",
        ["1", "1.1", "2", "3", "4"],
    )
    def test_pact_versions(self, pact: Pact, version: str) -> None:
        pact.with_specification(version)
        self._add_interactions(pact, 1)

        assert self._interaction_count(pact, "HTTP") == 1
        assert self._interaction_count(pact, "Async") == 1
        assert self._interaction_count(pact, "Sync") == 1
        assert self._interaction_count(pact, "All") == 3

    @pytest.mark.parametrize(
        ("version", "http", "async_", "sync"),
        itertools.product(["1", "1.1", "2", "3", "4"], range(3), range(3), range(3)),
    )
    def test_mixed_interactions(
        self,
        pact: Pact,
        version: str,
        http: int,
        async_: int,
        sync: int,
    ) -> None:
        pact.with_specification(version)
        for i in range(http):
            self._add_http_interaction(pact, i)
        for i in range(async_):
            self._add_async_interaction(pact, i)
        for i in range(sync):
            self._add_sync_interaction(pact, i)

        # Verify the expected counts
        assert self._interaction_count(pact, "HTTP") == http
        assert self._interaction_count(pact, "Async") == async_
        assert self._interaction_count(pact, "Sync") == sync
        assert self._interaction_count(pact, "All") == (http + async_ + sync)

        # Verify repeated iteration works
        assert self._interaction_count(pact, "HTTP") == http
        assert self._interaction_count(pact, "Async") == async_
        assert self._interaction_count(pact, "Sync") == sync
        assert self._interaction_count(pact, "All") == (http + async_ + sync)
