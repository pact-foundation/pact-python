# Logging Configuration

Pact Python uses the Rust FFI (Foreign Function Interface) library for its core functionality. While the Python code uses the standard library `logging` module, the underlying FFI cannot interface with that directly. This page explains how to configure FFI logging for debugging and troubleshooting.

## Basic Configuration

The simplest way to configure FFI logging is to use the [`log_to_stderr`][pact_ffi.log_to_stderr] function from the `pact_ffi` module. This directs all FFI log output to standard error.

```python
import pact_ffi

pact_ffi.log_to_stderr("INFO")
```

### Log Levels

The following log levels are available (from least to most verbose):

-   `"OFF"` - Disable all logging
-   `"ERROR"` - Only error messages
-   `"WARN"` - Warnings and errors
-   `"INFO"` - Informational messages, warnings, and errors
-   `"DEBUG"` - Debug messages and above
-   `"TRACE"` - All messages including trace-level details

## Recommended Setup with Pytest

/// warning | One-time Initialization
The FFI logging can only be initialized **once** per process. Attempting to configure it multiple times will result in an error. For this reason, it's recommended to set up logging in a session-scoped fixture.
///

The recommended way to configure FFI logging in your test suite is to use a pytest fixture with `autouse=True` and `scope="session"` in your `conftest.py` file:

```python
import pytest
import pact_ffi


@pytest.fixture(autouse=True, scope="session")
def pact_logging():
    """Configure Pact FFI logging for the test session."""
    pact_ffi.log_to_stderr("INFO")
```

This ensures that:

1.  Logging is configured automatically for all tests
2.  It's only initialized once at the start of the test session
3.  All test output includes relevant Pact FFI logs

## Advanced Configuration

For more advanced use cases, the `pact_ffi` module provides additional logging functions:

### Logging to a File

/// note | Not Yet Implemented
The `log_to_file` function is currently not implemented in the Python bindings. If you need this feature, please open an issue on the [Pact Python GitHub repository](https://github.com/pact-foundation/pact-python/issues).
///

To direct logs to a file instead of stderr, you would use:

```python
import pact_ffi

# This will be available in a future release
pact_ffi.log_to_file("/path/to/logfile.log", pact_ffi.LevelFilter.DEBUG)
```

### Logging to a Buffer

For applications that need to capture and process logs programmatically, you can use [`log_to_buffer`][pact_ffi.log_to_buffer]:

```python
import pact_ffi

# Configure logging to an internal buffer
pact_ffi.log_to_buffer("DEBUG")
```

This is particularly useful for:

-   Capturing logs in CI/CD environments
-   Including logs in test failure reports
-   Processing or filtering log messages programmatically

/// note | Retrieving Buffer Contents
The `fetch_log_buffer` function for retrieving buffered logs is currently not implemented in the Python bindings. If you need this feature, please open an issue on the [Pact Python GitHub repository](https://github.com/pact-foundation/pact-python/issues).
///

### Multiple Sinks

/// note | Advanced Usage
The functions `logger_init`, `logger_attach_sink`, and `logger_apply` are currently not implemented in the Python bindings. If you need these features, please open an issue on the [Pact Python GitHub repository](https://github.com/pact-foundation/pact-python/issues).
///

For the most advanced scenarios, the FFI supports configuring multiple log sinks simultaneously (e.g., logging to both stderr and a file). This requires using the lower-level `logger_init`, `logger_attach_sink`, and `logger_apply` functions, which are planned for future implementation.

## Plugin Logs

Pact plugins (such as the protobuf and gRPC plugins) run as separate processes, so their log output is not part of the FFI logging configured above. The [`pact.plugins`][pact.plugins] module exposes the plugin observability features of the Pact FFI.

/// warning | Initialisation
The FFI only captures plugin log entries once it has been initialised with [`init_with_log_level`][pact_ffi.init_with_log_level] (or [`init`][pact_ffi.init]). These initialise the FFI logger to stderr in the same way as `log_to_stderr`, so use one in its place; calling both results in the "Logger already initialized" error.
///

### Forwarding to `logging`

[`forward_to_logging`][pact.plugins.forward_to_logging] delivers every plugin log entry through the standard library `logging` module, at the equivalent level, via the `pact.plugins` logger by default:

```python
import pact_ffi
from pact import plugins

pact_ffi.init_with_log_level("INFO")
plugins.forward_to_logging()
```

The plugin instance ID, test run ID and plugin-side logger target are attached to each log record as `plugin_instance_id`, `test_run_id` and `plugin_target`, so they can be included in a formatter:

```python
logging.basicConfig(
    format="%(levelname)s %(name)s [%(plugin_instance_id)s] %(message)s",
)
```

Unlike the FFI logger, the plugin log callback can be replaced at any time. [`register_log_callback`][pact.plugins.register_log_callback] accepts any callable taking a [`PluginLogEntry`][pact.plugins.PluginLogEntry] for custom handling.

### Correlating Logs with Tests

Plugins serve every test in the process, so their log entries do not identify the test which triggered them. [`set_test_run_id`][pact.plugins.set_test_run_id] tags requests made from the current thread with an identifier which the plugin reports back on each log entry. Using the pytest node ID is the natural choice:

```python
import pytest

import pact_ffi
from pact import plugins


@pytest.fixture(autouse=True, scope="session")
def plugin_logging():
    pact_ffi.init_with_log_level("INFO")
    plugins.forward_to_logging()


@pytest.fixture(autouse=True)
def plugin_test_run_id(request):
    plugins.set_test_run_id(request.node.nodeid)
    yield request.node.nodeid
    plugins.set_test_run_id(None)
```

### Retrieving Buffered Logs

Every plugin log entry is also buffered by the Pact library for the lifetime of the process. [`get_logs`][pact.plugins.get_logs] returns the entries for a plugin instance, whose ID is reported on each [`PluginLogEntry`][pact.plugins.PluginLogEntry] received through the callback:

```python
entries = plugins.get_logs(plugin_instance_id)
for entry in entries:
    print(entry.timestamp, entry.level, entry.message)
```

## Troubleshooting

### "Logger already initialized" Error

If you see an error about the logger already being initialized, it means you're trying to configure FFI logging more than once. Ensure that:

1.  You're using a session-scoped fixture as shown above
2.  You're not calling any of the `log_to_*` functions multiple times in your code
3.  If running tests multiple times in the same process (e.g., with pytest-xdist), the fixture scope is set correctly

### No Log Output

If you're not seeing any log output:

1.  Check that the log level is appropriate - `"ERROR"` will only show errors, while `"INFO"` or `"DEBUG"` will show more information
2.  Verify that the logging is configured before any Pact operations are performed
3.  For `log_to_file`, ensure the file path is writable and the directory exists

## Further Information

For complete API documentation, see:

-   [`pact_ffi.log_to_stderr`][pact_ffi.log_to_stderr]
-   [`pact_ffi.log_to_file`][pact_ffi.log_to_file]
-   [`pact_ffi.log_to_buffer`][pact_ffi.log_to_buffer]
-   [`pact_ffi.LevelFilter`][pact_ffi.LevelFilter]
-   [`pact.plugins`][pact.plugins]
