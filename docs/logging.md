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

Each record from the library carries `test_run_id` and `log_id` as
attributes. `test_run_id` is set on records emitted from the thread which
called into the library; `log_id` is the mock server ID, set on records
emitted while the server handles a request on one of its own threads, where
`test_run_id` is `None`. Each plugin record carries `plugin_instance_id`,
`test_run_id` and `plugin_target`. They can be included in a formatter.
Records from other loggers do not have them, so give the formatter a default:

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

The `pact.ffi` and `pact.plugins` loggers share a single forwarding level: the
more verbose of the levels set on them. Setting only `pact.plugins` to `DEBUG`
therefore forwards the library's `DEBUG` events as well. Python discards them,
but only after each one has been passed from the library to the interpreter.

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
from that thread and, because it is attached to every plugin request the
thread makes, on every plugin record. This keeps records apart when tests run
in parallel, or when a plugin's clean-up overlaps the start of the next test.
Mock server records carry `log_id` instead.

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
-   [`pact_ffi.LevelFilter`][pact_ffi.LevelFilter]
