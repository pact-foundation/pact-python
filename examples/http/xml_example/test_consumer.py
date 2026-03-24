"""
Consumer contract tests using Pact (XML).

This module demonstrates how to test a consumer (see
[`consumer.py`][examples.http.xml_example.consumer]) against a mock provider
using Pact. The mock provider is set up by Pact to validate that the consumer
makes the expected requests and can handle the provider's responses. Once
validated, the contract is written to a file for use in provider verification.

## XML matchers

Unlike a literal XML string, the response body can be expressed using the
`pact.xml` builder. This allows standard Pact matchers (such as
`match.int()` and `match.str()`) to be embedded in the body description, so
the contract specifies *structural constraints* rather than exact values.

Whereas a JSON body can be described as:

```python
response = {"id": match.int(123), "name": match.str("Alice")}
```

An equivalent XML body is described with the `xml` builder as:

```python
from pact import match, xml

response = xml.body(
    xml.element(
        "user",
        xml.element("id", match.int(123)),
        xml.element("name", match.str("Alice")),
    )
)
```

Pass this dict to `.with_body()` with `content_type="application/xml"`. The
Pact FFI detects that the body is JSON, generates the example XML, and
registers matching rules for each annotated element. The resulting contract
will match _any_ XML response where `<id>` contains an integer and `<name>`
contains a string and not just the specific example values.

For attribute matchers, pass matcher objects via the `attrs` keyword argument:

```python
xml.element("user", attrs={"id": match.int(1), "type": "activity"})
```

## Setting request headers

`with_request()` does not accept a `headers` argument. Instead, use a
subsequent `.with_header()` call on the same interaction chain, as shown in the
tests below.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest
import requests

from examples.http.xml_example.consumer import UserClient
from pact import Pact, match, xml

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

logger = logging.getLogger(__name__)


@pytest.fixture
def pact(pacts_path: Path) -> Generator[Pact, None, None]:
    """
    Set up a Pact mock provider for consumer tests.

    This fixture creates a `Pact` object that acts as a mock
    provider. Each test defines the expected request and response using the Pact
    DSL, and Pact spins up a local HTTP server that validates the consumer
    makes exactly those requests. This allows the consumer to be tested in
    complete isolation from the real provider, no running provider is needed
    at this stage.

    After all tests in a session have run, `write_file` serialises the
    recorded interactions to a contract file. This file is then used by the
    [provider test][examples.http.xml_example.test_provider] to verify that
    the real provider honours the contract.

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
    Test the GET request for a user, expecting an XML response with matchers.

    This test defines the expected interaction for a successful user lookup.
    It demonstrates how to use `xml.body()` and `xml.element()` to specify
    structural constraints on
    the response body: the `id` element must contain an integer and the `name`
    element must contain a non-null string, but their exact values do not
    matter. The `Accept: application/xml` request header is registered via a
    separate `.with_header()` call after `.with_request()`.
    """
    response = xml.body(
        xml.element(
            "user",
            xml.element("id", match.int(123)),
            xml.element("name", match.str("Alice")),
        )
    )
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

    This test verifies that the consumer correctly handles a 404 error by
    propagating a `requests.HTTPError` (via `raise_for_status()`). No response
    body is matched: when the provider returns a 404, FastAPI produces a JSON
    error body, but this consumer does not inspect the error body; it only
    checks the status code and raises. Explicitly omitting `.with_body()` here
    communicates that the consumer's contract requirement is limited to the
    status code, not the error payload.
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
