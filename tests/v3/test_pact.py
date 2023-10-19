"""
Pact unit tests.
"""

from __future__ import annotations

import pytest
from pact.v3 import Pact


@pytest.fixture()
def pact() -> Pact:
    """
    Fixture for a Pact instance.
    """
    return Pact("consumer", "provider")


def test_init(pact: Pact) -> None:
    assert pact.consumer == "consumer"
    assert pact.provider == "provider"


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
