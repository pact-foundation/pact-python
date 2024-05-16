from __future__ import annotations

import json
import logging
import re
import os
import pytest
from collections import namedtuple
from tempfile import TemporaryDirectory
from typing import Any, Generator

import ast
from jsonpath_ng import parse
from pytest_bdd import (
    given,
    parsers,
    scenario,
    then,
    when,
)

from pact.v3.pact import AsyncMessageInteraction, MessagePact as Pact
from tests.v3.compatibility_suite.util import parse_markdown_table

logger = logging.getLogger(__name__)

PactInteraction = namedtuple("PactInteraction", ["pact", "interaction"])
PactResult = namedtuple('PactResult', ['received_payload', 'pact_data', 'error'])
ReceivedPayload = namedtuple('ReceivedPayload', ['message', 'context'])

NUM_RE = re.compile(r'^-?[.0-9]+$')

TEST_PACT_FILE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'pacts')

def read_json(file):
    with open(os.path.join(os.path.dirname(__file__),'definition','fixtures',file)) as f:
        return json.loads(f.read())

def compare_type(expected_type, t):
    if expected_type == 'integer':
        try:
            int(t)
            return True
        except ValueError:
            return False
    else:
        raise ValueError(f'Unknown type: {expected_type}')

@pytest.fixture(autouse=True)
def handle_pact_file_directory():
    if not os.path.exists(TEST_PACT_FILE_DIRECTORY):
        os.mkdir(TEST_PACT_FILE_DIRECTORY)
    yield
    os.rmdir(TEST_PACT_FILE_DIRECTORY)

@scenario(
    'definition/features/V3/message_consumer.feature',
    'Supports arbitrary message metadata'
)
def test_supports_arbitrary_message_metadata() -> None:
    """Supports arbitrary message metadata."""


@scenario(
    'definition/features/V3/message_consumer.feature',
    'Supports data for provider states'
)
def test_supports_data_for_provider_states() -> None:
    """Supports data for provider states."""


@scenario(
    'definition/features/V3/message_consumer.feature',
    'Supports specifying provider states'
)
def test_supports_specifying_provider_states() -> None:
    """Supports specifying provider states."""


@scenario(
    'definition/features/V3/message_consumer.feature',
    'Supports the use of generators with message metadata'
)
def test_supports_the_use_of_generators_with_message_metadata() -> None:
    """Supports the use of generators with message metadata."""


@scenario(
    'definition/features/V3/message_consumer.feature',
    'Supports the use of generators with the message body'
)
def test_supports_the_use_of_generators_with_the_message_body() -> None:
    """Supports the use of generators with the message body."""


@scenario(
    'definition/features/V3/message_consumer.feature',
    'When all messages are successfully processed'
)
def test_when_all_messages_are_successfully_processed() -> None:
    """When all messages are successfully processed."""


@scenario(
    'definition/features/V3/message_consumer.feature',
    'When not all messages are successfully processed'
)
def test_when_not_all_messages_are_successfully_processed() -> None:
    """When not all messages are successfully processed."""


################################################################################
## Given
################################################################################


@given(
    'a message integration is being defined for a consumer test',
    target_fixture='pact_interaction'
)
def a_message_integration_is_being_defined_for_a_consumer_test() -> (
    Generator[tuple[Pact, AsyncMessageInteraction], Any, None]
):
    """a message integration is being defined for a consumer test."""
    pact = Pact("message_consumer", "message_provider")
    pact.with_specification("V3")
    yield PactInteraction(pact, pact.upon_receiving("a request", "Async"))


@given('a message is defined')
def a_message_is_defined(pact_interaction: PactInteraction):
    """a message is defined."""
    print('A message is being defined. This is not yet implemented')


@given(
    parsers.re(
        r'a provider state "(?P<state>[^"]+)" for the message '
        r'is specified with the following data:\n(?P<table>.+)',
        re.DOTALL,
    ),
    converters={"table": parse_markdown_table},
)
def a_provider_state_for_the_message_is_specified_with_the_following_data(
    pact_interaction: PactInteraction,
    state: str,
    table: list[dict[str, Any]]
):
    """a provider state for the message is specified with the following data:"""
    for parameters in table:
        state_params = { k: ast.literal_eval(v) for k, v in parameters.items() }
        pact_interaction.interaction.given(state, parameters=state_params)


@given(
    parsers.re(r'a provider state "(?P<state>[^"]+)" for the message is specified')
)
def a_provider_state_for_the_message_is_specified(
    pact_interaction: PactInteraction,
    state: str,
):
    """a provider state for the message is specified."""
    pact_interaction.interaction.given(state)


@given(
    parsers.re('the message contains the following metadata:\n(?P<table>.+)', re.DOTALL),
    converters={"table": parse_markdown_table},
)
def the_message_contains_the_following_metadata(
    pact_interaction: PactInteraction,
    table: list[dict[str, Any]]
):
    """the message contains the following metadata:"""
    for metadata in table:
        if metadata.get('value','').startswith('JSON: '):
            metadata['value'] = metadata['value'].replace('JSON:', '')
        pact_interaction.interaction.with_metadata({metadata['key']: metadata['value']})


@given(
    parsers.re('the message is configured with the following:\n(?P<table>.+)', re.DOTALL),
    converters={"table": parse_markdown_table},
)
def the_message_is_configured_with_the_following(
    pact_interaction: PactInteraction,
    table: list[dict[str, Any]],
):
    """the message is configured with the following:"""
    body_json = generator_json = metadata_json = {}
    for entry in table:
        for k, v in entry.items():
            if k == 'generators':
                if v.startswith('JSON: '):
                    generator_json = json.loads(v.replace('JSON:', ''))
                else:
                    generator_json = read_json(v)
            elif k == 'body':
                if v.startswith('file: '):
                    file = v.replace('file: ', '')
                    body_json = read_json(file)
            elif k == 'metadata':
                metadata_json = json.loads(v)
    if generator_json:
        category = list(generator_json.keys())[0]
        if category == 'body':
            for k, v in generator_json['body'].items():
                path = parse(k)
                current_values = [match.value for match in path.find(body_json)]
                matches = path.find(body_json)
                for i, match in enumerate(matches):
                    generator_type = v['type']
                    del v['type']
                    replacement_value = {
                        'value': current_values[i],
                        'pact:matcher:type': 'notEmpty',
                        'pact:generator:type': generator_type,
                    }
                    replacement_value.update(v)
                    matches[i].full_path.update(body_json, replacement_value)
        elif category == 'metadata':
            for k in generator_json['metadata'].keys():
                metadata = metadata_json[k]
                if not isinstance(metadata, dict):
                    metadata = { 'value': metadata }
                    metadata_json[k] = metadata
                generator_data = generator_json['metadata'][k]
                metadata.update({
                    'pact:generator:type': generator_data['type'],
                    'pact:matcher:type': 'notEmpty',
                })
                del generator_data['type']
                metadata.update(generator_data)
        else:
            raise ValueError(f'Unknown generator category: {category}')
    pact_interaction.interaction.with_content(body_json)
    for k, v in metadata_json.items():
        if isinstance(v, dict):
            v = json.dumps(v)
        pact_interaction.interaction.with_metadata({k: str(v)})


@given(
    parsers.re('the message payload contains the "(?P<json_doc>[^"]+)" JSON document')
)
def the_message_payload_contains_the_basic_json_document(
    pact_interaction: PactInteraction,
    json_doc: str
):
    """the message payload contains the "basic" JSON document."""
    pact_interaction.interaction.with_content(read_json(f'{json_doc}.json'))


################################################################################
## When
################################################################################


@when(
    'the message is NOT successfully processed with a "Test failed" exception',
    target_fixture="pact_result"
)
def the_message_is_not_successfully_processed_with_an_exception(
    pact_interaction: PactInteraction
):
    """the message is NOT successfully processed with a "Test failed" exception."""
    # using a dict here because it's mutable
    received_payload = {'data': None}
    def fail(async_message, context):
        received_payload['data'] = ReceivedPayload(async_message, context)
        raise Exception('Test failed')
    try:
        pact_interaction.pact.verify(fail)
    except Exception as e:
        return PactResult(received_payload['data'], None, e)


@when(
    'the message is successfully processed',
    target_fixture="pact_result"
)
def the_message_is_successfully_processed(
    pact_interaction: PactInteraction
):
    """the message is successfully processed."""
    received_payload = {'data': None}
    def handler(async_message, context):
        received_payload['data'] = ReceivedPayload(async_message, context)
    pact_interaction.pact.verify(handler)
    pact_interaction.pact.write_file(TEST_PACT_FILE_DIRECTORY, overwrite=True)
    with open(os.path.join(TEST_PACT_FILE_DIRECTORY, 'message_consumer-message_provider.json')) as file:
        yield PactResult(received_payload['data'], json.load(file), None)
    os.remove(os.path.join(TEST_PACT_FILE_DIRECTORY, 'message_consumer-message_provider.json'))


################################################################################
## Then
################################################################################


@then('a Pact file for the message interaction will NOT have been written')
def a_pact_file_for_the_message_interaction_will_not_have_been_written():
    """a Pact file for the message interaction will NOT have been written."""
    assert not os.path.exists(os.path.join(TEST_PACT_FILE_DIRECTORY, 'message_consumer-message_provider.json'))


@then('a Pact file for the message interaction will have been written')
def a_pact_file_for_the_message_interaction_will_have_been_written():
    """a Pact file for the message interaction will have been written."""
    assert os.path.exists(os.path.join(TEST_PACT_FILE_DIRECTORY, 'message_consumer-message_provider.json'))


@then(
    parsers.re(r'the consumer test error will be "(?P<error>[^"]+)"')
)
def the_consumer_test_error_will_be_test_failed(
    pact_result: PactResult,
    error: str,
):
    """the consumer test error will be "Test failed"."""
    assert str(pact_result.error) == error


@then('the consumer test will have failed')
def the_consumer_test_will_have_failed(
    pact_result: PactResult
):
    """the consumer test will have failed."""
    assert type(pact_result.error) == Exception
    assert pact_result.pact_data is None


@then('the consumer test will have passed')
def the_consumer_test_will_have_passed(
    pact_result: PactResult
):
    """the consumer test will have passed."""
    assert pact_result.error is None
    assert pact_result.pact_data is not None


@then(
    parsers.re(r'the first message in the Pact file will contain provider state "(?P<state>[^"]+)"')
)
def the_first_message_in_the_pact_file_will_contain_provider_state(
    pact_result: PactResult,
    state: str,
):
    """the first message in the Pact file will contain provider state."""
    assert state in [
        provider_state['name']
        for provider_state in pact_result.pact_data['messages'][0]['providerStates']
    ]


@then(
    parsers.re(r'the first message in the pact file content type will be "(?P<content_type>[^"]+)"')
)
def the_first_message_in_the_pact_file_content_type_will_be(
    pact_result: PactResult,
    content_type: str,
):
    """the first message in the pact file content type will be "application/json"."""
    assert pact_result.pact_data['messages'][0]['metadata']['contentType'] == content_type


@then(
    parsers.re(r'the first message in the pact file will contain (?P<state_count>[0-9]+) provider states?'),
    converters={"state_count": int},
)
def the_first_message_in_the_pact_file_will_contain(
    pact_result: PactResult,
    state_count: int,
):
    """the first message in the pact file will contain 1 provider state."""
    assert len(pact_result.pact_data['messages'][0]['providerStates']) == state_count


@then(
    parsers.re('the first message in the pact file will contain the "(?P<json_doc>[^"]+)" document')
)
def the_first_message_in_the_pact_file_will_contain_the_basic_json_document(
    pact_result: PactResult,
    json_doc: str
):
    """the first message in the pact file will contain the "basic.json" document."""
    assert pact_result.pact_data['messages'][0]['contents'] == read_json(json_doc)


@then(
    parsers.re(
        r'the first message in the pact file will contain '
        r'the message metadata "(?P<key>[^"]+)" == "(?P<value>[^"\\]*(?:\\.[^"\\]*)*)"'
    )
)
def the_first_message_in_the_pact_file_will_contain_the_message_metadata(
    pact_result: PactResult,
    key: str,
    value: Any,
):
    """the first message in the pact file will contain the message metadata "Origin" == "Some Text"."""
    if value.startswith('JSON: '):
        value = value.replace('JSON: ', '')
        value = value.replace('\\"', '"')
        value = json.loads(value)
    assert pact_result.pact_data['messages'][0]['metadata'][key] == value


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
):
    """the message contents for "$.one" will have been replaced with an "integer"."""
    path = parse(replace_token)
    values = [match.value for match in path.find(pact_result.received_payload.message)]
    for v in values:
        assert compare_type(expected_type, v)


@then(
    parsers.parse('the pact file will contain {interaction_count:d} message interaction')
)
def the_pact_file_will_contain_message_interaction(
    pact_result: PactResult,
    interaction_count: int,
):
    """the pact file will contain 1 message interaction."""
    assert len(pact_result.pact_data['messages']) == interaction_count


@then(
    parsers.re(
        r'the provider state "(?P<state>[^"]+)" for the message '
        r'will contain the following parameters:\n(?P<parameters>.+)',
        re.DOTALL,
    ),
    converters={"parameters": parse_markdown_table},
)
def the_provider_state_for_the_message_will_contain_the_following_parameters(
    pact_interaction: PactInteraction,
    pact_result: PactResult,
    state: str,
    parameters: list[dict[str, Any]],
):
    """the provider state "a user exists" for the message will contain the following parameters:
| parameters                                     |
| {"age":66,"name":"Test Guy","username":"Test"} |."""
    print(
        f'The provider state "{state}" for the message will contain '
        f'the following parameters: {parameters}, got {pact_result}'
    )
    provider_state_params = None
    expected_params = json.loads(parameters[0]['parameters'])
    for provider_state in pact_interaction.pact.get_provider_states():
        if provider_state['name'] == state:
            provider_state_params = provider_state['params']
            break
    # if we have provider_state_params, we found the expected provider state name
    assert provider_state_params is not None
    found = { k: False for k in expected_params.keys() }
    for k, v in expected_params.items():
        for provider_state_param in provider_state_params:
            if provider_state_param.get(k):
                assert ast.literal_eval(provider_state_param[k]) == v
                found[k] = True
                break
    assert all(found.values())

@then(
    parsers.re(r'the received message content type will be "(?P<content_type>[^"]+)"')
)
def the_received_message_content_type_will_be(
    pact_result: PactResult,
    content_type: str,
):
    """the received message content type will be "application/json"."""
    assert any([context.get('contentType') == content_type for context in pact_result.received_payload.context])

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
):
    """the received message metadata will contain "ID" replaced with an "integer"."""
    found = False
    for metadata in pact_result.received_payload.context:
        if metadata.get(key):
            assert compare_type(expected_type, metadata[key])
            found = True
    assert found


@then(
    parsers.re(
        r'the received message metadata will contain "(?P<key>[^"]+)" == "(?P<value>[^"\\]*(?:\\.[^"\\]*)*)"'
    )
)
def the_received_message_metadata_will_contain(
    pact_result: PactResult,
    key: str,
    value: Any,
):
    """the received message metadata will contain "Origin" == "Some Text"."""
    found = False
    if value.startswith('JSON: '):
        value = value.replace('JSON: ', '')
        value = value.replace('\\"', '"')
        value = json.loads(value)
    for metadata in pact_result.received_payload.context:
        if metadata.get(key):
            if isinstance(value, dict):
                assert json.loads(metadata[key]) == value
            elif NUM_RE.match(metadata[key]):
                assert ast.literal_eval(metadata[key]) == value
            else:
                assert metadata[key] == value
            found = True
    assert found


@then(
    parsers.re('the received message payload will contain the "(?P<json_doc>[^"]+)" JSON document')
)
def the_received_message_payload_will_contain_the_basic_json_document(
    pact_result: PactResult,
    json_doc: str
):
    """the received message payload will contain the "basic" JSON document."""
    assert pact_result.received_payload.message == read_json(f'{json_doc}.json')

