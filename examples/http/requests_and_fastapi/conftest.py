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

import pytest

import pact_ffi

EXAMPLE_DIR = Path(__file__).parent.resolve()


@pytest.fixture(scope="session")
def pacts_path() -> Path:
    """Fixture for the Pact directory."""
    return EXAMPLE_DIR / "pacts"


@pytest.fixture(scope="session", autouse=True)
def _setup_pact_logging() -> None:
    """
    Set up logging for the pact package.
    """
    pact_ffi.log_to_stderr("INFO")
