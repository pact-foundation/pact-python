"""
Provider contract tests using Pact.

This module demonstrates how to test an Async / Message provider against a mock
consumer using Pact. The mock consumer replays the requests defined by the
consumer contract, and Pact validates that the provider responds as expected.

These tests show how provider verification ensures that the provider remains
compatible with the consumer contract as the provider evolves. Provider state
management is handled by mocking the database and using provider state
endpoints. For more, see the [Pact Provider
Test](https://docs.pact.io/5-minute-getting-started-guide#scope-of-a-provider-pact-test)
section of the Pact documentation.
"""

import json
from importlib.metadata import version
from typing import Any, Literal

from pact import Verifier
from pact.types import Message

BROKER_URL = "http://<host>:<port>"


def mock_test_state(
    action: Literal["setup", "teardown"],
    parameters: dict[str, Any] | None = None,
) -> None:
    # for tests that require setup use this structure
    # e.g. create db, fill it with data, etc.

    _ = parameters  # do something with parameters if needed

    if action == "setup":
        # e.g. create user
        return

    if action == "teardown":
        # e.g. delete user
        return

    msg = f"Unknown action: {action}"
    raise ValueError(msg)


def event_file_created_message_handler() -> Message:
    expected_contents = {
        "action": "file created",
        "path": "file.csv",
        "contents": ":O",
    }

    ## test / mock logic here!

    return {
        "contents": bytes(json.dumps(expected_contents).encode("utf-8")),
        "metadata": None,
        "content_type": "application/json",
    }


def test_provider() -> None:
    verif = (
        Verifier(name="service-provider")
        .message_handler({
            "file created": event_file_created_message_handler
        })  # use this, or `.add_transport`, not both
        .state_handler(
            {
                "user exists": mock_test_state,
            },
            teardown=True,
        )
        .broker_source(url=BROKER_URL, selector=True)
        .consumer_tags("files")  # tags 'MQ' tests
        .build()
        .set_publish_options(
            version=version("service-provider"),
            url=BROKER_URL,
            tags=["files"],
        )
    )
    verif.verify()
