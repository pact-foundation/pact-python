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
| `pact`                | Pact Python itself                                              |

The Rust module path's `::` separators become `.`, so the records from
`pact_matching::matchers` are emitted on `pact.ffi.pact_matching.matchers`,
and a level set on `pact.ffi.pact_matching` filters them. Which events the
library forwards at all is decided by the levels of `pact.ffi` and
`pact.plugins`, as described under [Verbosity](#verbosity).

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

The library forwards events at the most verbose level set explicitly on the
`pact.ffi` and `pact.plugins` loggers, or at
[`DEFAULT_LEVEL`][pact.logging.DEFAULT_LEVEL] (`logging.INFO`) when neither is
set. `DEBUG` and below add per-FFI-call tracing, per-request matching dumps
and, once a plugin is loaded, transport chatter from `hyper`, `rustls` and
`reqwest`; opt into that detail explicitly when debugging a failure:

```python
import logging

logging.getLogger("pact.ffi").setLevel(logging.DEBUG)
```

That level is fixed when the FFI is initialised, so set it before creating the
first `Pact` or `Verifier`, for example at the top of `conftest.py`. Standard
`logging` configuration then decides what is shown; under pytest, `log_level`
and `log_cli_level` apply as usual.

The library's `TRACE` level sits below `logging.DEBUG` and is exposed as
[`pact.logging.TRACE`][pact.logging.TRACE]:

```python
from pact.logging import TRACE

logging.getLogger("pact.ffi").setLevel(TRACE)
```

## Correlating Logs with Tests

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

## Migrating from `pact_ffi.log_to_stderr`

Earlier releases left the library's logging unconfigured, and test suites
called [`pact_ffi.log_to_stderr`][pact_ffi.log_to_stderr], typically from a
session-scoped fixture in `conftest.py`, to see the library's output. Pact
Python now applies the library's logger itself and forwards every event to
`logging`, so remove the call.

Once `pact` is imported, `log_to_stderr`, `log_to_stdout`, `log_to_file`,
`init` and `init_with_log_level` on `pact_ffi` emit a `UserWarning` and do
nothing else. A call made before `pact` is imported still applies the
library's own sink, and Pact Python keeps it: events are still forwarded to
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
-   [`pact_ffi.LevelFilter`][pact_ffi.LevelFilter]
