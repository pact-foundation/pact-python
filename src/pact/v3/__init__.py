"""
Pact Python V3.

The next major release of Pact Python will make use of the Pact reference
library written in Rust. This will allow us to support all of the features of
Pact, and bring the Python library in line with the other Pact libraries.

The migration will happen in stages, and this module will be used to provide
access to the new functionality without breaking existing code. The stages will
be as follows:

-   **Stage 1**: The new library is exposed within `pact.v3` and can be used
    alongside the existing library. During this stage, no guarantees are made
    about the stability of the `pact.v3` module.
-   **Stage 2**: The library within `pact.v3` is considered stable, and we begin
    the process of deprecating the existing library by raising deprecation
    warnings when it is used. A detailed migration guide will be provided.
-   **Stage 3**: The `pact.v3` module is renamed to `pact`, and the existing
    library is moved to the `pact.v2` scope. The `pact.v2` module will be
    considered deprecated, and will be removed in a future release.
"""

import warnings

from pact.v3.pact import Pact

__all__ = [
    "Pact",
]

warnings.warn(
    "The `pact.v3` module is not yet stable. Use at your own risk, and expect "
    "breaking changes in future releases.",
    stacklevel=2,
    category=ImportWarning,
)
