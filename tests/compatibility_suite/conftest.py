"""
Pytest configuration.

As the compatibility suite makes use of a submodule, we need to make sure the
submodule has been initialized before running the tests.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from pact.verifier import Verifier

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(scope="session", autouse=True)
def _submodule_init() -> None:
    """
    Initialize the compatibility suite Git submodule if required.
    """
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
    """
    Provide a Pact verifier instance scoped to a single test.

    Returns:
        Configurable verifier for compatibility suite scenarios.
    """
    return Verifier("provider")


@pytest.fixture(scope="session")
def broker_url(request: pytest.FixtureRequest) -> Generator[str, Any, None]:
    """
    Yield the Pact Broker URL, starting a container when required.

    If Pytest has been started with an explicit `--broker-url` option, then that
    URL is returned by this fixture; otherwise, a Pact Broker container is
    launched to run tests against it.

    Args:
        request:
            Active pytest request object used to inspect command-line options.

    Yields:
        Location of the Pact Broker to use for compatibility testing.
    """
    broker_url: str | None = request.config.getoption("--broker-url")

    # If we have been given a broker URL, there's nothing more to do here and we
    # can return early.
    if broker_url:
        yield broker_url
        return

    # On Windows, free-threaded builds have no `pywin32` wheels, so the
    # resolver falls back to a `docker` release which imports `distutils`.
    # Importing here keeps the rest of the suite collectable.
    from testcontainers.compose import (  # noqa: PLC0415
        DockerCompose,  # type: ignore[import-untyped]
    )

    with DockerCompose(
        Path(__file__).parent / "util",
        compose_file_name="pact-broker.yml",
        pull=True,
    ) as _:
        yield "http://pactbroker:pactbroker@localhost:9292"
    return
