"""
Global PyTest configuration.

This file is automatically loaded by PyTest before running any tests and is used
to define global fixtures and command line options. Command line options can
only be defined in this file.
"""

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Define additional command line options for the Pact examples.

    Args:
        parser:
            Parser used to register CLI options for the tests.
    """
    parser.addoption(
        "--broker-url",
        help=(
            "The URL of the broker to use. If this option has been given, the container"
            " will _not_ be started."
        ),
        type=str,
    )
    parser.addoption(
        "--container",
        action="store_true",
        help="Run tests using a container",
    )


def pytest_runtest_setup(item: pytest.Item) -> None:
    """
    Hook into the test setup phase to apply container markers.

    Args:
        item:
            Pytest item under execution, used to inspect markers and options.
    """
    if "container" in item.keywords and not item.config.getoption("--container"):
        pytest.skip("need --container to run this test")
