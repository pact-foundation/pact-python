"""
Consumer tests demonstrating binary payloads with matching rules.

Binary payloads (images, archives, compiled artefacts, etc.) cannot be
represented as JSON or XML, so Pact stores them as raw bytes and encodes them
as base64 within the generated contract. This means the contract cannot express
matching rules _inside_ the payload. Instead, matching rules are applied to the
payload as a whole, and the most useful of these is the `contentType` matcher:

```python
from pact import match

{"body": {"$": match.content_type("application/octet-stream")}}
```

The contract then requires that the payload be of the declared content type,
rather than an exact byte-for-byte match, so the provider may return (or accept)
any payload of that type. Exact byte matching is the default when no matching
rule is defined, which in practice makes binary contracts extremely brittle.

The example below models a small blob store: the consumer uploads an opaque
binary payload and later downloads it again. Both directions use
`with_binary_body` to declare the payload, with a `contentType` matching rule
on the body root (`$`).

The payloads here are arbitrary bytes with no meaning of their own, so the
declared type is `application/octet-stream`. A payload known to be a specific
format should declare that format (for example `image/png`) instead: the
matching rule constrains the type the provider must return.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import pytest

from pact import Pact, match

if TYPE_CHECKING:
    from collections.abc import Generator


#: Binary payload used as the example value within the contract. These bytes
#: are neither valid UTF-8 nor a well-known file signature, so Pact detects
#: them as `application/octet-stream`.
CONTRACT_BLOB = bytes([0x00, 0x01, 0x02, 0x03, 0xFF, 0xFE, 0x10, 0x20])

#: Payload actually sent by the consumer during the test. It deliberately
#: differs in both length and content from `CONTRACT_BLOB` to show that the
#: matching rule, not the example bytes, defines the contract.
ACTUAL_BLOB = bytes([0xDE, 0xAD, 0xBE, 0xEF, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55])


@pytest.fixture
def pact() -> Generator[Pact, None, None]:
    """
    Set up Pact for consumer contract testing.

    The generated contract is written to the `pacts` directory shared by all
    catalog entries, where the provider test picks it up for verification.
    """
    pact = Pact("binary-consumer", "binary-provider")
    yield pact
    pact.write_file(Path(__file__).parents[1] / "pacts")


def test_upload_binary_blob(pact: Pact) -> None:
    """
    Test uploading a binary payload with a matching rule.

    The request body is declared with `with_binary_body()` and a
    `contentType` matching rule on `$`. The test then sends a payload
    with different contents and a different length, which the mock server
    accepts because the rule only constrains the content type.

    The response is JSON and is matched field-by-field in the usual way, which
    shows that a binary request can be combined with a structured response.
    The `size` field uses `match.int()` so the provider is free to report the
    real size of whatever payload it received.
    """
    (
        pact
        .upon_receiving("a binary blob upload")
        .with_request("POST", "/blobs")
        .with_binary_body(CONTRACT_BLOB, "application/octet-stream")
        .with_matching_rules({
            "body": {"$": match.content_type("application/octet-stream")},
        })
        .will_respond_with(201)
        .with_body({
            "id": "blob-1",
            "size": match.int(len(CONTRACT_BLOB)),
        })
    )

    with pact.serve() as srv:
        response = httpx.post(
            f"{srv.url}/blobs",
            content=ACTUAL_BLOB,
            headers={"Content-Type": "application/octet-stream"},
            timeout=5,
        )

        assert response.status_code == 201
        result = response.json()
        assert result["id"] == "blob-1"
        assert result["size"] == len(CONTRACT_BLOB)


def test_download_binary_blob(pact: Pact) -> None:
    """
    Test downloading a binary payload with a matching rule.

    The response body is declared in the same way as the request body above:
    raw bytes via `with_binary_body`, plus a `contentType` matching rule on
    `$`. The mock server returns the example bytes from the contract, so the
    consumer can assert on the exact payload it receives.
    """
    (
        pact
        .upon_receiving("a request for a binary blob")
        .given("a binary blob exists", id="blob-1")
        .with_request("GET", "/blobs/blob-1")
        .will_respond_with(200)
        .with_binary_body(CONTRACT_BLOB, "application/octet-stream")
        .with_matching_rules({
            "body": {"$": match.content_type("application/octet-stream")},
        })
    )

    with pact.serve() as srv:
        response = httpx.get(f"{srv.url}/blobs/blob-1", timeout=5)

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/octet-stream"
        assert response.content == CONTRACT_BLOB
