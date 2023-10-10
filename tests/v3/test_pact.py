"""
Pact unit tests.
"""

from __future__ import annotations

import json

import aiohttp
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


@pytest.mark.parametrize(
    "method",
    [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "HEAD",
        "OPTIONS",
        "TRACE",
        "CONNECT",
    ],
)
@pytest.mark.asyncio()
async def test_basic_request_method(pact: Pact, method: str) -> None:
    (
        pact.upon_receiving(f"a basic {method} request")
        .with_request(method, "/")
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(method, "/") as resp:
                assert resp.status == 200


@pytest.mark.parametrize(
    "status",
    list(range(200, 600, 13)),
)
@pytest.mark.asyncio()
async def test_basic_response_status(pact: Pact, status: int) -> None:
    (
        pact.upon_receiving(f"a basic request producing status {status}")
        .with_request("GET", "/")
        .will_respond_with(status)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request("GET", "/") as resp:
                assert resp.status == status


@pytest.mark.parametrize(
    "headers",
    [
        [("X-Test", "true")],
        [("X-Foo", "true"), ("X-Bar", "true")],
        [("X-Test", "1"), ("X-Test", "2")],
    ],
)
@pytest.mark.asyncio()
async def test_with_header_request(
    pact: Pact,
    headers: list[tuple[str, str]],
) -> None:
    (
        pact.upon_receiving("a basic request with a header")
        .with_request("GET", "/")
        .with_headers(headers)
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/",
                headers=headers,
            ) as resp:
                assert resp.status == 200


@pytest.mark.parametrize(
    "headers",
    [
        [("X-Test", "true")],
        [("X-Foo", "true"), ("X-Bar", "true")],
        [("X-Test", "1"), ("X-Test", "2")],
    ],
)
@pytest.mark.asyncio()
async def test_with_header_response(
    pact: Pact,
    headers: list[tuple[str, str]],
) -> None:
    (
        pact.upon_receiving("a basic request with a header")
        .with_request("GET", "/")
        .will_respond_with(200)
        .with_headers(headers)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/",
            ) as resp:
                assert resp.status == 200
                response_headers = [(h.lower(), v) for h, v in resp.headers.items()]
                for header, value in headers:
                    assert (header.lower(), value) in response_headers


@pytest.mark.asyncio()
async def test_with_header_dict(pact: Pact) -> None:
    (
        pact.upon_receiving("a basic request with a headers from a dict")
        .with_request("GET", "/")
        .with_headers({"X-Test": "true", "X-Foo": "bar"})
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/",
                headers={"X-Test": "true", "X-Foo": "bar"},
            ) as resp:
                assert resp.status == 200


@pytest.mark.parametrize(
    "headers",
    [
        [("X-Test", "true")],
        [("X-Foo", "true"), ("X-Bar", "true")],
    ],
)
@pytest.mark.asyncio()
async def test_set_header_request(
    pact: Pact,
    headers: list[tuple[str, str]],
) -> None:
    (
        pact.upon_receiving("a basic request with a header")
        .with_request("GET", "/")
        .set_headers(headers)
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/",
                headers=headers,
            ) as resp:
                assert resp.status == 200


@pytest.mark.asyncio()
async def test_set_header_request_repeat(
    pact: Pact,
) -> None:
    headers = [("X-Test", "1"), ("X-Test", "2")]
    (
        pact.upon_receiving("a basic request with a header")
        .with_request("GET", "/")
        # As set_headers makes no additional processing, the last header will be
        # the one that is used.
        .set_headers(headers)
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/",
                headers=headers,
            ) as resp:
                assert resp.status == 500


@pytest.mark.parametrize(
    "headers",
    [
        [("X-Test", "true")],
        [("X-Foo", "true"), ("X-Bar", "true")],
    ],
)
@pytest.mark.asyncio()
async def test_set_header_response(
    pact: Pact,
    headers: list[tuple[str, str]],
) -> None:
    (
        pact.upon_receiving("a basic request with a header")
        .with_request("GET", "/")
        .will_respond_with(200)
        .set_headers(headers)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/",
            ) as resp:
                assert resp.status == 200
                response_headers = [(h.lower(), v) for h, v in resp.headers.items()]
                for header, value in headers:
                    assert (header.lower(), value) in response_headers


@pytest.mark.asyncio()
async def test_set_header_response_repeat(
    pact: Pact,
) -> None:
    headers = [("X-Test", "1"), ("X-Test", "2")]
    (
        pact.upon_receiving("a basic request with a header")
        .with_request("GET", "/")
        .will_respond_with(200)
        # As set_headers makes no additional processing, the last header will be
        # the one that is used.
        .set_headers(headers)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/",
                headers=headers,
            ) as resp:
                assert resp.status == 200
                response_headers = [(h.lower(), v) for h, v in resp.headers.items()]
                assert ("x-test", "2") in response_headers
                assert ("x-test", "1") not in response_headers


@pytest.mark.asyncio()
async def test_set_header_dict(pact: Pact) -> None:
    (
        pact.upon_receiving("a basic request with a headers from a dict")
        .with_request("GET", "/")
        .set_headers({"X-Test": "true", "X-Foo": "bar"})
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/",
                headers={"X-Test": "true", "X-Foo": "bar"},
            ) as resp:
                assert resp.status == 200


@pytest.mark.parametrize(
    "query",
    [
        [("test", "true")],
        [("foo", "true"), ("bar", "true")],
        [("test", "1"), ("test", "2")],
    ],
)
@pytest.mark.asyncio()
async def test_with_query_parameter_request(
    pact: Pact,
    query: list[tuple[str, str]],
) -> None:
    (
        pact.upon_receiving("a basic request with a query parameter")
        .with_request("GET", "/")
        .with_query_parameters(query)
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            url = srv.url.with_query(query)
            async with session.request(
                "GET",
                url.path_qs,
            ) as resp:
                assert resp.status == 200


@pytest.mark.asyncio()
async def test_with_query_parameter_dict(pact: Pact) -> None:
    (
        pact.upon_receiving("a basic request with a query parameter from a dict")
        .with_request("GET", "/")
        .with_query_parameters({"test": "true", "foo": "bar"})
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            url = srv.url.with_query({"test": "true", "foo": "bar"})
            async with session.request(
                "GET",
                url.path_qs,
            ) as resp:
                assert resp.status == 200


@pytest.mark.parametrize(
    "method",
    ["GET", "POST", "PUT"],
)
@pytest.mark.asyncio()
async def test_with_body_request(pact: Pact, method: str) -> None:
    (
        pact.upon_receiving(f"a basic {method} request with a body")
        .with_request(method, "/")
        .with_body(json.dumps({"test": True}), "application/json")
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                method,
                "/",
                json={"test": True},
            ) as resp:
                assert resp.status == 200


@pytest.mark.parametrize(
    "method",
    ["GET", "POST", "PUT"],
)
@pytest.mark.asyncio()
async def test_with_body_response(pact: Pact, method: str) -> None:
    (
        pact.upon_receiving(
            f"a basic {method} request expecting a response with a body",
        )
        .with_request(method, "/")
        .will_respond_with(200)
        .with_body(json.dumps({"test": True}), "application/json")
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                method,
                "/",
                json={"test": True},
            ) as resp:
                assert resp.status == 200
                assert await resp.json() == {"test": True}


@pytest.mark.asyncio()
async def test_with_body_explicit(pact: Pact) -> None:
    (
        pact.upon_receiving("")
        .with_request("GET", "/")
        .will_respond_with(200)
        .with_body(json.dumps({"request": True}), "application/json", "Request")
        .with_body(json.dumps({"response": True}), "application/json", "Response")
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/",
                json={"request": True},
            ) as resp:
                assert resp.status == 200
                assert await resp.json() == {"response": True}


def test_with_body_invalid(pact: Pact) -> None:
    with pytest.raises(ValueError, match="Invalid part: Invalid"):
        (
            pact.upon_receiving("")
            .with_request("GET", "/")
            .will_respond_with(200)
            .with_body(json.dumps({"request": True}), "application/json", "Invalid")
        )


@pytest.mark.asyncio()
async def test_given(pact: Pact) -> None:
    (
        pact.upon_receiving("a basic request given state 1")
        .given("state 1")
        .with_request("GET", "/")
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request("GET", "/") as resp:
                assert resp.status == 200
