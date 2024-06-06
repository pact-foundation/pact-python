"""
Pact Python V3.

This module provides a preview of the next major version of Pact Python. It is
subject to breaking changes and may have bugs; however, it is available for
testing and feedback. If you encounter any issues, please report them on
[GitHub](https://github.com/pact-foundation/pact-python/issues), and if you have
any feedback, please let us know on either the [GitHub
discussions](https://github.com/pact-foundation/pact-python/discussions) or on
[Slack](https://slack.pact.io/).

The next major release will use the [Pact Rust
library](https://github.com/pact-foundation/pact-reference) to provide full
support for all Pact features, and bring feature parity between the Python
library and the other Pact libraries.

## Migration Plan

This change will introduce some breaking changes where needed, but it will be
done in a staged manner to give everyone the opportunity to migrate.

### :construction: Stage 1 (from v2.2)

-   The main Pact Python library remains the same. Bugs and minor features will
    continue to be added to the existing library, but no new major features will
    be added as the focus will be on the new library.
-   The new library is exposed within `pact.v3` and can be used alongside the
    existing library. During this stage, no guarantees are made about the
    stability of the `pact.v3` module.
-   Users are **not** recommended to use the new library in any production
    critical code at this stage, but are encouraged to try it out and provide
    feedback.
-   The existing library will raise
    [`PendingDeprecationWarning`][PendingDeprecationWarning] warnings when it is
    used (if these warnings are enabled).

### :hammer_and_wrench: Stage 2 (from v2.3, tbc)

-   The library within `pact.v3` is considered generally stable and users are
    encouraged to start migrating to it.
-   A detailed migration guide will be provided.
-   The existing library will raise [`DeprecationWarning`][DeprecationWarning]
    warnings when it is used to help raise awareness of the upcoming change.
-   This stage will likely last a few months to give everyone the opportunity to
    migrate.

### :rocket: Stage 3 (from v3)

-   The `pact.v3` module is renamed to `pact`

    -   People who have previously migrated to `pact.v3` should be able to do a
        `s/pact.v3/pact/` and have everything work.
    -   If the previous stage identifies any breaking changes as necessary, they
        will be made at this point and a detailed migration guide will be
        provided.

-   The existing library is moved to the `pact.v2` scope.

    -   :bangbang: This will be a very major and breaking change. Previous code
         running against `v2` of Pact Python will **not** work against `v3` of
         Pact Python.
    -   Users still wanting to use the `v2` library will need to update their
        code to use the new `pact.v2` module. A `s/pact/pact.v2/` should be
        sufficient.
    -   The `pact.v2` module will be considered deprecated, and will eventually
        be removed in a future release. No new features and only critical bug
        fixes will be made to this part of the library.

"""

import warnings

from pact.v3.pact import Pact
from pact.v3.verifier import Verifier

warnings.warn(
    "The `pact.v3` module is not yet stable. Use at your own risk, and expect "
    "breaking changes in future releases.",
    stacklevel=2,
    category=ImportWarning,
)

__all__ = ["Pact", "Verifier"]
