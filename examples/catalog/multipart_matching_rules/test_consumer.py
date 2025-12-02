"""
Consumer test demonstrating multipart/form-data with matching rules.

This test shows how to use Pact matching rules with multipart requests. The
examples illustrates this with a request containing both JSON metadata and
binary data (an image). The contract uses matching rules to validate
structure and types rather than exact values, allowing flexibility in the data
sent by the consumer and accepted by the provider.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import pytest

from pact import Pact, match

if TYPE_CHECKING:
    from collections.abc import Generator


# Minimal JPEG for testing. The important part is the magic bytes. The rest is
# not strictly valid JPEG data.
# fmt: off
JPEG_BYTES = bytes([
    0xFF, 0xD8,                    # Start of Image (SOI) marker
    0xFF, 0xE0,                    # JFIF APP0 Marker
    0x00, 0x10,                    # Length of APP0 segment
    0x4A, 0x46, 0x49, 0x46, 0x00,  # "JFIF\0"
    0x01, 0x02,                    # Major and minor versions
])
# fmt: on
"""
Some minimal JPEG bytes for testing multipart uploads.

In this example, we only need the JPEG magic bytes to validate the file type.
This is not a complete JPEG file, but is sufficient for testing purposes.
"""


@pytest.fixture
def pact() -> Generator[Pact, None, None]:
    """
    Set up Pact for consumer contract testing.

    This fixture initializes a Pact instance for the consumer tests, specifying
    the consumer and provider names, and ensuring that the generated Pact files
    are written to the appropriate directory after the tests run.
    """
    pact = Pact(
        "multipart-consumer",
        "multipart-provider",
    )
    yield pact
    pact.write_file(Path(__file__).parents[1] / "pacts")


def test_multipart_upload_with_matching_rules(pact: Pact) -> None:
    """
    Test multipart upload with matching of the contents.

    This test builds a `multipart/form-data` request by hand, and then uses a
    library (`httpx`) to send the request to the mock server started by Pact.
    Unlike simpler payloads, the matching rules _cannot_ be embedded within the
    body itself. Instead, the body and matching rules are defined in separate
    calls.

    Some key points about this example:

    -   We use a matching rule for the `Content-Type` header to allow any valid
        multipart boundary. This is important because many HTTP libraries
        generate random boundaries automatically without user control.
    -   The body includes arbitrary binary data (a JPEG image) which cannot be
        represented as a string. Therefore, it is critical that
        `with_binary_body` is used to define the payload.
    -   Matching rules are defined for both the JSON metadata and the image part
        to allow flexibility in the values sent by the consumer. The general
        form to match a part within the multipart body is `$.<part name>`. So
        to match a field in the `metadata` part, we use `$.metadata.<field>`; or
        to match the content type of the `image` part, we use `$.image`:

        ```python
        from pact import match

        {
            "body": {
                "$.image": match.content_type("image/jpeg"),
                "$.metadata.name": match.regex(regex=r"^[a-zA-Z]+$"),
            },
        }
        ```

    /// warning

    Proper content types are essential when working with multipart data. This
    ensures that Pact can correctly identify and apply matching rules to each
    part of the multipart body. If content types are missing or incorrect, the
    matching rules may not be applied as expected, leading to test failures or
    incorrect behavior.

    ///

    To view the implementation, expand the source code below.
    """
    # It is recommended to use a fixed boundary for testing, this ensures that
    # the generated Pact is consistent across test runs.
    boundary = "test-boundary-12345"

    metadata = {
        "name": "test",
        "size": 100,
    }

    # Build multipart body with both JSON and binary parts. Note that since we
    # are combining text and binary data, the strings must be encoded to bytes.
    expected_body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="metadata"\r\n'
        f"Content-Type: application/json\r\n"
        f"\r\n"
        f"{json.dumps(metadata)}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="test.jpg"\r\n'
        f"Content-Type: image/jpeg\r\n"
        f"\r\n"
    ).encode()
    expected_body += JPEG_BYTES
    expected_body += f"\r\n--{boundary}--\r\n".encode()

    # Define the interaction with matching rules
    (
        pact.upon_receiving("a multipart upload with JSON metadata and image")
        .with_request("POST", "/upload")
        .with_header(
            "Content-Type",
            # The matcher here is important if you don't have the ability to fix
            # the boundary in the actual request (e.g., when using a library
            # that generates it automatically).
            match.regex(
                f"multipart/form-data; boundary={boundary}",
                regex=r"multipart/form-data;\s*boundary=.*",
            ),
        )
        .with_binary_body(
            expected_body,
            f"multipart/form-data; boundary={boundary}",
        )
        # Matching rules make the contract flexible
        .with_matching_rules({
            "body": {
                "$.image": match.content_type("image/jpeg"),
                "$.metadata": match.type({}),
                "$.metadata.name": match.regex(regex=r"^[a-zA-Z]+$"),
                "$.metadata.size": match.int(),
            },
        })
        .will_respond_with(201)
        .with_body({
            "id": "upload-1",
            "message": "Upload successful",
            "metadata": {"name": "test", "size": 100},
            "image_size": len(JPEG_BYTES),
        })
    )

    # Execute the test. Note that the matching rules take effect here, so we can
    # send data that differs from the example in the contract.
    with pact.serve() as srv:
        # Simple inline consumer: just make the multipart request
        files = {
            "metadata": (
                None,
                json.dumps({"name": "different", "size": 200}).encode(),
                "application/json",
            ),
            "image": ("test.jpg", JPEG_BYTES, "image/jpeg"),
        }
        response = httpx.post(f"{srv.url}/upload", files=files, timeout=5)

        assert response.status_code == 201
        result = response.json()
        assert result["message"] == "Upload successful"
        assert result["id"] == "upload-1"
