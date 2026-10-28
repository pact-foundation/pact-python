# Binary Payloads with Matching Rules

This entry demonstrates how to write a Pact contract for binary payloads, both
on the consumer and on the provider side.

Binary payloads (images, archives, compiled artefacts, opaque blobs, etc.)
cannot be described as JSON or XML, so Pact stores them as raw bytes and
base64-encodes them within the generated contract. As a consequence, matching
rules cannot be embedded _inside_ the payload, the way they can for JSON or XML
fields. Instead, matching rules apply to the payload as a whole, and the most
useful of these is the `contentType` matcher:

```python
from pact import match

{"body": {"$": match.content_type("application/octet-stream")}}
```

Without a matching rule, binary bodies are compared byte-for-byte, which makes
contracts brittle: any change to the payload size or contents breaks the
contract even when the consumer does not care about the exact bytes. With a
`contentType` matching rule, the contract only requires the payload to be of
the declared type.

For full implementation details, see the code and docstrings in this directory.
For general catalog usage, prerequisites, and test-running instructions, see
the [main catalog README](../README.md).

## What This Example Demonstrates

-   Declaring a binary request and response body with `with_binary_body()`
-   Applying a `contentType` matching rule to the body root (path `$`)
-   Sending a payload whose length and contents differ from the example in the
    contract, and having the mock server accept it
-   Combining a binary request with a JSON response carrying `match.int()`
    based metadata
-   Provider verification where the provider returns its own payload, which
    differs from the contract example but is still `application/octet-stream`

## Choosing the Content Type

The `contentType` matching rule constrains the payload type rather than its
bytes, so the provider must return a payload of the declared type. The payloads
here are arbitrary bytes with no meaning of their own, which is why the example
uses `application/octet-stream` throughout; a payload that is known to be, say,
a PNG should declare `image/png` instead.

## Related Documentation

-   [Pact Matching Rules](https://docs.pact.io/getting_started/matching)
-   [Pact Specification v4](https://github.com/pact-foundation/pact-specification/tree/version-4)
