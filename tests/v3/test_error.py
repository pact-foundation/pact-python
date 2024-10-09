"""
Error handling and mismatch tests.
"""

import re

import aiohttp
import pytest

from pact.v3 import Pact
from pact.v3.error import (
    BodyMismatch,
    BodyTypeMismatch,
    HeaderMismatch,
    MismatchesError,
    MissingRequest,
    QueryMismatch,
    RequestMismatch,
    RequestNotFound,
)


@pytest.fixture
def pact() -> Pact:
    """
    Fixture for a Pact instance.
    """
    return Pact("consumer", "provider")


@pytest.mark.asyncio
async def test_missing_request(pact: Pact) -> None:
    (
        pact.upon_receiving("a missing request")
        .with_request("GET", "/")
        .will_respond_with(200)
    )
    with pytest.raises(MismatchesError) as exc, pact.serve() as srv:  # noqa: PT012
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/nonexistent",
            ):
                pass

    assert len(exc.value.mismatches) == 2
    missing_request, request_not_found = sorted(
        exc.value.mismatches,
        key=lambda m: m.__class__.__name__,
    )

    assert isinstance(missing_request, MissingRequest)
    assert missing_request.path == "/"
    assert missing_request.method == "GET"
    assert re.match(r"Missing request: GET /: \{.*\}", str(missing_request))

    assert isinstance(request_not_found, RequestNotFound)
    assert request_not_found.path == "/nonexistent"
    assert request_not_found.method == "GET"
    assert re.match(
        r"Request not found: GET /nonexistent: \{.*\}", str(request_not_found)
    )


@pytest.mark.asyncio
async def test_query_mismatch_value(pact: Pact) -> None:
    (
        pact.upon_receiving("a query mismatch")
        .with_request("GET", "/resource")
        .with_query_parameter("param", "expected")
        .will_respond_with(200)
    )
    with pytest.raises(MismatchesError) as exc, pact.serve() as srv:  # noqa: PT012
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/resource?param=actual",
            ):
                pass

    assert len(exc.value.mismatches) == 1
    request_mismatch = exc.value.mismatches[0]

    assert isinstance(request_mismatch, RequestMismatch)
    assert request_mismatch.path == "/resource"
    assert request_mismatch.method == "GET"
    assert (
        str(request_mismatch)
        == """Request mismatch: GET /resource
    (1) Query mismatch: Expected query parameter 'param' \
with value 'expected' but was 'actual'"""
    )

    query_mismatch = request_mismatch.mismatches[0]
    assert isinstance(query_mismatch, QueryMismatch)
    assert query_mismatch.parameter == "param"
    assert query_mismatch.expected == "expected"
    assert query_mismatch.actual == "actual"
    assert str(query_mismatch) == (
        "Query mismatch: "
        "Expected query parameter 'param' with value 'expected' but was 'actual'"
    )


@pytest.mark.asyncio
async def test_query_mismatch_different_keys(pact: Pact) -> None:
    (
        pact.upon_receiving("a query mismatch with different keys")
        .with_request("GET", "/resource")
        .with_query_parameter("key", "value")
        .will_respond_with(200)
    )
    with pytest.raises(MismatchesError) as exc, pact.serve() as srv:  # noqa: PT012
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/resource?foo=bar",
            ):
                pass

    assert len(exc.value.mismatches) == 1
    request_mismatch = exc.value.mismatches[0]

    assert isinstance(request_mismatch, RequestMismatch)
    assert request_mismatch.path == "/resource"
    assert request_mismatch.method == "GET"

    mismatches = sorted(
        request_mismatch.mismatches,
        key=lambda m: getattr(m, "parameter", ""),
    )

    mismatch = mismatches[0]
    assert isinstance(mismatch, QueryMismatch)
    assert mismatch.parameter == "foo"
    assert mismatch.expected == ""
    assert mismatch.actual == '["bar"]'

    mismatch = mismatches[1]
    assert isinstance(mismatch, QueryMismatch)
    assert mismatch.parameter == "key"
    assert mismatch.expected == '["value"]'
    assert mismatch.actual == ""


@pytest.mark.asyncio
async def test_header_mismatch(pact: Pact) -> None:
    (
        pact.upon_receiving("a header mismatch")
        .with_request("GET", "/")
        .with_header("X-Foo", "expected")
        .will_respond_with(200)
    )
    with pytest.raises(MismatchesError) as exc, pact.serve() as srv:  # noqa: PT012
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "GET",
                "/",
                headers={"X-Foo": "unexpected"},
            ):
                pass

    assert len(exc.value.mismatches) == 1
    request_mismatch = exc.value.mismatches[0]

    assert isinstance(request_mismatch, RequestMismatch)
    assert request_mismatch.path == "/"
    assert request_mismatch.method == "GET"

    header_mismatch = request_mismatch.mismatches[0]
    assert isinstance(header_mismatch, HeaderMismatch)
    assert header_mismatch.key == "X-Foo"
    assert header_mismatch.expected == "expected"
    assert header_mismatch.actual == "unexpected"
    assert str(header_mismatch) == (
        "Header mismatch: Mismatch with header 'X-Foo': "
        "Expected 'unexpected' to be equal to 'expected'"
    )


@pytest.mark.asyncio
async def test_body_type_mismatch(pact: Pact) -> None:
    (
        pact.upon_receiving("a body type mismatch")
        .with_request("POST", "/")
        .with_body("{}", "application/json")
        .will_respond_with(200)
    )
    with pytest.raises(MismatchesError) as exc, pact.serve() as srv:  # noqa: PT012
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "POST",
                "/",
                headers={"Content-Type": "text/plain"},
                data="plain text",
            ):
                pass

    assert len(exc.value.mismatches) == 1
    request_mismatch = exc.value.mismatches[0]
    assert isinstance(request_mismatch, RequestMismatch)
    assert request_mismatch.path == "/"
    assert request_mismatch.method == "POST"

    header_mismatch = request_mismatch.mismatches[0]
    assert isinstance(header_mismatch, HeaderMismatch)
    assert header_mismatch.key == "Content-Type"
    assert header_mismatch.expected == "application/json"
    assert header_mismatch.actual == "text/plain"
    assert str(header_mismatch) == (
        "Header mismatch: Mismatch with header 'Content-Type': "
        "Expected header 'Content-Type' to have value 'application/json' "
        "but was 'text/plain'"
    )

    body_type_mismatch = request_mismatch.mismatches[1]
    assert isinstance(body_type_mismatch, BodyTypeMismatch)
    assert body_type_mismatch.expected == "application/json"
    assert body_type_mismatch.actual == "text/plain"
    assert str(body_type_mismatch) == (
        "Body type mismatch: Expected a body of 'application/json' "
        "but the actual content type was 'text/plain'"
    )


@pytest.mark.asyncio
async def test_body_mismatch(pact: Pact) -> None:
    (
        pact.upon_receiving("a body mismatch")
        .with_request("POST", "/")
        .with_body("expected")
        .will_respond_with(200)
    )
    with pytest.raises(MismatchesError) as exc, pact.serve() as srv:  # noqa: PT012
        async with aiohttp.ClientSession(srv.url) as session:
            async with session.request(
                "POST",
                "/",
                data="unexpected",
            ):
                pass

    assert len(exc.value.mismatches) == 1
    request_mismatch = exc.value.mismatches[0]

    assert isinstance(request_mismatch, RequestMismatch)
    assert request_mismatch.path == "/"
    assert request_mismatch.method == "POST"

    body_mismatch = request_mismatch.mismatches[0]
    assert isinstance(body_mismatch, BodyMismatch)
    assert body_mismatch.path == "$"
    assert body_mismatch.expected == "expected"
    assert body_mismatch.actual == "unexpected"
    assert str(body_mismatch) == (
        "Body mismatch: Expected body 'expected' to match 'unexpected' "
        "using equality but did not match"
    )
