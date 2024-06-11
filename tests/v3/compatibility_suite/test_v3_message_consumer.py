"""V3 Message consumer feature tests."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any, Generator, NamedTuple, Tuple

from pytest_bdd import (
    given,
    parsers,
    scenario,
    then,
    when,
)

from pact.v3.pact import AsyncMessageInteraction, Pact
from tests.v3.compatibility_suite.util import FIXTURES_ROOT, parse_markdown_table


class PactInteraction(NamedTuple):
    """Holder class for Pact and Interaction."""

    pact: Pact
    interaction: AsyncMessageInteraction


class PactResult(NamedTuple):
    """Holder class for Pact Result objects."""

    received_payload: ReceivedPayload
    pact_data: dict[str, Any] | None
    error: Exception | None


class ReceivedPayload(NamedTuple):
    """Holder class for Message Received Payload."""

    message: Any
    context: Any


class UnknownTypeError(Exception):
    """Unknown type error."""

    def __init__(self, expected_type: str) -> None:
        """Initialize the UnknownTypeError."""
        super().__init__(f"Unknown type: {expected_type}")


class UnknownGeneratorCategoryError(Exception):
    """Unknown type error."""

    def __init__(self, generator_category: str) -> None:
        """Initialize the UnknownGeneratorCategoryError."""
        super().__init__(f"Unknown generator category: {generator_category}")


class TestFailedError(Exception):
    """Test failed error."""

    def __init__(self) -> None:
        """Initialize the TestFailedError."""
        super().__init__("Test failed")


@scenario(
    "definition/features/V3/message_consumer.feature",
    "Supports arbitrary message metadata",
)
def test_supports_arbitrary_message_metadata() -> None:
    """Supports arbitrary message metadata."""


@scenario(
    "definition/features/V3/message_consumer.feature",
    "Supports data for provider states",
)
def test_supports_data_for_provider_states() -> None:
    """Supports data for provider states."""


@scenario(
    "definition/features/V3/message_consumer.feature",
    "Supports specifying provider states",
)
def test_supports_specifying_provider_states() -> None:
    """Supports specifying provider states."""


@scenario(
    "definition/features/V3/message_consumer.feature",
    "Supports the use of generators with message metadata",
)
def test_supports_the_use_of_generators_with_message_metadata() -> None:
    """Supports the use of generators with message metadata."""


@scenario(
    "definition/features/V3/message_consumer.feature",
    "Supports the use of generators with the message body",
)
def test_supports_the_use_of_generators_with_the_message_body() -> None:
    """Supports the use of generators with the message body."""


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


################################################################################
## Given
################################################################################


@given(
    "a message integration is being defined for a consumer test",
    target_fixture="pact_interaction",
)
def a_message_integration_is_being_defined_for_a_consumer_test() -> (
    Generator[tuple[Pact, AsyncMessageInteraction], Any, None]
):
    """A message integration is being defined for a consumer test."""
    pact = Pact("consumer", "provider")
    pact.with_specification("V3")
    yield PactInteraction(pact, pact.upon_receiving("a request", "Async"))


@given("a message is defined")
def _a_message_is_defined() -> None:
    """A message is defined."""


@given(
    parsers.re(
        r'a provider state "(?P<state>[^"]+)" for the message '
        r"is specified with the following data:\n(?P<table>.+)",
        re.DOTALL,
    ),
    converters={"table": parse_markdown_table},
)
def a_provider_state_for_the_message_is_specified_with_the_following_data(
    pact_interaction: PactInteraction, state: str, table: list[dict[str, Any]]
) -> None:
    """A provider state for the message is specified with the following data."""
    for parameters in table:
        state_params = {k: ast.literal_eval(v) for k, v in parameters.items()}
        pact_interaction.interaction.given(state, parameters=state_params)


@given(parsers.re(r'a provider state "(?P<state>[^"]+)" for the message is specified'))
def a_provider_state_for_the_message_is_specified(
    pact_interaction: PactInteraction,
    state: str,
) -> None:
    """A provider state for the message is specified."""
    pact_interaction.interaction.given(state)


@given(
    parsers.re(
        "the message contains the following " "metadata:\n(?P<table>.+)", re.DOTALL
    ),
    converters={"table": parse_markdown_table},
)
def the_message_contains_the_following_metadata(
    pact_interaction: PactInteraction, table: list[dict[str, Any]]
) -> None:
    """The message contains the following metadata."""
    for metadata in table:
        if metadata.get("value", "").startswith("JSON: "):
            metadata["value"] = metadata["value"].replace("JSON:", "")
        pact_interaction.interaction.with_metadata({metadata["key"]: metadata["value"]})


@given(
    parsers.re(
        "the message is configured with the following:\n" "(?P<table>.+)", re.DOTALL
    ),
    converters={"table": parse_markdown_table},
)
def the_message_is_configured_with_the_following(
    pact_interaction: PactInteraction,
    table: list[dict[str, Any]],
) -> None:
    """The message is configured with the following."""
    body_json, generator_json, metadata_json = _build_message_data(table)
    if generator_json:
        category = next(iter(generator_json.keys()))
        if category == "body":
            _build_body_generator(generator_json, body_json)
        elif category == "metadata":
            _build_metadata_generator(generator_json, metadata_json)
        else:
            raise UnknownGeneratorCategoryError(category)
    pact_interaction.interaction.with_content(json.dumps(body_json))
    for k, v in metadata_json.items():
        v_str = v
        if isinstance(v, dict):
            v_str = json.dumps(v)
        pact_interaction.interaction.with_metadata({k: str(v_str)})


@given(
    parsers.re('the message payload contains the "(?P<json_doc>[^"]+)" JSON document')
)
def the_message_payload_contains_the_basic_json_document(
    pact_interaction: PactInteraction, json_doc: str
) -> None:
    """The message payload contains the "basic" JSON document."""
    pact_interaction.interaction.with_content(json.dumps(read_json(f"{json_doc}.json")))


################################################################################
## When
################################################################################


@when(
    'the message is NOT successfully processed with a "Test failed" exception',
    target_fixture="pact_result",
)
def the_message_is_not_successfully_processed_with_an_exception(
    pact_interaction: PactInteraction,
) -> PactResult:
    """The message is NOT successfully processed with a "Test failed" exception."""
    # using a dict here because it's mutable
    received_payload: dict[str, ReceivedPayload] = {}

    def fail(async_message: str | dict[Any, Any], context: dict[Any, Any]) -> None:
        received_payload["data"] = ReceivedPayload(async_message, context)
        raise TestFailedError

    try:
        pact_interaction.interaction.verify(fail)
        return PactResult(received_payload["data"], None, None)
    except Exception as e:  # noqa: BLE001
        return PactResult(received_payload["data"], None, e)


@when("the message is successfully processed", target_fixture="pact_result")
def the_message_is_successfully_processed(
    pact_interaction: PactInteraction, temp_dir: Path
) -> Generator[PactResult, Any, None]:
    """The message is successfully processed."""
    received_payload: dict[str, ReceivedPayload] = {}

    def handler(
        async_message: str | dict[Any, Any],
        context: dict[Any, Any],
    ) -> None:
        received_payload["data"] = ReceivedPayload(async_message, context)

    pact_interaction.interaction.verify(handler)
    (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
    pact_interaction.pact.write_file(temp_dir / "pacts")
    with (temp_dir / "pacts" / "consumer-provider.json").open() as file:
        yield PactResult(received_payload.get("data"), json.load(file), None)


################################################################################
## Then
################################################################################


@then("a Pact file for the message interaction will NOT have been written")
def a_pact_file_for_the_message_interaction_will_not_have_been_written(
    temp_dir: Path,
) -> None:
    """A Pact file for the message interaction will NOT have been written."""
    assert not Path(temp_dir / "pacts" / "consumer-provider.json").exists()


@then("a Pact file for the message interaction will have been written")
def a_pact_file_for_the_message_interaction_will_have_been_written(
    temp_dir: Path,
) -> None:
    """A Pact file for the message interaction will have been written."""
    assert Path(temp_dir / "pacts" / "consumer-provider.json").exists()


@then(parsers.re(r'the consumer test error will be "(?P<error>[^"]+)"'))
def the_consumer_test_error_will_be_test_failed(
    pact_result: PactResult,
    error: str,
) -> None:
    """The consumer test error will be "Test failed"."""
    assert str(pact_result.error) == error


@then("the consumer test will have failed")
def the_consumer_test_will_have_failed(pact_result: PactResult) -> None:
    """The consumer test will have failed."""
    assert type(pact_result.error) == TestFailedError
    assert pact_result.pact_data is None


@then("the consumer test will have passed")
def the_consumer_test_will_have_passed(pact_result: PactResult) -> None:
    """The consumer test will have passed."""
    assert pact_result.error is None
    assert pact_result.pact_data is not None


@then(
    parsers.re(
        r"the first message in the Pact file will contain "
        'provider state "(?P<state>[^"]+)"'
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
    found = False
    for provider_state in messages[0]["providerStates"]:
        if state in list(provider_state.values()):
            found = True
            break
    assert found


@then(
    parsers.re(
        r"the first message in the pact file content type "
        'will be "(?P<content_type>[^"]+)"'
    )
)
def the_first_message_in_the_pact_file_content_type_will_be(
    pact_result: PactResult,
    content_type: str,
) -> None:
    """The first message in the pact file content type will be "application/json"."""
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
        "(?P<state_count>[0-9]+) provider states?"
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
        "the first message in the pact file will contain "
        'the "(?P<json_doc>[^"]+)" document'
    )
)
def the_first_message_in_the_pact_file_will_contain_the_basic_json_document(
    pact_result: PactResult, json_doc: str
) -> None:
    """The first message in the pact file will contain the "basic.json" document."""
    if not pact_result.pact_data:
        msg = "No pact data found"
        raise RuntimeError(msg)
    messages: list[dict[str, Any]] = pact_result.pact_data["messages"]
    if not isinstance(messages, list) or not messages:
        msg = "No messages found"
        raise RuntimeError(msg)
    assert messages[0]["contents"] == read_json(json_doc)


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
        r'the message contents for "(?P<replace_token>[^"]+)" '
        'will have been replaced with an? "(?P<expected_type>[^"]+)"'
    )
)
def the_message_contents_will_have_been_replaced_with(
    pact_result: PactResult,
    replace_token: str,
    expected_type: str,
) -> None:
    """The message contents for "$.one" will have been replaced with an "integer"."""
    elem_key = replace_token.split(".")[1]
    value = json.loads(pact_result.received_payload.message).get(elem_key)
    assert compare_type(expected_type, value)


@then(
    parsers.parse(
        "the pact file will contain {interaction_count:d} message interaction"
    )
)
def the_pact_file_will_contain_message_interaction(
    pact_result: PactResult,
    interaction_count: int,
) -> None:
    """The pact file will contain 1 message interaction."""
    if not pact_result.pact_data:
        msg = "No pact data found"
        raise RuntimeError(msg)
    messages: list[Any] = pact_result.pact_data["messages"]
    assert len(messages) == interaction_count


@then(
    parsers.re(
        r'the provider state "(?P<state>[^"]+)" for the message '
        r"will contain the following parameters:\n(?P<parameters>.+)",
        re.DOTALL,
    ),
    converters={"parameters": parse_markdown_table},
)
def the_provider_state_for_the_message_will_contain_the_following_parameters(
    pact_interaction: PactInteraction,
    state: str,
    parameters: list[dict[str, Any]],
) -> None:
    """The provider state for the message will contain the following parameters."""
    provider_state_params = None
    expected_params = json.loads(parameters[0]["parameters"])
    for provider_state in pact_interaction.pact.get_provider_states():
        if provider_state["name"] == state:
            provider_state_params = provider_state["params"]
            break
    # if we have provider_state_params, we found the expected provider state name
    assert provider_state_params is not None
    found = {k: False for k in expected_params}
    for k, v in expected_params.items():
        assert ast.literal_eval(provider_state_params.get(k)) == v
        found[k] = True
    assert all(found.values())


@then(
    parsers.re(r'the received message content type will be "(?P<content_type>[^"]+)"')
)
def the_received_message_content_type_will_be(
    pact_result: PactResult,
    content_type: str,
) -> None:
    """The received message content type will be "application/json"."""
    import pdb; pdb.set_trace()
    assert pact_result.received_payload.context.get("contentType") == content_type


@then(
    parsers.re(
        r'the received message metadata will contain "(?P<key>[^"]+)" '
        'replaced with an? "(?P<expected_type>[^"]+)"'
    )
)
def the_received_message_metadata_will_contain_replaced_with(
    pact_result: PactResult,
    key: str,
    expected_type: str,
) -> None:
    """The received message metadata will contain "ID" replaced with an "integer"."""
    found = False
    metadata = pact_result.received_payload.context
    if metadata.get(key):
        assert compare_type(expected_type, metadata[key])
        found = True
    assert found


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
    """The received message metadata will contain "Origin" == "Some Text"."""
    if value.startswith("JSON: "):
        value = value.replace("JSON: ", "")
        value = value.replace('\\"', '"')
        value = json.loads(value)
    metadata = pact_result.received_payload.context

    found = False
    if metadata.get(key):
        assert metadata[key] == value
        found = True
    assert found


@then(
    parsers.re(
        r"the received message payload will contain "
        'the "(?P<json_doc>[^"]+)" JSON document'
    )
)
def the_received_message_payload_will_contain_the_basic_json_document(
    pact_result: PactResult, json_doc: str
) -> None:
    """The received message payload will contain the "basic" JSON document."""
    assert json.loads(pact_result.received_payload.message) == read_json(f"{json_doc}.json")


def read_json(file: str) -> dict[str, Any]:
    with Path(FIXTURES_ROOT / file).open() as f:
        return json.loads(f.read())


def compare_type(expected_type: str, t: str | int | None) -> bool:
    if expected_type == "integer":
        assert t is not None
        try:
            int(t)
        except ValueError:
            return False
        return True
    raise UnknownTypeError(expected_type)


def _build_message_data(
    table: list[dict[str, Any]],
) -> Tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    body_json = generator_json = metadata_json = {}
    for entry in table:
        for k, v in entry.items():
            if k == "generators":
                if v.startswith("JSON: "):
                    generator_json = json.loads(v.replace("JSON:", ""))
                else:
                    generator_json = read_json(v)
            elif k == "body":
                if v.startswith("file: "):
                    file = v.replace("file: ", "")
                    body_json = read_json(file)
            elif k == "metadata":
                metadata_json = json.loads(v)
    return body_json, generator_json, metadata_json


def _build_body_generator(
    generator_json: dict[str, Any], body_json: dict[str, Any]
) -> None:
    for k, v in generator_json["body"].items():
        elem_name = k.split(".")[1]
        body_elem = body_json.get(elem_name)
        replace_value = {
            "pact:generator:type": v["type"],
            "pact:matcher:type": "notEmpty",
            "value": body_elem,
        }
        body_json.update({elem_name: replace_value})


def _build_metadata_generator(
    generator_json: dict[str, Any], metadata_json: dict[str, Any]
) -> None:
    for k in generator_json["metadata"]:
        metadata = metadata_json[k]
        if not isinstance(metadata, dict):
            metadata = {"value": metadata}
            metadata_json[k] = metadata
        generator_data = generator_json["metadata"][k]
        metadata.update({
            "pact:generator:type": generator_data["type"],
            "pact:matcher:type": "notEmpty",
        })
        del generator_data["type"]
        metadata.update(generator_data)
