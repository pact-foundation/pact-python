"""
Tests for the pytest plugin in [`pact.testing.pytest`][pact.testing.pytest].
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

CONFTEST = """
import pytest

import pact.logging

calls = []


# Session scope so the recorder is in place before the plugin's function-scoped
# autouse fixture runs.
@pytest.fixture(autouse=True, scope="session")
def _record():
    original = pact.logging.set_test_run_id
    pact.logging.set_test_run_id = calls.append
    yield
    pact.logging.set_test_run_id = original


def pytest_sessionfinish(session):
    session.config.rootpath.joinpath("calls.txt").write_text(
        "\\n".join(str(c) for c in calls)
    )
"""

TEST_FILE = """
def test_one(pact_test_run_id, request):
    assert pact_test_run_id == request.node.nodeid
"""


def test_fixture_scopes_the_run_id(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(CONFTEST)
    pytester.makepyfile(test_example=TEST_FILE)

    result = pytester.runpytest("-p", "no:cacheprovider")

    result.assert_outcomes(passed=1)
    calls = pytester.path.joinpath("calls.txt").read_text().splitlines()
    assert calls == ["test_example.py::test_one", "None"]


def test_plugin_can_be_disabled(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(test_example=TEST_FILE)

    result = pytester.runpytest("-p", "no:pact", "-p", "no:cacheprovider")

    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*fixture 'pact_test_run_id' not found*"])
