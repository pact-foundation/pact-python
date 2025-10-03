"""
Pact Python V3.

This package provides contract testing capabilities for Python applications
using the [Pact specification](https://docs.pact.io/). Built on the [Pact Rust
FFI library](https://github.com/pact-foundation/pact-reference), it offers full
support for all Pact features and maintains compatibility with other Pact
implementations.

## Package Structure

### Main Classes

The primary entry points for contract testing are:

-   [`Pact`][pact.Pact]: For consumer-side contract testing, defining expected
    interactions and generating contract files.
-   [`Verifier`][pact.Verifier]: For provider-side contract verification,
    validating that a provider implementation satisfies consumer contracts.

These functions are defined in [`pact.pact`][pact.pact] and
[`pact.verifier`][pact.verifier] and re-exported for convenience.

### Matching and Generation

For flexible contract definitions, use the matching and generation modules:

```python
from pact import match, generate

# Import modules, not individual functions
# Use functions via module namespace to avoid shadowing built-ins
user_id = match.int(min=1)
user_name = match.str(size=20)
created_at = match.datetime()

# Generators work similarly
response_id = generate.uuid()
score = generate.float(precision=2)
```

The functions within these modules are designed to align with a number of
Python built-in types and functions. As such, the module should be imported
as a whole, rather than importing individual functions to avoid potential
shadowing of built-ins.

### Utility Modules

-   `error`: Exception classes used throughout the package. Typically not
    imported directly unless implementing custom error handling.
-   `types`: Type definitions and protocols. This does not provide much
    functionality, but will be used by your type-checker.

## Basic Usage

### Consumer Testing

```python
from pact import Pact, match

# Create a consumer contract
pact = Pact("consumer", "provider")

# Define expected interactions
(
    pact.upon_receiving("get user")
    .given("user exists")
    .with_request(method="GET", path="/users/123")
    .will_respond_with(
        status=200,
        body={
            "id": match.int(123),
            "name": match.str("alice"),
        },
    )
)

# Use in tests with the mock server
with pact.serve() as server:
    # Make requests to server.url
    # Test your consumer code
    pass
```

### Provider Verification

```python
from pact import Verifier

# Verify provider against contracts
verifier = Verifier()
verifier.verify_with_broker(
    provider="provider-name",
    broker_url="https://my-org.pactflow.io",
)
```

For more detailed usage examples, see the
[examples](https://pact-foundation.github.io/pact-python/examples).
"""

from __future__ import annotations

from pact.__version__ import __version__, __version_tuple__
from pact.pact import Pact
from pact.verifier import Verifier

__url__ = "https://github.com/pact-foundation/pact-python"
__license__ = "MIT"
__author__ = "Pact Foundation"

__all__ = [
    "Pact",
    "Verifier",
    "__version__",
    "__version_tuple__",
]
