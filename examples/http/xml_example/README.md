# Example: requests Client and FastAPI Provider with XML Contract Testing

This example demonstrates contract testing between a synchronous
[`requests`](https://docs.python-requests.org/en/latest/)-based client
(consumer) and a [FastAPI](https://fastapi.tiangolo.com/) web server (provider)
where the payload format is XML rather than JSON. It is designed to be
pedagogical, highlighting both the standard Pact contract testing workflow and
the specific constraints that arise when working with XML.

## Overview

-   [**Consumer**][examples.http.xml_example.consumer]: Synchronous HTTP client
    using requests, parsing XML with `xml.etree.ElementTree`
-   [**Provider**][examples.http.xml_example.provider]: FastAPI web server
    returning XML responses
-   [**Consumer Tests**][examples.http.xml_example.test_consumer]: Contract
    definition and consumer testing with Pact
-   [**Provider Tests**][examples.http.xml_example.test_provider]: Provider
    verification against contracts

Use the above links to view additional documentation within.

## What This Example Demonstrates

### Consumer Side

-   Synchronous HTTP client implementation with requests
-   Parsing XML responses using the standard library
    [`xml.etree.ElementTree`][xml.etree.ElementTree] module
-   Consumer contract testing with Pact mock servers
-   Setting request headers (e.g., `Accept: application/xml`) using
    `.with_header()` as a separate chain step

### Provider Side

-   FastAPI web server returning `application/xml` responses built with
    `xml.etree.ElementTree`
-   Provider verification against consumer contracts
-   Provider state setup and teardown for isolated, repeatable verification

### Testing Patterns

-   Independent consumer and provider testing
-   Contract-driven development workflow
-   Using the [`pact.xml`][pact.xml] builder to apply Pact matchers to XML
    bodies
-   How matcher-based contracts are more flexible than exact XML string matching

## XML Matchers

Unlike JSON, XML bodies cannot be expressed as a plain Python dict of
field-matcher pairs. Instead, use the [`pact.xml`][pact.xml] builder, which
constructs the body description from nested
[`xml.element()`][pact.xml.element] calls:

```python
from pact import match, xml

response = xml.body(
    xml.element("user",
        xml.element("id", match.int(123)),
        xml.element("name", match.str("Alice")),
    )
)
```

Pass the result to `.with_body()` with `content_type="application/xml"`. The
Pact FFI detects that the body is JSON, generates the example XML, and
registers matching rules for each annotated element. The resulting contract
will match _any_ XML response where `<id>` contains an integer and `<name>`
contains a string and not just the specific example values.

For attribute matchers, pass matcher objects via the `attrs` keyword argument:

```python
xml.element("user", attrs={"id": match.int(1), "type": "activity"})
```

For repeating elements, chain [`.each()`][pact.xml.XmlElement.each] to add a
`type` matching rule:

```python
(
    xml.element(
        "items",
        xml.element("item", xml.element("id", match.int(1))).each(min=1, examples=2),
    )
)
```

For JSON-based examples using the same matchers, see
[`requests_and_fastapi/`](../requests_and_fastapi/).

## Prerequisites

-   Python 3.10 or higher
-   A dependency manager ([uv](https://docs.astral.sh/uv/) recommended,
    [pip](https://pip.pypa.io/en/stable/) also works)

## Running the Example

### Using uv (Recommended)

We recommend using [uv](https://docs.astral.sh/uv/) to manage the virtual
environment and dependencies. The following command will automatically set up
the virtual environment, install dependencies, and execute the tests:

```console
uv run --group test pytest
```

### Using pip

If using the [`venv`][venv] module, the required steps are:

1.  Create and activate a virtual environment:

    ```console
    python -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    .venv\Scripts\activate     # On Windows
    ```

2.  Install dependencies:

    ```console
    pip install -U pip  # Pip 25.1 is required
    pip install --group test -e .
    ```

3.  Run tests:

    ```console
    pytest
    ```

## Related Documentation

-   [Pact Documentation](https://docs.pact.io/)
-   [requests Documentation](https://docs.python-requests.org/)
-   [FastAPI Documentation](https://fastapi.tiangolo.com/)
-   [pytest Documentation](https://docs.pytest.org/)
-   [xml.etree.ElementTree Documentation](https://docs.python.org/3/library/xml.etree.elementtree.html)
