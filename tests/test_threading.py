"""
Tests for using Pact from several threads at once.
"""

from __future__ import annotations

import subprocess
import sys
import sysconfig
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

import pytest
import requests

from pact import Pact, match

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.skipif(
    not sysconfig.get_config_var("Py_GIL_DISABLED"),
    reason="Requires a free-threaded build",
)
def test_import_keeps_gil_disabled() -> None:
    # An extension module which does not declare support for running without
    # the GIL re-enables it on import. The test runs in a separate interpreter
    # so that the test dependencies are not imported.
    code = (
        "import sys, pact, pact_ffi; "
        "pact.Pact; pact_ffi.lib; "
        "print(sys._is_gil_enabled())"
    )
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-W", "error::RuntimeWarning", "-c", code],
        capture_output=True,
        check=True,
        text=True,
    )
    assert result.stdout.strip() == "False"


def test_concurrent_mock_servers(tmp_path: Path) -> None:
    threads = 8
    barrier = threading.Barrier(threads)

    def run(i: int) -> int:
        pact = Pact("consumer", f"provider-{i}").with_specification("V4")
        (
            pact
            .upon_receiving(f"a request for item {i}")
            .with_request("GET", f"/items/{i}")
            .will_respond_with(200)
            .with_body({"id": match.int(i)})
        )
        # Start the threads together so that the FFI calls overlap.
        barrier.wait()
        for _ in range(3):
            with pact.serve() as srv:
                response = requests.get(str(srv / "items" / str(i)), timeout=5)
                assert response.json() == {"id": i}
        pact.write_file(tmp_path)
        return i

    with ThreadPoolExecutor(threads) as executor:
        assert sorted(executor.map(run, range(threads))) == list(range(threads))
    assert len(list(tmp_path.glob("*.json"))) == threads
