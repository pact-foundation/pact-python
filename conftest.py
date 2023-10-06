"""
Global Pytest configuration.

This file is used to define global Pytest configuration. In this case, we use it
to define additional command line options to customise the examples.
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
