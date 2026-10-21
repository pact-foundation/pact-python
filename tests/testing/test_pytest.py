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


def test_session_without_pact_does_not_load_the_ffi(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        test_example="""
        import sys

        def test_ffi_not_loaded(pact_test_run_id):
            assert "pact_ffi" not in sys.modules
        """
    )

    result = pytester.runpytest_subprocess("-p", "no:cacheprovider")

    result.assert_outcomes(passed=1)


def test_run_id_applied_when_pact_is_imported_during_a_test(
    pytester: pytest.Pytester,
) -> None:
    # The plugin holds the ID in Python until the logging integration loads,
    # which then applies it to the FFI.
    pytester.makepyfile(
        test_example="""
        import sys

        def test_import_during_test(request):
            import pact_ffi

            calls = []
            pact_ffi.set_test_run_id = calls.append
            assert "pact.logging" not in sys.modules
            import pact.logging

            assert calls == [request.node.nodeid]
        """
    )

    result = pytester.runpytest_subprocess("-p", "no:cacheprovider")

    result.assert_outcomes(passed=1)
