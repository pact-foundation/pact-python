"""Basic HTTP consumer feature tests."""

from __future__ import annotations

import json
import logging
from typing import Any, Generator

from pytest_bdd import given, parsers, scenario, then

from pact.v3.pact import HttpInteraction, Pact
from tests.v3.compatibility_suite.util import PactInteractionTuple, string_to_int
from tests.v3.compatibility_suite.util.consumer import (
    the_pact_file_for_the_test_is_generated,
)

logger = logging.getLogger(__name__)

################################################################################
## Scenario
################################################################################


@scenario(
    "definition/features/V4/http_consumer.feature",
    "Sets the type for the interaction",
)
def test_sets_the_type_for_the_interaction() -> None:
    """Sets the type for the interaction."""


@scenario(
    "definition/features/V4/http_consumer.feature",
    "Supports specifying a key for the interaction",
)
def test_supports_specifying_a_key_for_the_interaction() -> None:
    """Supports specifying a key for the interaction."""


@scenario(
    "definition/features/V4/http_consumer.feature",
    "Supports specifying the interaction is pending",
)
def test_supports_specifying_the_interaction_is_pending() -> None:
    """Supports specifying the interaction is pending."""


@scenario(
    "definition/features/V4/http_consumer.feature",
    "Supports adding comments",
)
def test_supports_adding_comments() -> None:
    """Supports adding comments."""


################################################################################
## Given
################################################################################


@given(
    "an HTTP interaction is being defined for a consumer test",
    target_fixture="pact_interaction",
)
def an_http_interaction_is_being_defined_for_a_consumer_test() -> (
    Generator[PactInteractionTuple[HttpInteraction], Any, None]
):
    """An HTTP interaction is being defined for a consumer test."""
    pact = Pact("consumer", "provider")
    pact.with_specification("V4")
    yield PactInteractionTuple(pact, pact.upon_receiving("a request"))


@given(parsers.re(r'a key of "(?P<key>[^"]+)" is specified for the HTTP interaction'))
def a_key_is_specified_for_the_http_interaction(
    pact_interaction: PactInteractionTuple[HttpInteraction],
    key: str,
) -> None:
    """A key is specified for the HTTP interaction."""
    pact_interaction.interaction.set_key(key)


@given("the HTTP interaction is marked as pending")
def the_http_interaction_is_marked_as_pending(
    pact_interaction: PactInteractionTuple[HttpInteraction],
) -> None:
    """The HTTP interaction is marked as pending."""
    pact_interaction.interaction.set_pending(pending=True)


@given(parsers.re(r'a comment "(?P<comment>[^"]+)" is added to the HTTP interaction'))
def a_comment_is_added_to_the_http_interaction(
    pact_interaction: PactInteractionTuple[HttpInteraction],
    comment: str,
) -> None:
    """A comment of "<comment>" is added to the HTTP interaction."""
    pact_interaction.interaction.set_comment("text", [comment])


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
