"""
Pytest configuration.

As the compatibility suite makes use of a submodule, we need to make sure the
submodule has been initialized before running the tests.
"""

import shutil
import subprocess
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from testcontainers.compose import DockerCompose  # type: ignore[import-untyped]
from yarl import URL

from pact.v3.verifier import Verifier


@pytest.fixture(scope="session", autouse=True)
def _submodule_init() -> None:
    """Initialize the submodule."""
    # Locate the git execute
    submodule_dir = Path(__file__).parent / "definition"
    if submodule_dir.is_dir():
        return

    git_exec = shutil.which("git")
    if git_exec is None:
        msg = (
            "Submodule not initialized and git executable not found."
            " Please initialize the submodule with `git submodule init`."
        )
        raise RuntimeError(msg)
    subprocess.check_call([git_exec, "submodule", "init"])  # noqa: S603


@pytest.fixture
def verifier() -> Verifier:
    """Return a new Verifier."""
    return Verifier("provider")


@pytest.fixture(scope="session")
def broker_url(request: pytest.FixtureRequest) -> Generator[URL, Any, None]:
    """
    Fixture to run the Pact broker.

    This inspects whether the `--broker-url` option has been given. If it has,
    it is assumed that the broker is already running and simply returns the
    given URL.

    Otherwise, the Pact broker is started in a container. The URL of the
    containerised broker is then returned.
    """
    broker_url: str | None = request.config.getoption("--broker-url")

    # If we have been given a broker URL, there's nothing more to do here and we
    # can return early.
    if broker_url:
        yield URL(broker_url)
        return

    with DockerCompose(
        Path(__file__).parent / "util",
        compose_file_name="pact-broker.yml",
        pull=True,
    ) as _:
        yield URL("http://pactbroker:pactbroker@localhost:9292")
    return
