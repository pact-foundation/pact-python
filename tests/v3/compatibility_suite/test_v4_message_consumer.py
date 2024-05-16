"""Message consumer feature tests."""
import json
import os
import pytest
from collections import namedtuple
from typing import Any

from pytest_bdd import (
    given,
    parsers,
    scenario,
    then,
    when,
)

from tests.v3.compatibility_suite.util import string_to_int
from pact.v3.pact import AsyncMessageInteraction, MessagePact as Pact

PactInteraction = namedtuple("PactInteraction", ["pact", "interaction"])

TEST_PACT_FILE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'pacts')

@scenario(
    'definition/features/V4/message_consumer.feature',
    'Sets the type for the interaction'
)
def test_sets_the_type_for_the_interaction():
    """Sets the type for the interaction."""


@scenario(
    'definition/features/V4/message_consumer.feature',
    'Supports adding comments'
)
def test_supports_adding_comments():
    """Supports adding comments."""


@pytest.fixture(autouse=True)
def handle_pact_file_directory():
    if not os.path.exists(TEST_PACT_FILE_DIRECTORY):
        os.mkdir(TEST_PACT_FILE_DIRECTORY)
    yield
    os.rmdir(TEST_PACT_FILE_DIRECTORY)

@scenario(
    'definition/features/V4/message_consumer.feature',
    'Supports specifying a key for the interaction'
)
def test_supports_specifying_a_key_for_the_interaction():
    """Supports specifying a key for the interaction."""


@scenario(
    'definition/features/V4/message_consumer.feature',
    'Supports specifying the interaction is pending'
)
def test_supports_specifying_the_interaction_is_pending():
    """Supports specifying the interaction is pending."""


################################################################################
## Given
################################################################################


@given(
    parsers.re(r'a comment "(?P<comment>[^"]+)" is added to the message interaction')
)
def a_comment_is_added_to_the_message_interaction(
    pact_interaction: PactInteraction,
    comment: str
):
    """a comment "{comment}" is added to the message interaction."""
    pact_interaction.interaction.add_text_comment(comment)


@given(parsers.re(r'a key of "(?P<key>[^"]+)" is specified for the message interaction'))
def a_key_is_specified_for_the_http_interaction(
    pact_interaction: PactInteraction,
    key: str,
) -> None:
    """A key is specified for the HTTP interaction."""
    pact_interaction.interaction.set_key(key)


@given(
    'a message interaction is being defined for a consumer test',
    target_fixture='pact_interaction'
)
def a_message_interaction_is_being_defined_for_a_consumer_test():
    """a message integration is being defined for a consumer test."""
    pact = Pact("message_consumer", "message_provider")
    pact.with_specification("V4")
    yield PactInteraction(pact, pact.upon_receiving("a request", "Async"))


@given('the message interaction is marked as pending')
def the_message_interaction_is_marked_as_pending(
    pact_interaction: PactInteraction
):
    """the message interaction is marked as pending."""
    pact_interaction.interaction.set_pending(pending=True)


################################################################################
## When
################################################################################


@when(
    'the Pact file for the test is generated',
    target_fixture='pact_data'
)
def the_pact_file_for_the_test_is_generated(
    pact_interaction: PactInteraction
):
    """the Pact file for the test is generated."""
    pact_interaction.pact.write_file(TEST_PACT_FILE_DIRECTORY, overwrite=True)
    with open(os.path.join(TEST_PACT_FILE_DIRECTORY, 'message_consumer-message_provider.json')) as file:
        yield json.load(file)
    os.remove(os.path.join(TEST_PACT_FILE_DIRECTORY, 'message_consumer-message_provider.json'))


################################################################################
## Then
################################################################################


@then(
    parsers.re(
        r"the (?P<num>[^ ]+) interaction in the Pact file"
        r" will have \"(?P<key>[^\"]+)\" = '(?P<value>[^']+)'"
    ),
    converters={"num": string_to_int},
)
def the_interaction_in_the_pact_file_will_have_a_key_of(
    pact_data: dict[str, Any],
    num: int,
    key: str,
    value: str,
) -> None:
    """The interaction in the Pact file will have a key of value."""
    assert "interactions" in pact_data
    assert len(pact_data["interactions"]) >= num
    interaction = pact_data["interactions"][num - 1]
    assert key in interaction
    value = json.loads(value)
    if isinstance(value, list):
        assert interaction[key] in value
    else:
        assert interaction[key] == value

@then(
    parsers.re(
        r"the (?P<num>[^ ]+) interaction in the Pact file"
        r' will have a type of "(?P<interaction_type>[^"]+)"'
    ),
    converters={"num": string_to_int},
)
def the_interaction_in_the_pact_file_will_container_provider_states(
    pact_data: dict[str, Any],
    num: int,
    interaction_type: str,
) -> None:
    """The interaction in the Pact file will container provider states."""
    assert "interactions" in pact_data
    assert len(pact_data["interactions"]) >= num
    interaction = pact_data["interactions"][num - 1]
    assert interaction["type"] == interaction_type

