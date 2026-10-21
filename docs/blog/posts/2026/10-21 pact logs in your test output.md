---
authors:
    - JP-Ellis
date:
    created: 2026-10-21
---

# Pact Logs through native Python logging

Pact Python now integrates directly with Python's native [`logging`][logging]
module. As a result, test harnesses like [Pytest](https://docs.pytest.org) and
[`unittest`][unittest] are now significantly quieter when tests pass, and only
the relevant logs are shown on failure, as capture through the test harness. We
really hope this improves the developer (and agentic) experience!

This post walks through a small consumer test suite, before and after the
change, with the output of each run.

<!-- more -->

## The Example

The consumer is a small client for a user service:

```python title="user_client.py"
from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass
class User:
    id: int
    name: str
    email: str


class UserClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/json"

    def get_user(self, user_id: int) -> User | None:
        response = self.session.get(f"{self.base_url}/users/{user_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return User(**response.json())

    def create_user(self, name: str, email: str) -> User:
        response = self.session.post(
            f"{self.base_url}/users",
            json={"name": name, "email": email},
        )
        response.raise_for_status()
        return User(**response.json())

    def delete_user(self, user_id: int) -> None:
        response = self.session.delete(f"{self.base_url}/user/{user_id}")  # (1)
        response.raise_for_status()
```

1.  The bug: `/user/` is missing its `s`.

The test suite has four tests: fetching a user, fetching an unknown user, creating a user and deleting a user. The first three pass. The fourth catches the bug.

//// tab | pytest

```python title="test_user_client.py"
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from pact import Pact, match
from user_client import UserClient

if TYPE_CHECKING:
    from collections.abc import Generator

PACT_DIR = Path(__file__).parent / "pacts"


@pytest.fixture
def pact() -> Generator[Pact, None, None]:
    pact = Pact("user-web", "user-service")
    yield pact
    pact.write_file(PACT_DIR)
```

/// details | `test_get_user`

```python
def test_get_user(pact: Pact) -> None:
    (
        pact
        .upon_receiving("a request for user 123")
        .given("user 123 exists")
        .with_request("GET", "/users/123")
        .will_respond_with(200)
        .with_body(
            {
                "id": 123,
                "name": match.str("Alice"),
                "email": match.str("alice@example.com"),
            },
            content_type="application/json",
        )
    )
    with pact.serve() as srv:
        user = UserClient(str(srv.url)).get_user(123)
    assert user is not None
    assert user.name == "Alice"
```

///

/// details | `test_get_unknown_user`

```python
def test_get_unknown_user(pact: Pact) -> None:
    (
        pact
        .upon_receiving("a request for an unknown user")
        .given("user 999 does not exist")
        .with_request("GET", "/users/999")
        .will_respond_with(404)
    )
    with pact.serve() as srv:
        assert UserClient(str(srv.url)).get_user(999) is None
```

///

/// details | `test_create_user`

```python
def test_create_user(pact: Pact) -> None:
    (
        pact
        .upon_receiving("a request to create a user")
        .with_request("POST", "/users")
        .with_body(
            {"name": "Bob", "email": "bob@example.com"},
            content_type="application/json",
        )
        .will_respond_with(201)
        .with_body(
            {
                "id": match.int(124),
                "name": "Bob",
                "email": "bob@example.com",
            },
            content_type="application/json",
        )
    )
    with pact.serve() as srv:
        user = UserClient(str(srv.url)).create_user("Bob", "bob@example.com")
    assert user.id == 124
```

///

/// details | `test_delete_user`
    open: True

```python
def test_delete_user(pact: Pact) -> None:
    (
        pact
        .upon_receiving("a request to delete user 123")
        .given("user 123 exists")
        .with_request("DELETE", "/users/123")
        .will_respond_with(204)
    )
    with pact.serve() as srv:
        UserClient(str(srv.url)).delete_user(123)
```

///

////

//// tab | unittest

```python title="test_user_client.py"
from __future__ import annotations

import unittest
from pathlib import Path

from pact import Pact, match
from pact.testing.unittest import PactTestMixin
from user_client import UserClient

PACT_DIR = Path(__file__).parent / "pacts"


class UserClientTest(PactTestMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.pact = Pact("user-web", "user-service").with_specification("V4")

    def tearDown(self) -> None:
        self.pact.write_file(PACT_DIR)
```

/// details | `test_get_user`

```python
def test_get_user(self) -> None:
    (
        self.pact
        .upon_receiving("a request for user 123")
        .given("user 123 exists")
        .with_request("GET", "/users/123")
        .will_respond_with(200)
        .with_body(
            {
                "id": 123,
                "name": match.str("Alice"),
                "email": match.str("alice@example.com"),
            },
            content_type="application/json",
        )
    )
    with self.pact.serve() as srv:
        user = UserClient(str(srv.url)).get_user(123)
    assert user is not None
    self.assertEqual(user.name, "Alice")
```

///

/// details | `test_get_unknown_user`

```python
def test_get_unknown_user(self) -> None:
    (
        self.pact
        .upon_receiving("a request for an unknown user")
        .given("user 999 does not exist")
        .with_request("GET", "/users/999")
        .will_respond_with(404)
    )
    with self.pact.serve() as srv:
        self.assertIsNone(UserClient(str(srv.url)).get_user(999))
```

///

/// details | `test_create_user`

```python
def test_create_user(self) -> None:
    (
        self.pact
        .upon_receiving("a request to create a user")
        .with_request("POST", "/users")
        .with_body(
            {"name": "Bob", "email": "bob@example.com"},
            content_type="application/json",
        )
        .will_respond_with(201)
        .with_body(
            {
                "id": match.int(124),
                "name": "Bob",
                "email": "bob@example.com",
            },
            content_type="application/json",
        )
    )
    with self.pact.serve() as srv:
        user = UserClient(str(srv.url)).create_user("Bob", "bob@example.com")
    self.assertEqual(user.id, 124)
```

///

/// details | `test_delete_user`
open: True

```python
def test_delete_user(self) -> None:
    (
        self.pact
        .upon_receiving("a request to delete user 123")
        .given("user 123 exists")
        .with_request("DELETE", "/users/123")
        .will_respond_with(204)
    )
    with self.pact.serve() as srv:
        UserClient(str(srv.url)).delete_user(123)
```

///

////

## Before: `log_to_stderr`

Earlier releases did not have any logging callbacks between the underlying FFI
and the Python runtime. As a result, if users wanted to see logs from the
underlying Rust library, they had to set `pact_ffi.log_to_stderr` at startup.
This also cannot be modified once set, so either all tests are set to `DEBUG`,
or all at `INFO`, etc.

With that configured, the library then wrote straight to the process's standard
error, with no filtering from Python's `logging` configuration to filter or
format those lines. The test runners also could only see the raw output, unable
to distinguish a genuine call to print to `stderr` from one generated by the
underlying library.

//// tab | pytest

```python title="conftest.py"
import pact_ffi
import pytest


@pytest.fixture(scope="session", autouse=True)
def pact_logging() -> None:
    pact_ffi.log_to_stderr("INFO")
```

////

//// tab | unittest

```python title="test_user_client.py"
import pact_ffi


def setUpModule() -> None:
    pact_ffi.log_to_stderr("INFO")
```

////

### Passing Tests with `log_to_stderr`

Pytest captures the standard error of each test by default, so a plain `pytest`
run of the three passing tests printed three dots. The issue arose when running
with `-s`, as is common while debugging or from an IDE, in which case the FFI
printed every request of every test into the progress line, clobbering the
output. Unittest captures nothing, so its runs always looked like this:

//// tab | pytest

```ansi-color title="pytest -s"
--8<-- "docs/blog/posts/2026/pact-logs-in-your-test-output/pytest-before-pass.ansi"
```

////

//// tab | unittest

```ansi-color title="python -m unittest"
--8<-- "docs/blog/posts/2026/pact-logs-in-your-test-output/unittest-before-pass.ansi"
```

////

### Failing Tests with `log_to_stderr`

When there is a genuine test failure, it sat among the lines of the passing
tests. unittest also printed Pact Pythons' own error ahead of the `E` through
Python's last-resourt handler.

//// tab | pytest

```ansi-color title="pytest -s"
--8<-- "docs/blog/posts/2026/pact-logs-in-your-test-output/pytest-before-fail.ansi"
```

////

//// tab | unittest

```ansi-color title="python -m unittest"
--8<-- "docs/blog/posts/2026/pact-logs-in-your-test-output/unittest-before-fail.ansi"
```

////

Worse yet was that if the log level is lowered to `DEBUG`, as one would likely
due while troubleshooting, a number of logs emitted by the FFI between tests
escaped Pytest's capture and clobbered the progress line. For example, the mock
server's shut-down logs arrived after the summary, and the library's line and
python's own records landed in separate sections:

```ansi-color title="pytest"
--8<-- "docs/blog/posts/2026/pact-logs-in-your-test-output/pytest-before-debug.ansi"
```

## After: Logs Through `logging`

Pact Python now registers a log callback with the Pact library when the first `Pact` or `Verifier` is created. Each event from the library becomes a record on a logger under `pact.ffi`, named after the Rust module which emitted it.

//// tab | pytest

Pytest captures these records like any others. It captures only warnings and errors by default, so set its `log_level` to see the library's `INFO` records too:

```toml title="pyproject.toml"
[tool.pytest]
log_level = "INFO"
```

////

//// tab | unittest

Add [`PactTestMixin`][pact.testing.unittest.PactTestMixin] to the test case, ahead of `unittest.TestCase`:

```python title="test_user_client.py"
import unittest

from pact.testing.unittest import PactTestMixin


class UserClientTest(PactTestMixin, unittest.TestCase): ...
```

The mixin collects the Pact records of each test. When a test fails or errors, it writes them to standard error under a banner naming the test.

////

### Passing Tests with `logging`

The three passing tests print three dots. Pytest's log capture works independently of its output capture, so the run stays quiet with `-s` too:

//// tab | pytest

```ansi-color title="pytest -s"
--8<-- "docs/blog/posts/2026/pact-logs-in-your-test-output/pytest-after-pass.ansi"
```

////

//// tab | unittest

```ansi-color title="python -m unittest"
--8<-- "docs/blog/posts/2026/pact-logs-in-your-test-output/unittest-after-pass.ansi"
```

////

### Failing Tests with `logging`

The failing test now reports the mock server's record and Pact Python's error together, in the order they were logged:

//// tab | pytest

```ansi-color title="pytest"
--8<-- "docs/blog/posts/2026/pact-logs-in-your-test-output/pytest-after-fail.ansi"
```

The `logging.py:197` location is where Pact Python emits each forwarded record. A `log_format` without `%(filename)s:%(lineno)d` leaves it out.

////

//// tab | unittest

```ansi-color title="python -m unittest"
--8<-- "docs/blog/posts/2026/pact-logs-in-your-test-output/unittest-after-fail.ansi"
```

The suite configures no logging, so Python's last-resort handler still prints the bare `Mismatches:` error ahead of the `E`. The mixin collects records at the forwarding level whatever the root logger's level, so the banner also holds the `INFO` record from the mock server.

////

### Debugging a Mismatch

The logger names follow the Rust module paths, so standard `logging` levels can pick out the useful parts of the `DEBUG` output. The `pact.ffi` logger sets which events the library forwards at all. The `pact_ffi` crate traces every FFI call at `DEBUG`, and raising `pact.ffi.pact_ffi` back to `INFO` drops those traces:

//// tab | pytest

```python title="conftest.py"
import logging

logging.getLogger("pact.ffi").setLevel(logging.DEBUG)  # (1)
logging.getLogger("pact.ffi.pact_ffi").setLevel(logging.INFO)  # (2)
```

1.  The level of `pact.ffi` sets which events the library forwards at all, so it
    must be the lowest of all the `pact.ffi` levels.
2.  A logger beneath `pact.ffi` can raise its level above `DEBUG`. Lowering it
    below `DEBUG` shows nothing more, as the library never forwards those
    events.

```toml title="pyproject.toml"
[tool.pytest]
log_level = "DEBUG"
```

////

//// tab | unittest

```python title="test_user_client.py"
import logging

logging.getLogger("pact.ffi").setLevel(logging.DEBUG)  # (1)
logging.getLogger("pact.ffi.pact_ffi").setLevel(logging.INFO)  # (2)
```

1.  The level of `pact.ffi` sets which events the library forwards at all, so it
    must be the lowest of all the `pact.ffi` levels.
2.  A logger beneath `pact.ffi` can raise its level above `DEBUG`. Lowering it
    below `DEBUG` shows nothing more, as the library never forwards those
    events.

////

The failure report now follows the request from start to finish. Under pytest, the `urllib3` records from the client and the matching records from the mock server appear in one sequence. The banner of the mixin holds the Pact records alone, including those logged during `tearDown`:

//// tab | pytest

```ansi-color title="pytest"
--8<-- "docs/blog/posts/2026/pact-logs-in-your-test-output/pytest-after-debug.ansi"
```

////

//// tab | unittest

```ansi-color title="python -m unittest"
--8<-- "docs/blog/posts/2026/pact-logs-in-your-test-output/unittest-after-debug.ansi"
```

////

The three passing tests still print three dots.

/// warning | Set the Level Before the First `Pact`
The library's forwarding level is fixed when the first `Pact` or `Verifier` is created. Set the level of `pact.ffi` before then, for example at the top of `conftest.py` or of the test module. A call to `caplog.set_level` inside a test cannot bring back records which were never forwarded.
///

### Test Run IDs

When several tests run at once, knowing which log belongs to which test is just
as important as seeing the logs at all. To help with this, the pytest plugin and
the mixin also set a Pact test run ID for each test: the pytest node ID, or the
`unittest` test ID. Every record the library emits on the test's thread carries
this ID as a `test_run_id` attribute. The ID is also sent along with every
request the test makes to a plugin, so the log entries the plugin sends back
carry it too. The mock server handles requests on its own threads, so its
records carry the mock server's ID as `log_id` instead. A custom handler or
formatter can use these attributes to group records by test, which is
especially useful when tests run in parallel.

There is nothing to set up for this. Pact Python registers the pytest plugin
automatically, and it is careful not to load the Pact library itself, so a
pytest session which never uses Pact is unaffected. If you would rather go
without it, pass `-p no:pact`. A `PactTestMixin` test case can also run under
pytest, in which case the mixin hands the run ID back to the pytest node ID once
the test finishes.

## Plugin Logs

Plugins run as separate processes, each with logs of its own. Pact Python
forwards both the
lines each plugin writes to its standard error and the log entries it sends back
over its RPC connection to the `pact.plugins` logger. Each record carries the
`plugin_instance_id` of the plugin which emitted it. Unlike the `pact.ffi`
loggers, every plugin entry is forwarded, so the level of `pact.plugins` alone
decides which ones are shown, and it can be changed at any time.

The library also keeps every plugin entry in a buffer for the life of the
process. If you need them after the fact, pass a `plugin_instance_id` to
[`pact.plugins.get_logs`][pact.plugins.get_logs] to read the entries for that
plugin instance, along with their timestamps and sources.

## Migrating

Migrating is mostly a matter of deleting code. Remove every call to
`pact_ffi.log_to_stderr`, `log_to_stdout`, `log_to_file`, `init` and
`init_with_log_level`. Once Pact Python's logging integration is loaded, these
functions no longer do anything except emit a `UserWarning`, which pytest lists
in its summary:

```ansi-color title="pytest"
--8<-- "docs/blog/posts/2026/pact-logs-in-your-test-output/pytest-migrate.ansi"
```

For the full details, the [Logging](../../../logging.md) guide lists every
logger and record attribute, including the `log_id` which identifies each mock
server and provider verification.
