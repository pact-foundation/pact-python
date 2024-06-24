"""Message consumer feature tests."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pytest_bdd import (
    given,
    parsers,
    scenario,
    then,
)

from tests.v3.compatibility_suite.util import PactInteractionTuple, string_to_int
from tests.v3.compatibility_suite.util.consumer import (
    a_message_integration_is_being_defined_for_a_consumer_test,
    the_pact_file_for_the_test_is_generated,
)

if TYPE_CHECKING:
    from pact.v3.pact import AsyncMessageInteraction


@scenario(
    "definition/features/V4/message_consumer.feature",
    "Sets the type for the interaction",
)
def test_sets_the_type_for_the_interaction() -> None:
    """Sets the type for the interaction."""


@scenario(
    "definition/features/V4/message_consumer.feature",
    "Supports specifying a key for the interaction",
)
def test_supports_specifying_a_key_for_the_interaction() -> None:
    """Supports specifying a key for the interaction."""


@scenario(
    "definition/features/V4/message_consumer.feature",
    "Supports specifying the interaction is pending",
)
def test_supports_specifying_the_interaction_is_pending() -> None:
    """Supports specifying the interaction is pending."""


@scenario(
    "definition/features/V4/message_consumer.feature",
    "Supports adding comments",
)
def test_supports_adding_comments() -> None:
    """Supports adding comments."""


################################################################################
## Given
################################################################################

a_message_integration_is_being_defined_for_a_consumer_test("V4")


@given(
    parsers.re(r'a comment "(?P<comment>[^"]+)" is added to the message interaction')
)
def a_comment_is_added_to_the_message_interaction(
    pact_interaction: PactInteractionTuple[AsyncMessageInteraction],
    comment: str,
) -> None:
    """A comment "{comment}" is added to the message interaction."""
    pact_interaction.interaction.add_text_comment(comment)


@given(
    parsers.re(r'a key of "(?P<key>[^"]+)" is specified for the message interaction')
)
def a_key_is_specified_for_the_message_interaction(
    pact_interaction: PactInteractionTuple[AsyncMessageInteraction],
    key: str,
) -> None:
    """A key is specified for the HTTP interaction."""
    pact_interaction.interaction.set_key(key)


@given("the message interaction is marked as pending")
def the_message_interaction_is_marked_as_pending(
    pact_interaction: PactInteractionTuple[AsyncMessageInteraction],
) -> None:
    """The message interaction is marked as pending."""
    pact_interaction.interaction.set_pending(pending=True)


################################################################################
## When
################################################################################


the_pact_file_for_the_test_is_generated()


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
