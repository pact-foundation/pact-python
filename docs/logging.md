# Logging

Pact Python is built on the Pact FFI, a Rust library, and Pact plugins run as
separate processes. Neither writes to Python's `logging` module on its own, so
Pact Python forwards their log events for them. Nothing needs to be
configured: the first [`Pact`][pact.Pact] or [`Verifier`][pact.Verifier]
created in a process initialises the FFI and registers the forwarding.

## Loggers

| Logger                | Source                                                          |
| --------------------- | --------------------------------------------------------------- |
| `pact.ffi.<target>`   | The Pact library, where `<target>` is the Rust module path      |
| `pact.plugins`        | Plugins, whether written to their stderr or sent over the RPC   |
| `pact.<module>`       | Pact Python itself, for example `pact.pact` or `pact.verifier`  |
| `pact`                | Pact Python's warnings about the logging set-up                 |

The Rust module path's `::` separators become `.`, so the records from
`pact_matching::matchers` are emitted on `pact.ffi.pact_matching.matchers`,
and a level set on `pact.ffi.pact_matching` filters them. Which events the
library forwards at all is decided by the level of `pact.ffi`, as described
under [Verbosity](#verbosity).

Each record from the library carries `log_id` and `test_run_id` as
attributes:

-   `log_id` identifies the operation which emitted the event: the mock
    server ID while the server handles a request, or `verify:<provider name>`
    while verifying a provider. It is `None` otherwise.
-   `test_run_id` is the ID set with
    [`set_test_run_id`][pact.logging.set_test_run_id] on the thread which
    emitted the event. Records from the mock server's threads have none.
    While a provider is verified, most records carry an ID which the
    verifier generates for the run.

Each plugin record carries `plugin_instance_id`, `test_run_id` and
`plugin_target`. These attributes can be included in a formatter. Records from
other loggers do not have them, so give the formatter a default:

```python
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "%(levelname)s %(name)s [%(test_run_id)s] %(message)s",
        defaults={"test_run_id": "-"},
    )
)
logging.basicConfig(handlers=[handler])
```

## Verbosity

By default, the library forwards events at `INFO` and above
([`DEFAULT_LEVEL`][pact.logging.DEFAULT_LEVEL]). Its `DEBUG` output is much
noisier: it traces every FFI call, dumps each request as it is matched and,
once a plugin is loaded, includes the transport logs of `hyper`, `rustls` and
`reqwest`. To see it when debugging a failure, set the level of the `pact.ffi`
logger:

```python
import logging

logging.getLogger("pact.ffi").setLevel(logging.DEBUG)
```

/// warning | Set the Level Before the First `Pact`
The forwarding level is fixed when the first `Pact` or `Verifier` is created,
and cannot be changed afterwards. Set it before then, for example at the top of
`conftest.py`. A more verbose level set later only logs a warning on the `pact`
logger, once. In particular, `caplog.set_level` within a test cannot show
records which were never forwarded.
///

Forwarded records are handled like any others, so the `logging` configuration
decides which are shown. Under pytest, `log_level` and `log_cli_level` apply as
usual. With no logging configured at all, Python's last-resort handler writes
warnings and errors to stderr. To silence them, add a handler such as
`logging.NullHandler()` to the `pact` logger.

Plugin events do not depend on the forwarding level. Every one of them is
forwarded to the `pact.plugins` logger, and its level filters them like any
other logger's. That level can be changed at any time.

The library's `TRACE` level sits below `logging.DEBUG` and is exposed as
[`pact.logging.TRACE`][pact.logging.TRACE]:

```python
from pact.logging import TRACE

logging.getLogger("pact.ffi").setLevel(TRACE)
```

## Correlating Logs with Tests

/// note | Set Automatically
Most test suites never call `set_test_run_id` themselves. The
[pytest plugin](#pytest) and the [`unittest` mixin](#unittest) described below
set the run ID for every test.
///

Plugins serve every test in the process, so their records do not identify
the test which triggered them on their own.
[`set_test_run_id`][pact.logging.set_test_run_id] sets an identifier for the
current thread which is reported as `test_run_id` on the library's records
from that thread. It is also attached to every plugin request the thread
makes, so the log entries a plugin sends back while handling that request
carry it too. Lines a plugin writes to its stderr carry no `test_run_id`;
`plugin_instance_id` identifies the plugin which wrote them. This keeps
records apart when tests run in parallel, or when a plugin's clean-up overlaps
the start of the next test.

Records from the library's own threads do not carry this ID. Group them by
`log_id` instead: the records of one mock server share its ID, and the records
of one provider verification share `verify:<provider name>`.

### Pytest

The pytest plugin in [`pact.testing.pytest`][pact.testing.pytest] is enabled
automatically. Its autouse fixture
[`pact_test_run_id`][pact.testing.pytest.pact_test_run_id] sets each test's
node ID as the run ID. Pytest's own log capture then shows Pact records in the
"Captured log call" section of a failing test. By default, pytest only captures
warnings and errors; set its `log_level` to `INFO` to capture the other
records too. Disable the plugin with `-p no:pact`.

### Unittest

Use [`PactTestMixin`][pact.testing.unittest.PactTestMixin] on test cases which
use Pact. It sets the test ID as the run ID and, when a test fails or errors,
writes the Pact records collected during the test to stderr. While the test
runs, the `pact` logger is lowered to the forwarding level
([`forwarding_level`][pact.logging.forwarding_level]) if it has no explicit
level of its own, so records below the root logger's level are collected too.
Handlers on the root logger still receive only the records at or above its
level:

```python
import unittest

from pact.testing.unittest import PactTestMixin


class ConsumerTest(PactTestMixin, unittest.TestCase):
    def test_something(self) -> None: ...
```

## Migrating from `pact_ffi.log_to_stderr`

Earlier releases left the library's logging unconfigured, and test suites
called [`pact_ffi.log_to_stderr`][pact_ffi.log_to_stderr], typically from a
session-scoped fixture in `conftest.py`, to see the library's output. Pact
Python now applies the library's logger itself and forwards every event to
`logging`, so remove the call.

Once `pact` is imported, `log_to_stderr`, `log_to_stdout`, `log_to_file`,
`init` and `init_with_log_level` on `pact_ffi` emit a `UserWarning` and do
nothing else. A call to `log_to_stderr`, `init` or `init_with_log_level` made
before `pact` is imported still applies the library's own sink, and Pact Python
keeps it: events are still forwarded to
`logging`, at the more restrictive of the sink's level and the level described
under [Verbosity](#verbosity), and a warning is logged on the `pact` logger.

To keep seeing the library's output on stderr, attach a handler through
`logging`:

```python
import logging

logging.basicConfig(level=logging.INFO)
```

Under pytest, `--log-cli-level=INFO` shows the records as each test runs.

## Further Information

-   [`pact.logging`][pact.logging]
-   [`pact.testing.pytest`][pact.testing.pytest]
-   [`pact.testing.unittest`][pact.testing.unittest]
-   [`pact_ffi.LevelFilter`][pact_ffi.LevelFilter]
