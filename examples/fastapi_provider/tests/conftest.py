# Load in the fixtures from common/sharedfixtures.py
import sys

sys.path.append("../common")

pytest_plugins = [
    "sharedfixtures",
]

from multiprocessing import Process

import pytest

from .pact_provider import run_server


@pytest.fixture(scope="module")
def server():
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    yield proc

    # Cleanup after test
    if sys.version_info >= (3, 7):
        # multiprocessing.kill is new in 3.7
        proc.kill()
    else:
        proc.terminate()
