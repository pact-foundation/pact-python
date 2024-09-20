"""
Shared PyTest configuration.

In order to run the examples, we need to run the Pact broker. In order to avoid
having to run the Pact broker manually, or repeating the same code in each
example, we define a PyTest fixture to run the Pact broker.

We also define a `pact_dir` fixture to define the directory where the generated
Pact files will be stored. You are encouraged to have a look at these files
after the examples have been run.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from testcontainers.compose import DockerCompose  # type: ignore[import-untyped]
from yarl import URL

if TYPE_CHECKING:
    from collections.abc import Generator

EXAMPLE_DIR = Path(__file__).parent.resolve()


@pytest.fixture(scope="session")
def broker(request: pytest.FixtureRequest) -> Generator[URL, Any, None]:
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
        EXAMPLE_DIR,
        compose_file_name=["docker-compose.yml"],
        pull=True,
        wait=False,
    ) as _:
        yield URL("http://pactbroker:pactbroker@localhost:9292")
    return


@pytest.fixture(scope="session")
def pact_dir() -> Path:
    """Fixture for the Pact directory."""
    return EXAMPLE_DIR / "pacts"
