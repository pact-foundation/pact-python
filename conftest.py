"""
Global PyTest configuration.

This file is automatically loaded by PyTest before running any tests and is used
to define global fixtures and command line options. Command line options can
only be defined in this file.
"""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Define additional command lines to customise the examples."""
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
    Hook into the setup phase of tests.
    """
    if "container" in item.keywords and not item.config.getoption("--container"):
        pytest.skip("need --container to run this test")
