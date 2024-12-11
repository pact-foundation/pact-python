"""
Tests for `pact.v3._server` module.
"""

import json
from unittest.mock import MagicMock

import aiohttp
import pytest

from pact.v3._server import MessageProducer, StateCallback


def test_message_default_init() -> None:
    handler = MagicMock()
    server = MessageProducer(handler)

    assert server.host == "localhost"
    assert server.port > 1024  # Random non-privileged port
    assert server.url == f"http://{server.host}:{server.port}/_pact/message"


@pytest.mark.asyncio
async def test_message_invalid_path_http() -> None:
    handler = MagicMock(return_value="Not OK")
    server = MessageProducer(handler)

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.get(server.url) as response:
                assert response.status == 404
    handler.assert_not_called()


@pytest.mark.asyncio
async def test_message_get_http() -> None:
    handler = MagicMock(return_value=b"Pact Python is awesome!")
    server = MessageProducer(handler)

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.get(server.url) as response:
                assert response.status == 404

    handler.assert_not_called()


@pytest.mark.asyncio
async def test_message_post_http() -> None:
    handler = MagicMock(
        return_value={
            "contents": json.dumps({"hello": "world"}).encode(),
            "metadata": None,
            "content_type": "application/json",
        }
    )
    server = MessageProducer(handler)

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                server.url,
                data=json.dumps({
                    "description": "A simple message",
                }),
            ) as response:
                assert response.status == 200
                assert await response.text() == '{"hello": "world"}'

    handler.assert_called_once()
    assert handler.call_args.args == ("A simple message", {})


def test_callback_default_init() -> None:
    handler = MagicMock()
    server = StateCallback(handler)

    assert server.host == "localhost"
    assert server.port > 1024  # Random non-privileged port
    assert server.url == f"http://{server.host}:{server.port}/_pact/state"


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
            async with session.get(server.url) as response:
                assert response.status == 404

    handler.assert_not_called()


@pytest.mark.asyncio
async def test_callback_post() -> None:
    handler = MagicMock(return_value=None)
    server = StateCallback(handler)

    with server:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                server.url,
                json={
                    "state": "user exists",
                    "action": "setup",
                    "params": {
                        "id": 123,
                    },
                },
            ) as response:
                assert response.status == 200

    handler.assert_called_once()
    assert handler.call_args.args == (
        "user exists",
        "setup",
        {"id": 123},
    )
