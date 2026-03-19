"""
Consumer contract tests using Pact (XML).

This module demonstrates how to test a consumer (see
[`consumer.py`][examples.http.xml_example.consumer]) against a mock provider
using Pact. The key difference from JSON-based examples is that the response
body is specified as a plain XML string — no matchers are used, as XML matchers
do not exist in pact-python. The `Accept` header is set via a separate
`.with_header()` call after `.with_request()`.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest
import requests

from examples.http.xml_example.consumer import UserClient
from pact import Pact

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

logger = logging.getLogger(__name__)


@pytest.fixture
def pact(pacts_path: Path) -> Generator[Pact, None, None]:
    """
    Set up a Pact mock provider for consumer tests.

    Args:
        pacts_path:
            The path where the generated pact file will be written.

    Yields:
        A Pact object for use in tests.
    """
    pact = Pact("xml-consumer", "xml-provider").with_specification("V4")
    yield pact
    pact.write_file(pacts_path)


def test_get_user(pact: Pact) -> None:
    """
    Test the GET request for a user, expecting an XML response.

    The response body is a plain XML string. Note that `.with_header()` is
    called as a separate chain step — `with_request()` does not accept a
    headers argument.
    """
    response = "<user><id>123</id><name>Alice</name></user>"
    (
        pact
        .upon_receiving("A request for a user as XML")
        .given("the user exists", id=123, name="Alice")
        .with_request("GET", "/users/123")
        .with_header("Accept", "application/xml")
        .will_respond_with(200)
        .with_body(response, content_type="application/xml")
    )

    with (
        pact.serve() as srv,
        UserClient(str(srv.url)) as client,
    ):
        user = client.get_user(123)
        assert user.id == 123
        assert user.name == "Alice"


def test_get_unknown_user(pact: Pact) -> None:
    """
    Test the GET request for an unknown user, expecting a 404 response.
    """
    (
        pact
        .upon_receiving("A request for an unknown user as XML")
        .given("the user doesn't exist", id=123)
        .with_request("GET", "/users/123")
        .with_header("Accept", "application/xml")
        .will_respond_with(404)
    )

    with (
        pact.serve() as srv,
        UserClient(str(srv.url)) as client,
        pytest.raises(requests.HTTPError),
    ):
        client.get_user(123)
