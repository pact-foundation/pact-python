"""
Tests for `pact.types.URL`.
"""

from __future__ import annotations

import pytest

from pact.types import URL


@pytest.mark.parametrize(
    ("base", "segments", "expected"),
    [
        pytest.param("http://h:1", ["a"], "http://h:1/a", id="single"),
        pytest.param("http://h:1", ["a", "b"], "http://h:1/a/b", id="chained"),
        pytest.param("http://h:1", ["a/b"], "http://h:1/a/b", id="slash-in-segment"),
        pytest.param("http://h/a", ["b"], "http://h/a/b", id="base-without-slash"),
        pytest.param("http://h/a/", ["b"], "http://h/a/b", id="base-with-slash"),
        pytest.param("http://h:1", ["a b"], "http://h:1/a%20b", id="space"),
        pytest.param("http://h:1", ["a%20b"], "http://h:1/a%2520b", id="percent"),
        pytest.param("http://h:1", ["a?b"], "http://h:1/a%3Fb", id="question-mark"),
        pytest.param("http://h:1", ["a+b"], "http://h:1/a+b", id="plus"),
        pytest.param("http://h:1", [":@"], "http://h:1/:@", id="colon-at"),
        pytest.param("http://h:1/a", [""], "http://h:1/a", id="empty-segment"),
        pytest.param("http://h/a?x=1#f", ["b"], "http://h/a/b", id="drop-query"),
        pytest.param("http://u:p@h/", ["b"], "http://u:p@h/b", id="credentials"),
    ],
)
def test_truediv(base: str, segments: list[str], expected: str) -> None:
    url = URL(base)
    for segment in segments:
        url /= segment
    assert isinstance(url, URL)
    assert url == expected


def test_truediv_rejects_leading_slash() -> None:
    with pytest.raises(ValueError, match="starting with '/'"):
        _ = URL("http://h") / "/a"


def test_truediv_rejects_non_str() -> None:
    with pytest.raises(TypeError):
        _ = URL("http://h") / 1


@pytest.mark.parametrize(
    ("url", "scheme", "host", "port", "path"),
    [
        pytest.param(
            "http://localhost:1234", "http", "localhost", 1234, "/", id="port"
        ),
        pytest.param(
            "http://example.com/a", "http", "example.com", 80, "/a", id="http"
        ),
        pytest.param(
            "https://Example.com/", "https", "example.com", 443, "/", id="https"
        ),
        pytest.param("grpc://h/x", "grpc", "h", None, "/x", id="unknown-scheme"),
        pytest.param("http://[::1]:8080/", "http", "::1", 8080, "/", id="ipv6"),
    ],
)
def test_attributes(
    url: str,
    scheme: str,
    host: str,
    port: int | None,
    path: str,
) -> None:
    parsed = URL(url)
    assert parsed.scheme == scheme
    assert parsed.host == host
    assert parsed.port == port
    assert parsed.path == path


def test_str_behaviour() -> None:
    url = URL("http://h:1")
    assert isinstance(url, str)
    assert url == "http://h:1"
    assert f"{url}/a" == "http://h:1/a"
    assert str(url) == "http://h:1"
    assert type(str(url)) is str
    assert repr(url) == "URL('http://h:1')"


def test_hash_matches_str() -> None:
    url = URL("http://h:1")
    mapping: dict[str, int] = {url: 1}
    assert mapping["http://h:1"] == 1
    assert {url, "http://h:1"} == {"http://h:1"}
