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

The library forwards events at the most verbose level set explicitly on the
`pact.ffi` and `pact.plugins` loggers, or at
[`DEFAULT_LEVEL`][pact.logging.DEFAULT_LEVEL] when neither is set:

```python
import logging

logging.getLogger("pact.ffi").setLevel(logging.INFO)
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
from that thread and, because it is attached to every plugin request the
thread makes, on every plugin record. This keeps records apart when tests run
in parallel, or when a plugin's clean-up overlaps the start of the next test.
Mock server records carry `log_id` instead.

## Configuring the FFI Directly

The `pact_ffi` module exposes the library's own sinks. Calling
[`log_to_stderr`][pact_ffi.log_to_stderr] or
[`log_to_buffer`][pact_ffi.log_to_buffer] before the first `Pact` or
`Verifier` applies that sink instead of the silent one Pact Python uses.
Events are still forwarded to `logging`, at the more restrictive of the
sink's level and the level described under [Verbosity](#verbosity), and a
warning is logged on the `pact` logger. The library's logger can be applied
once per process, so calling these after a `Pact` or `Verifier` exists fails
with "Logger already initialized".

/// note | Not Yet Implemented
`log_to_file`, `fetch_log_buffer`, `logger_init`, `logger_attach_sink` and
`logger_apply` are not implemented in the Python bindings. If you need one,
open an issue on the [Pact Python GitHub
repository](https://github.com/pact-foundation/pact-python/issues).
///

## Further Information

-   [`pact.logging`][pact.logging]
-   [`pact_ffi.LevelFilter`][pact_ffi.LevelFilter]
