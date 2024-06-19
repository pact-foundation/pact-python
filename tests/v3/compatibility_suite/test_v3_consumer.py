"""Basic HTTP consumer feature tests."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Generator

from pytest_bdd import given, parsers, scenario, then

from pact.v3.pact import HttpInteraction, Pact
from tests.v3.compatibility_suite.util import PactInteractionTuple, parse_markdown_table
from tests.v3.compatibility_suite.util.consumer import (
    the_pact_file_for_the_test_is_generated,
)

logger = logging.getLogger(__name__)

################################################################################
## Scenario
################################################################################


@scenario(
    "definition/features/V3/http_consumer.feature",
    "Supports specifying multiple provider states",
)
def test_supports_specifying_multiple_provider_states() -> None:
    """Supports specifying multiple provider states."""


@scenario(
    "definition/features/V3/http_consumer.feature",
    "Supports data for provider states",
)
def test_supports_data_for_provider_states() -> None:
    """Supports data for provider states."""


################################################################################
## Given
################################################################################


@given(
    "an integration is being defined for a consumer test",
    target_fixture="pact_interaction",
)
def an_integration_is_being_defined_for_a_consumer_test() -> (
    Generator[PactInteractionTuple[HttpInteraction], Any, None]
):
    """An integration is being defined for a consumer test."""
    pact = Pact("consumer", "provider")
    pact.with_specification("V3")
    yield PactInteractionTuple(pact, pact.upon_receiving("a request"))


@given(parsers.re(r'a provider state "(?P<state>[^"]+)" is specified'))
def a_provider_state_is_specified(
    pact_interaction: PactInteractionTuple[HttpInteraction],
    state: str,
) -> None:
    """A provider state is specified."""
    pact_interaction.interaction.given(state)


@given(
    parsers.re(
        r'a provider state "(?P<state>[^"]+)" is specified'
        r" with the following data:\n(?P<table>.+)",
        re.DOTALL,
    ),
    converters={"table": parse_markdown_table},
)
def a_provider_state_is_specified_with_the_following_data(
    pact_interaction: PactInteractionTuple[HttpInteraction],
    state: str,
    table: list[dict[str, Any]],
) -> None:
    """A provider state is specified."""
    for row in table:
        for key, value in row.items():
            if value.startswith('"') and value.endswith('"'):
                row[key] = value[1:-1]
        for key, value in row.items():
            if value == "true":
                row[key] = True
            elif value == "false":
                row[key] = False
            elif value.isdigit():
                row[key] = int(value)
            elif value.replace(".", "", 1).isdigit():
                row[key] = float(value)

    pact_interaction.interaction.given(state, parameters=table[0])


################################################################################
## When
################################################################################


the_pact_file_for_the_test_is_generated()


################################################################################
## Then
################################################################################


@then(
    parsers.re(
        r"the interaction in the Pact file will contain"
        r" (?P<num>\d+) provider states?"
    ),
    converters={"num": int},
)
def the_interaction_in_the_pact_file_will_container_provider_states(
    num: int,
    pact_data: dict[str, Any],
) -> None:
    """The interaction in the Pact file will container provider states."""
    assert "interactions" in pact_data
    assert len(pact_data["interactions"]) == 1
    assert "providerStates" in pact_data["interactions"][0]
    assert len(pact_data["interactions"][0]["providerStates"]) == num


@then(
    parsers.re(
        r"the interaction in the Pact file will contain"
        r' provider state "(?P<state>[^"]+)"'
    ),
)
def the_interaction_in_the_pact_file_will_container_provider_state(
    state: str,
    pact_data: dict[str, Any],
) -> None:
    """The interaction in the Pact file will container provider state."""
    assert "interactions" in pact_data
    assert len(pact_data["interactions"]) == 1
    assert "providerStates" in pact_data["interactions"][0]

    assert any(
        status["name"] == state
        for status in pact_data["interactions"][0]["providerStates"]
    )


@then(
    parsers.re(
        r'the provider state "(?P<state>[^"]+)" in the Pact file'
        r" will contain the following parameters:\n(?P<table>.+)",
        re.DOTALL,
    ),
    converters={"table": parse_markdown_table},
)
def the_provider_state_in_the_pact_file_will_contain_the_following_parameters(
    state: str,
    table: list[dict[str, Any]],
    pact_data: dict[str, Any],
) -> None:
    """The provider state in the Pact file will contain the following parameters."""
    assert "interactions" in pact_data
    assert len(pact_data["interactions"]) == 1
    assert "providerStates" in pact_data["interactions"][0]
    parameters: dict[str, Any] = json.loads(table[0]["parameters"])

    provider_state = next(
        status
        for status in pact_data["interactions"][0]["providerStates"]
        if status["name"] == state
    )
    assert provider_state["params"] == parameters
