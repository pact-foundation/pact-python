"""
Tests for `pact.v3._server` module.
"""

import base64
import json
from unittest.mock import MagicMock

import aiohttp
import pytest

from pact.v3._server import MessageProducer, StateCallback


def test_relay_default_init() -> None:
    handler = MagicMock()
    server = MessageProducer(handler)

    assert server.host == "localhost"
    assert server.port > 1024  # Random non-privileged port
    assert server.url == f"http://{server.host}:{server.port}"


@pytest.mark.asyncio
async def test_relay_invalid_path_http() -> None:
    handler = MagicMock(return_value="Not OK")
    server = MessageProducer(handler)

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.get(server.url) as response:
                assert response.status == 404
    handler.assert_not_called()


@pytest.mark.asyncio
async def test_relay_get_http() -> None:
    handler = MagicMock(return_value=b"Pact Python is awesome!")
    server = MessageProducer(handler)

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.get(server.url + "/_pact/message") as response:
                assert response.status == 200
                assert await response.text() == "Pact Python is awesome!"

    handler.assert_called_once()
    assert handler.call_args.args == (None, None)


@pytest.mark.asyncio
async def test_relay_post_http() -> None:
    handler = MagicMock(return_value=b"Pact Python is awesome!")
    server = MessageProducer(handler)

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                server.url + "/_pact/message",
                data='{"hello": "world"}',
            ) as response:
                assert response.status == 200
                assert await response.text() == "Pact Python is awesome!"

    handler.assert_called_once()
    assert handler.call_args.args == (b'{"hello": "world"}', None)


@pytest.mark.asyncio
async def test_relay_get_with_metadata() -> None:
    handler = MagicMock(return_value=b"Pact Python is awesome!")
    server = MessageProducer(handler)
    metadata = base64.b64encode(json.dumps({"key": "value"}).encode()).decode()

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                server.url + "/_pact/message",
                headers={"Pact-Message-Metadata": metadata},
            ) as response:
                assert response.status == 200
                assert await response.text() == "Pact Python is awesome!"

    handler.assert_called_once()
    assert handler.call_args.args == (None, {"key": "value"})


@pytest.mark.asyncio
async def test_relay_post_with_metadata() -> None:
    handler = MagicMock(return_value=b"Pact Python is awesome!")
    server = MessageProducer(handler)
    metadata = base64.b64encode(json.dumps({"key": "value"}).encode()).decode()

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                server.url + "/_pact/message",
                data='{"hello": "world"}',
                headers={"Pact-Message-Metadata": metadata},
            ) as response:
                assert response.status == 200
                assert await response.text() == "Pact Python is awesome!"

    handler.assert_called_once()
    assert handler.call_args.args == (b'{"hello": "world"}', {"key": "value"})


def test_callback_default_init() -> None:
    handler = MagicMock()
    server = StateCallback(handler)

    assert server.host == "localhost"
    assert server.port > 1024  # Random non-privileged port
    assert server.url == f"http://{server.host}:{server.port}"


@pytest.mark.asyncio
async def test_callback_invalid_http() -> None:
    handler = MagicMock(return_value=None)
    server = StateCallback(handler)

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.get(server.url) as response:
                assert response.status == 404
    handler.assert_not_called()


@pytest.mark.asyncio
async def test_callback_get_http() -> None:
    handler = MagicMock(return_value=None)
    server = StateCallback(handler)

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.get(server.url + "/_pact/state") as response:
                assert response.status == 404

    handler.assert_not_called()


@pytest.mark.asyncio
async def test_callback_post_query() -> None:
    handler = MagicMock(return_value=None)
    server = StateCallback(handler)

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                server.url + "/_pact/state",
                params={
                    "state": "user exists",
                    "action": "setup",
                    "foo": "bar",
                    "1": 2,
                },
            ) as response:
                assert response.status == 200

    handler.assert_called_once()
    assert handler.call_args.args == (
        "user exists",
        "setup",
        {"foo": "bar", "1": "2"},
    )


@pytest.mark.asyncio
async def test_callback_post_body() -> None:
    handler = MagicMock(return_value=None)
    server = StateCallback(handler)

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                server.url + "/_pact/state",
                json={
                    "state": "user exists",
                    "action": "setup",
                    "foo": "bar",
                    "1": 2,
                },
            ) as response:
                assert response.status == 200

    handler.assert_called_once()
    assert handler.call_args.args == (
        "user exists",
        "setup",
        {"foo": "bar", "1": 2},
    )
