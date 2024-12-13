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

import socket
import sys
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from testcontainers.compose import DockerCompose  # type: ignore[import-untyped]
from yarl import URL

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

    import execnet

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

    # Check whether port 9292 is already in use. If it is, we assume that the
    # broker is already running and return early.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("localhost", 9292)) == 0:
            yield URL("http://pactbroker:pactbroker@localhost:9292")
            return

    with DockerCompose(
        EXAMPLE_DIR,
        compose_file_name=["docker-compose.yml"],
        pull=True,
        wait=False,
    ) as _:
        yield URL("http://pactbroker:pactbroker@localhost:9292")


@pytest.fixture(scope="session")
def pact_dir() -> Path:
    """Fixture for the Pact directory."""
    return EXAMPLE_DIR / "pacts"


def pytest_xdist_setupnodes(
    config: pytest.Config,  # noqa: ARG001
    specs: Sequence[execnet.XSpec],
) -> None:
    """
    Hook to check if the examples are run with multiple workers.

    The examples are designed to run in a specific order, with the consumer
    tests running _before_ the provider tests as the provider tests require that
    the consumer-generated Pacts are published.

    If multiple xdist workers are detected, a warning is printed to the console.
    """
    if len(specs) > 1:
        sys.stderr.write("\n")
        warnings.warn(
            "Running the examples with multiple workers may cause issues. "
            "Consider running the examples with a single worker by setting "
            "`--numprocesses=1` or using `hatch run example`.",
            stacklevel=1,
        )
