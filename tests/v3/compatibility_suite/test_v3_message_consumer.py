"""V3 Message consumer feature tests."""

from __future__ import annotations

import ast
import json
import logging
import re
from typing import TYPE_CHECKING, Any, List, NamedTuple

from pytest_bdd import (
    given,
    parsers,
    scenario,
    then,
    when,
)

from tests.v3.compatibility_suite.util import (
    FIXTURES_ROOT,
    PactInteractionTuple,
    parse_markdown_table,
)
from tests.v3.compatibility_suite.util.consumer import (
    a_message_integration_is_being_defined_for_a_consumer_test,
)

if TYPE_CHECKING:
    from pathlib import Path

    from pact.v3.pact import AsyncMessageInteraction, InteractionVerificationError

logger = logging.getLogger(__name__)

################################################################################
## Helpers
################################################################################


class ReceivedMessage(NamedTuple):
    """Holder class for Message Received Payload."""

    body: Any
    context: Any


class PactResult(NamedTuple):
    """Holder class for Pact Result objects."""

    messages: List[ReceivedMessage]
    pact_data: dict[str, Any] | None
    errors: List[InteractionVerificationError]


def assert_type(expected_type: str, value: Any) -> None:  # noqa: ANN401
    logger.debug("Ensuring that %s is of type %s", value, expected_type)
    if expected_type == "integer":
        assert value is not None
        assert isinstance(value, int) or re.match(r"^\d+$", value)
    else:
        msg = f"Unknown type: {expected_type}"
        raise ValueError(msg)


################################################################################
## Scenarios
################################################################################


@scenario(
    "definition/features/V3/message_consumer.feature",
    "When all messages are successfully processed",
)
def test_when_all_messages_are_successfully_processed() -> None:
    """When all messages are successfully processed."""


@scenario(
    "definition/features/V3/message_consumer.feature",
    "When not all messages are successfully processed",
)
def test_when_not_all_messages_are_successfully_processed() -> None:
    """When not all messages are successfully processed."""


@scenario(
    "definition/features/V3/message_consumer.feature",
    "Supports arbitrary message metadata",
)
def test_supports_arbitrary_message_metadata() -> None:
    """Supports arbitrary message metadata."""


@scenario(
    "definition/features/V3/message_consumer.feature",
    "Supports specifying provider states",
)
def test_supports_specifying_provider_states() -> None:
    """Supports specifying provider states."""


@scenario(
    "definition/features/V3/message_consumer.feature",
    "Supports data for provider states",
)
def test_supports_data_for_provider_states() -> None:
    """Supports data for provider states."""


@scenario(
    "definition/features/V3/message_consumer.feature",
    "Supports the use of generators with the message body",
)
def test_supports_the_use_of_generators_with_the_message_body() -> None:
    """Supports the use of generators with the message body."""


@scenario(
    "definition/features/V3/message_consumer.feature",
    "Supports the use of generators with message metadata",
)
def test_supports_the_use_of_generators_with_message_metadata() -> None:
    """Supports the use of generators with message metadata."""


################################################################################
## Given
################################################################################


a_message_integration_is_being_defined_for_a_consumer_test("V3")


@given(
    parsers.re(
        r'a provider state "(?P<state>[^"]+)" for the message is specified'
        r"( with the following data:\n)?(?P<table>.*)",
        re.DOTALL,
    ),
    converters={"table": lambda v: parse_markdown_table(v) if v else None},
)
def a_provider_state_for_the_message_is_specified_with_the_following_data(
    pact_interaction: PactInteractionTuple[AsyncMessageInteraction],
    state: str,
    table: list[dict[str, str]] | None,
) -> None:
    """A provider state for the message is specified with the following data."""
    logger.debug("Specifying provider state '%s': %s", state, table)
    if table:
        parameters = {k: ast.literal_eval(v) for k, v in table[0].items()}
        pact_interaction.interaction.given(state, parameters=parameters)
    else:
        pact_interaction.interaction.given(state)


@given("a message is defined")
def a_message_is_defined() -> None:
    """A message is defined."""


@given(
    parsers.re(
        r"the message contains the following metadata:\n(?P<table>.+)",
        re.DOTALL,
    ),
    converters={"table": parse_markdown_table},
)
def the_message_contains_the_following_metadata(
    pact_interaction: PactInteractionTuple[AsyncMessageInteraction],
    table: list[dict[str, Any]],
) -> None:
    """The message contains the following metadata."""
    logger.debug("Adding metadata to message: %s", table)
    for metadata in table:
        if metadata.get("value", "").startswith("JSON: "):
            metadata["value"] = metadata["value"].replace("JSON:", "")
        pact_interaction.interaction.with_metadata({metadata["key"]: metadata["value"]})


@given(
    parsers.re(
        r"the message is configured with the following:\n(?P<table>.+)",
        re.DOTALL,
    ),
    converters={"table": parse_markdown_table},
)
def the_message_is_configured_with_the_following(
    pact_interaction: PactInteractionTuple[AsyncMessageInteraction],
    table: list[dict[str, Any]],
) -> None:
    """The message is configured with the following."""
    assert len(table) == 1, "Only one row is expected"
    config: dict[str, str] = table[0]

    if body := config.pop("body", None):
        if body.startswith("file: "):
            file = FIXTURES_ROOT / body.replace("file: ", "")
            content_type = "application/json" if file.suffix == ".json" else None
            pact_interaction.interaction.with_body(file.read_text(), content_type)
        else:
            msg = f"Unsupported body configuration: {config['body']}"
            raise ValueError(msg)

    if generators := config.pop("generators", None):
        if generators.startswith("JSON: "):
            data = json.loads(generators.replace("JSON: ", ""))
            pact_interaction.interaction.with_generators(data)
        else:
            file = FIXTURES_ROOT / generators
            pact_interaction.interaction.with_generators(file.read_text())

    if metadata := config.pop("metadata", None):
        data = json.loads(metadata)
        pact_interaction.interaction.with_metadata({
            k: json.dumps(v) for k, v in data.items()
        })

    if config:
        msg = f"Unknown configuration keys: {', '.join(config.keys())}"
        raise ValueError(msg)


@given(
    parsers.re(r'the message payload contains the "(?P<basename>[^"]+)" JSON document')
)
def the_message_payload_contains_the_basic_json_document(
    pact_interaction: PactInteractionTuple[AsyncMessageInteraction],
    basename: str,
) -> None:
    """The message payload contains the "basic" JSON document."""
    json_path = FIXTURES_ROOT / f"{basename}.json"
    if not json_path.is_file():
        msg = f"File not found: {json_path}"
        raise FileNotFoundError(msg)
    pact_interaction.interaction.with_body(
        json_path.read_text(),
        content_type="application/json",
    )


################################################################################
## When
################################################################################


@when("the message is successfully processed", target_fixture="pact_result")
def the_message_is_successfully_processed(
    pact_interaction: PactInteractionTuple[AsyncMessageInteraction],
    temp_dir: Path,
) -> PactResult:
    """The message is successfully processed."""
    messages: list[ReceivedMessage] = []

    def handler(
        body: str | bytes | None,
        context: dict[str, str],
    ) -> None:
        messages.append(ReceivedMessage(body, context))

    # While the expectation is that the message will be processed successfully,
    # we don't raise an exception and instead capture any errors that occur.
    errors = pact_interaction.pact.verify(handler, "Async", raises=False)
    if errors:
        logger.error("%d errors occured during verification:", len(errors))
        for error in errors:
            logger.error(error)
        msg = "Errors occurred during verification"
        raise AssertionError(msg)

    (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
    pact_interaction.pact.write_file(temp_dir / "pacts")
    with (temp_dir / "pacts" / "consumer-provider.json").open() as file:
        pact_data = json.load(file)

    return PactResult(messages, pact_data, errors)


@when(
    parsers.re(
        r"the message is NOT successfully processed "
        r'with a "(?P<failure>[^"]+)" exception'
    ),
    target_fixture="pact_result",
)
def the_message_is_not_successfully_processed_with_an_exception(
    pact_interaction: PactInteractionTuple[AsyncMessageInteraction],
    failure: str,
) -> PactResult:
    """The message is NOT successfully processed with a "Test failed" exception."""
    messages: list[ReceivedMessage] = []

    def handler(body: str | bytes | None, context: dict[str, str]) -> None:
        messages.append(ReceivedMessage(body, context))
        raise AssertionError(failure)

    errors = pact_interaction.pact.verify(handler, "Async", raises=False)
    return PactResult(messages, None, errors)


################################################################################
## Then
################################################################################


@then(
    parsers.re(
        r"a Pact file for the message interaction "
        r"will(?P<success>( NOT)?) have been written"
    ),
    converters={"success": lambda x: x != " NOT"},
)
def a_pact_file_for_the_message_interaction_will_maybe_have_been_written(
    temp_dir: Path,
    success: bool,  # noqa: FBT001
) -> None:
    """A Pact file for the message interaction will maybe have been written."""
    assert (temp_dir / "pacts" / "consumer-provider.json").exists() == success


@then(parsers.re(r'the consumer test error will be "(?P<error>[^"]+)"'))
def the_consumer_test_error_will_be_test_failed(
    pact_result: PactResult,
    error: str,
) -> None:
    """The consumer test error will be "Test failed"."""
    assert len(pact_result.errors) == 1
    assert error in str(pact_result.errors[0].error)


@then(
    parsers.re(r"the consumer test will have (?P<success>passed|failed)"),
    converters={"success": lambda x: x == "passed"},
)
def the_consumer_test_will_have_passed_or_failed(
    pact_result: PactResult,
    success: bool,  # noqa: FBT001
) -> None:
    """The consumer test will have passed or failed."""
    assert (len(pact_result.errors) == 0) == success


@then(
    parsers.re(
        r"the first message in the pact file content type "
        r'will be "(?P<content_type>[^"]+)"'
    )
)
def the_first_message_in_the_pact_file_content_type_will_be(
    pact_result: PactResult,
    content_type: str,
) -> None:
    """The first message in the pact file content type will be."""
    if not pact_result.pact_data:
        msg = "No pact data found"
        raise RuntimeError(msg)
    messages: list[dict[str, dict[str, Any]]] = pact_result.pact_data["messages"]
    if not isinstance(messages, list) or not messages:
        msg = "No messages found"
        raise RuntimeError(msg)
    assert messages[0].get("metadata", {}).get("contentType") == content_type


@then(
    parsers.re(
        r"the first message in the pact file will contain "
        r"(?P<state_count>\d+) provider states?"
    ),
    converters={"state_count": int},
)
def the_first_message_in_the_pact_file_will_contain(
    pact_result: PactResult,
    state_count: int,
) -> None:
    """The first message in the pact file will contain 1 provider state."""
    if not pact_result.pact_data:
        msg = "No pact data found"
        raise RuntimeError(msg)
    messages: list[dict[str, list[Any]]] = pact_result.pact_data["messages"]
    if not isinstance(messages, list) or not messages:
        msg = "No messages found"
        raise RuntimeError(msg)
    assert len(messages[0].get("providerStates", [])) == state_count


@then(
    parsers.re(
        r"the first message in the Pact file will contain "
        r'provider state "(?P<state>[^"]+)"'
    )
)
def the_first_message_in_the_pact_file_will_contain_provider_state(
    pact_result: PactResult,
    state: str,
) -> None:
    """The first message in the Pact file will contain provider state."""
    if not pact_result.pact_data:
        msg = "No pact data found"
        raise RuntimeError(msg)
    messages = pact_result.pact_data["messages"]
    if not isinstance(messages, list) or not messages:
        msg = "No messages found"
        raise RuntimeError(msg)
    message: dict[str, Any] = messages[0]
    provider_states: list[dict[str, Any]] = message.get("providerStates", [])
    for provider_state in provider_states:
        if provider_state["name"] == state:
            break
    else:
        msg = f"Provider state not found: {state}"
        raise AssertionError(msg)


@then(
    parsers.re(
        r"the first message in the pact file will contain "
        r'the "(?P<basename>[^"]+)" document'
    )
)
def the_first_message_in_the_pact_file_will_contain_the_basic_json_document(
    pact_result: PactResult,
    basename: str,
) -> None:
    """The first message in the pact file will contain the "basic.json" document."""
    path = FIXTURES_ROOT / basename
    if not path.is_file():
        msg = f"File not found: {path}"
        raise FileNotFoundError(msg)
    if not pact_result.pact_data:
        msg = "No pact data found"
        raise RuntimeError(msg)
    messages: list[dict[str, Any]] = pact_result.pact_data["messages"]
    if not isinstance(messages, list) or not messages:
        msg = "No messages found"
        raise RuntimeError(msg)
    try:
        assert messages[0]["contents"] == json.loads(path.read_text())
    except json.JSONDecodeError as e:
        logger.info("Error decoding JSON: %s", e)
        logger.info("Performing basic string comparison")
        assert messages[0]["contents"] == path.read_text()


@then(
    parsers.re(
        r"the first message in the pact file will contain "
        r'the message metadata "(?P<key>[^"]+)" == "(?P<value>[^"\\]*(?:\\.[^"\\]*)*)"'
    )
)
def the_first_message_in_the_pact_file_will_contain_the_message_metadata(
    pact_result: PactResult,
    key: str,
    value: Any,  # noqa: ANN401
) -> None:
    """The first message in the pact file will contain the message metadata."""
    if value.startswith("JSON: "):
        value = value.replace("JSON: ", "")
        value = value.replace('\\"', '"')
        value = json.loads(value)
    if not pact_result.pact_data:
        msg = "No pact data found"
        raise RuntimeError(msg)
    messages: list[dict[str, dict[str, Any]]] = pact_result.pact_data["messages"]
    assert messages[0]["metadata"][key] == value


@then(
    parsers.re(
        r'the message contents for "(?P<path>[^"]+)" '
        r'will have been replaced with an? "(?P<expected_type>[^"]+)"'
    )
)
def the_message_contents_will_have_been_replaced_with(
    pact_result: PactResult,
    path: str,
    expected_type: str,
) -> None:
    """The message contents for "$.one" will have been replaced with an "integer"."""
    json_path = path.split(".")
    assert len(json_path) == 2, "Only one level of nesting is supported"
    assert json_path[0] == "$", "Only root level replacement is supported"
    key = json_path[1]

    assert len(pact_result.messages) == 1
    message = pact_result.messages[0]
    value = json.loads(message.body).get(key)
    assert_type(expected_type, value)


@then(
    parsers.parse(
        "the pact file will contain {interaction_count:d} message interaction"
    )
)
def the_pact_file_will_contain_message_interaction(
    pact_result: PactResult,
    interaction_count: int,
) -> None:
    """The pact file will contain N message interaction."""
    if not pact_result.pact_data:
        msg = "No pact data found"
        raise RuntimeError(msg)
    messages: list[Any] = pact_result.pact_data["messages"]
    assert len(messages) == interaction_count


@then(
    parsers.re(
        r'the provider state "(?P<state>[^"]+)" for the message '
        r"will contain the following parameters:\n(?P<table>.+)",
        re.DOTALL,
    ),
    converters={"table": parse_markdown_table},
)
def the_provider_state_for_the_message_will_contain_the_following_parameters(
    pact_interaction: PactInteractionTuple[AsyncMessageInteraction],
    pact_result: PactResult,
    state: str,
    table: list[dict[str, Any]],
) -> None:
    """The provider state for the message will contain the following parameters."""
    assert len(table) == 1, "Only one row is expected"
    expected = json.loads(table[0]["parameters"])

    # It is unclear whether this test is meant to verify the `Interaction`
    # object, or the result as written to the Pact file. As a result, we
    # will perform both checks.

    ## Verifying the Pact File

    if not pact_result.pact_data:
        msg = "No pact data found"
        raise RuntimeError(msg)
    messages: list[dict[str, list[dict[str, Any]]]] = pact_result.pact_data["messages"]
    assert len(messages) == 1, "Only one message is expected"
    message = messages[0]

    assert len(message["providerStates"]) > 0, "At least one provider state is expected"
    provider_states = message["providerStates"]
    for provider_state_dict in provider_states:
        if provider_state_dict["name"] == state:
            assert expected == provider_state_dict["params"]
            break
    else:
        msg = f"Provider state not found in Pact file: {state}"
        raise AssertionError(msg)

    ## Verifying the Interaction Object

    for interaction in pact_interaction.pact.interactions("Async"):
        for provider_state in interaction.provider_states():
            if provider_state.name == state:
                provider_state_params = {
                    k: ast.literal_eval(v) for k, v in provider_state.parameters()
                }
                assert expected == provider_state_params
                break
        else:
            msg = f"Provider state not found: {state}"
            raise ValueError(msg)
        break
    else:
        msg = "No interactions found"
        raise ValueError(msg)


@then(
    parsers.re(r'the received message content type will be "(?P<content_type>[^"]+)"')
)
def the_received_message_content_type_will_be(
    pact_result: PactResult,
    content_type: str,
) -> None:
    """The received message content type will be "application/json"."""
    assert len(pact_result.messages) == 1
    message = pact_result.messages[0]
    assert message.context.get("contentType") == content_type


@then(
    parsers.re(
        r"the received message metadata will contain "
        r'"(?P<key>[^"]+)" == "(?P<value>[^"\\]*(?:\\.[^"\\]*)*)"'
    )
)
def the_received_message_metadata_will_contain(
    pact_result: PactResult,
    key: str,
    value: Any,  # noqa: ANN401
) -> None:
    """The received message metadata will contain."""
    # If we're given some JSON value, we will need to parse the value from the
    # `message.context` and compare it to the parsed JSON value; otherwise,
    # equivalent JSON values may not match due to formatting differences.
    json_matching = False
    if value.startswith("JSON: "):
        value = value.replace("JSON: ", "").replace(r"\"", '"')
        value = json.loads(value)
        json_matching = True

    assert len(pact_result.messages) == 1
    message = pact_result.messages[0]
    for k, v in message.context.items():
        if k == key:
            if json_matching:
                assert json.loads(v) == value
            else:
                assert v == value
            break
    else:
        msg = f"Key '{key}' not found in message metadata"
        raise AssertionError(msg)


@then(
    parsers.re(
        r'the received message metadata will contain "(?P<key>[^"]+)" '
        r'replaced with an? "(?P<expected_type>[^"]+)"'
    )
)
def the_received_message_metadata_will_contain_replaced_with(
    pact_result: PactResult,
    key: str,
    expected_type: str,
) -> None:
    """The received message metadata will contain "ID" replaced with an "integer"."""
    assert isinstance(pact_result.messages, list)
    assert len(pact_result.messages) == 1, "Only one message is expected"
    message = pact_result.messages[0]
    value = message.context.get(key)
    assert_type(expected_type, value)


@then(
    parsers.re(
        r"the received message payload will contain "
        r'the "(?P<basename>[^"]+)" JSON document'
    )
)
def the_received_message_payload_will_contain_the_basic_json_document(
    pact_result: PactResult,
    basename: str,
) -> None:
    """The received message payload will contain the JSON document."""
    json_path = FIXTURES_ROOT / f"{basename}.json"
    if not json_path.is_file():
        msg = f"File not found: {json_path}"
        raise FileNotFoundError(msg)

    assert len(pact_result.messages) == 1
    message = pact_result.messages[0]

    try:
        assert json.loads(message.body) == json.loads(json_path.read_text())
    except json.JSONDecodeError as e:
        logger.info("Error decoding JSON: %s", e)
        logger.info("Performing basic comparison")
        if isinstance(message.body, str):
            assert message.body == json_path.read_text()
        elif isinstance(message.body, bytes):
            assert message.body == json_path.read_bytes()
        else:
            msg = f"Unexpected message body type: {type(message.body).__name__}"
            raise TypeError(msg) from None
