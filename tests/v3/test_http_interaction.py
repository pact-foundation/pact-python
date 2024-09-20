"""
Pact Http Interaction unit tests.
"""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING

import aiohttp
import pytest

from pact.v3 import Pact, match
from pact.v3.error import RequestMismatch, RequestNotFound
from pact.v3.pact import MismatchesError

if TYPE_CHECKING:
    from pathlib import Path

ALL_HTTP_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
    "TRACE",
    "CONNECT",
]


@pytest.fixture
def pact() -> Pact:
    """
    Fixture for a Pact instance.
    """
    return Pact("consumer", "provider")


def test_str(pact: Pact) -> None:
    interaction = pact.upon_receiving("a basic request")
    assert str(interaction) == "HttpInteraction(a basic request)"


def test_repr(pact: Pact) -> None:
    interaction = pact.upon_receiving("a basic request")
    assert (
        re.match(r"^HttpInteraction\(InteractionHandle\(\d+\)\)$", repr(interaction))
        is not None
    )


@pytest.mark.parametrize(
    "method",
    ALL_HTTP_METHODS,
)
@pytest.mark.asyncio
async def test_basic_request_method(pact: Pact, method: str) -> None:
    (
        pact.upon_receiving(f"a basic {method} request")
        .with_request(method, "/")
        .will_respond_with(200)
    )
    with pact.serve(raises=False) as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            for m in ALL_HTTP_METHODS:
                async with session.request(m, "/") as resp:
                    assert resp.status == (200 if m == method else 500)

        # As we are making unexpected requests, we should have mismatches
        for mismatch in srv.mismatches:
            assert isinstance(mismatch, RequestNotFound)


@pytest.mark.parametrize(
    "status",
    list(range(200, 600, 13)),
)
@pytest.mark.asyncio
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
@pytest.mark.asyncio
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
            async with session.request("GET", "/", headers=headers) as resp:
                assert resp.status == 200


@pytest.mark.parametrize(
    "headers",
    [
        [("X-Test", "true")],
        [("X-Foo", "true"), ("X-Bar", "true")],
        [("X-Test", "1"), ("X-Test", "2")],
    ],
)
@pytest.mark.asyncio
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
            async with session.request("GET", "/") as resp:
                assert resp.status == 200
                response_headers = [(h.lower(), v) for h, v in resp.headers.items()]
                for header, value in headers:
                    assert (header.lower(), value) in response_headers


@pytest.mark.asyncio
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
@pytest.mark.asyncio
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
            async with session.request("GET", "/", headers=headers) as resp:
                assert resp.status == 200


@pytest.mark.asyncio
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
    with pact.serve(raises=False) as srv:
        async with (
            aiohttp.ClientSession(srv.url) as session,
            session.request(
                "GET",
                "/",
                headers=headers,
            ) as resp,
        ):
            assert resp.status == 500

        assert len(srv.mismatches) == 1
        assert isinstance(srv.mismatches[0], RequestMismatch)


@pytest.mark.parametrize(
    "headers",
    [
        [("X-Test", "true")],
        [("X-Foo", "true"), ("X-Bar", "true")],
    ],
)
@pytest.mark.asyncio
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
            async with session.request("GET", "/") as resp:
                assert resp.status == 200
                response_headers = [(h.lower(), v) for h, v in resp.headers.items()]
                for header, value in headers:
                    assert (header.lower(), value) in response_headers


@pytest.mark.asyncio
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
            async with session.request("GET", "/", headers=headers) as resp:
                assert resp.status == 200
                response_headers = [(h.lower(), v) for h, v in resp.headers.items()]
                assert ("x-test", "2") in response_headers
                assert ("x-test", "1") not in response_headers


@pytest.mark.asyncio
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
@pytest.mark.asyncio
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
            async with session.request("GET", url.path_qs) as resp:
                assert resp.status == 200


@pytest.mark.asyncio
async def test_with_query_parameter_with_matcher(
    pact: Pact,
) -> None:
    (
        pact.upon_receiving("a basic request with a query parameter")
        .with_request("GET", "/")
        .with_query_parameter("test", match.string("true"))
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            url = srv.url.with_query([("test", "true")])
            async with session.request("GET", url.path_qs) as resp:
                assert resp.status == 200


@pytest.mark.asyncio
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
            async with session.request("GET", url.path_qs) as resp:
                assert resp.status == 200


@pytest.mark.asyncio
async def test_with_query_parameter_tuple_list(pact: Pact) -> None:
    (
        pact.upon_receiving("a basic request with a query parameter from a dict")
        .with_request("GET", "/")
        .with_query_parameters([("test", "true"), ("foo", "bar")])
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            url = srv.url.with_query({"test": "true", "foo": "bar"})
            async with session.request("GET", url.path_qs) as resp:
                assert resp.status == 200


@pytest.mark.parametrize(
    "method",
    ["GET", "POST", "PUT"],
)
@pytest.mark.asyncio
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
@pytest.mark.asyncio
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
                assert json.loads(await resp.content.read()) == {"test": True}


@pytest.mark.asyncio
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
                assert json.loads(await resp.content.read()) == {"response": True}


def test_with_body_invalid(pact: Pact) -> None:
    with pytest.raises(ValueError, match="Invalid part: Invalid"):
        (
            pact.upon_receiving("")
            .with_request("GET", "/")
            .will_respond_with(200)
            .with_body(
                json.dumps({"request": True}),
                "application/json",
                "Invalid",  # type: ignore[arg-type]
            )
        )


@pytest.mark.asyncio
async def test_given(pact: Pact) -> None:
    (
        pact.upon_receiving("a basic request given state 1")
        .given("state 1")
        .with_request("GET", "/state")
        .will_respond_with(200)
    )
    (
        pact.upon_receiving("a basic request given a user exists (1)")
        .given("a user exists", name="id", value="123")
        .given("a user exists", name="name", value="John")
        .with_request("GET", "/user1")
        .will_respond_with(201)
    )
    (
        pact.upon_receiving("a basic request given a user exists (2)")
        .given("a user exists", parameters={"id": "123", "name": "John"})
        .with_request("GET", "/user2")
        .will_respond_with(202)
    )

    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request("GET", "/state") as resp:
                assert resp.status == 200
            async with session.request("GET", "/user1") as resp:
                assert resp.status == 201
            async with session.request("GET", "/user2") as resp:
                assert resp.status == 202


@pytest.mark.asyncio
async def test_binary_file_request(pact: Pact) -> None:
    payload = bytes(range(8))
    (
        pact.upon_receiving("a basic request with a binary file")
        .with_request("POST", "/")
        .with_binary_body(payload, "application/octet-stream")
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.post("/", data=payload) as resp:
                assert resp.status == 200

    with pytest.raises(MismatchesError), pact.serve() as srv:  # noqa: PT012
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.post("/", data=payload[:2]) as resp:
                assert resp.status == 200


@pytest.mark.asyncio
async def test_binary_file_response(pact: Pact) -> None:
    payload = bytes(range(5))
    (
        pact.upon_receiving("a basic request with a binary file response")
        .with_request("GET", "/")
        .will_respond_with(200)
        .with_binary_body(payload, "application/bytes")
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.get("/") as resp:
                assert resp.status == 200
                assert await resp.read() == payload
                assert payload == bytes(range(5))  # to make sure it's not mutated
                assert resp.headers["Content-Type"] == "application/bytes"


@pytest.mark.skip(reason="Not working yet")
@pytest.mark.asyncio
async def test_multipart_file_request(pact: Pact, temp_dir: Path) -> None:
    fpy = temp_dir / "test.py"
    fpng = temp_dir / "test.png"
    (
        pact.upon_receiving("a basic request with a multipart file")
        .with_request("POST", "/")
        .with_multipart_file(
            fpy.name,
            fpy,
            "text/x-python",
        )
        .with_multipart_file(
            fpng.name,
            fpng,
            "image/png",
        )
        .will_respond_with(200)
    )
    with pact.serve() as srv, aiohttp.MultipartWriter() as mpwriter:
        mpwriter.append(
            fpy.open("rb"),
            # TODO: Remove type ignore once aio-libs/aiohttp#7741 is resolved
            # https://github.com/pact-foundation/pact-python/issues/450
            {"Content-Type": "text/x-python"},  # type: ignore[arg-type]
        )
        mpwriter.append(
            fpng.open("rb"),
            # TODO: Remove type ignore once aio-libs/aiohttp#7741 is resolved
            # https://github.com/pact-foundation/pact-python/issues/450
            {"Content-Type": "image/png"},  # type: ignore[arg-type]
        )

        async with (
            aiohttp.ClientSession(srv.url) as session,
            session.post(
                "/",
                data=mpwriter,
            ) as resp,
        ):
            assert resp.status == 200
            assert await resp.read() == b""


@pytest.mark.asyncio
async def test_name(pact: Pact) -> None:
    (
        pact.upon_receiving("a basic request with a test name")
        .test_name("a test name")
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.get("/") as resp:
                assert resp.status == 200
                assert await resp.read() == b""


@pytest.mark.asyncio
async def test_with_plugin(pact: Pact) -> None:
    (
        pact.upon_receiving("a basic request with a plugin")
        .with_plugin_contents("{}", "application/json")
        .will_respond_with(200)
    )
    with pact.serve() as srv:
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.get("/") as resp:
                assert resp.status == 200
                assert await resp.read() == b""


@pytest.mark.asyncio
async def test_pact_server_verbose(
    pact: Pact,
    caplog: pytest.LogCaptureFixture,
) -> None:
    (
        pact.upon_receiving("a basic request with a plugin")
        .with_request("GET", "/foo")
        .will_respond_with(200)
    )
    with (
        caplog.at_level(logging.WARNING, logger="pact.v3.pact"),
        pact.serve(raises=False, verbose=True) as srv,
    ):
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.get("/bar") as resp:
                assert resp.status == 500

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.levelname == "ERROR"
        assert record.message.startswith("Mismatches:\n")
