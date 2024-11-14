"""
Basic HTTP provider feature test.
"""

from __future__ import annotations

import logging
import sys

import pytest
from pytest_bdd import given, parsers, scenario

from tests.v3.compatibility_suite.util import parse_horizontal_table
from tests.v3.compatibility_suite.util.interaction_definition import (
    InteractionDefinition,
)
from tests.v3.compatibility_suite.util.provider import (
    a_pact_file_for_interaction_is_to_be_verified_with_a_provider_states_defined,
    a_provider_is_started_that_returns_the_responses_from_interactions,
    a_provider_state_callback_is_configured,
    the_provider_state_callback_will_be_called_after_the_verification_is_run,
    the_provider_state_callback_will_be_called_before_the_verification_is_run,
    the_provider_state_callback_will_receive_a_setup_call,
    the_provider_state_callback_will_receive_a_setup_call_with_parameters,
    the_verification_is_run,
)

logger = logging.getLogger(__name__)


################################################################################
## Scenario
################################################################################


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/http_provider.feature",
    "Verifying an interaction with multiple defined provider states",
)
def test_verifying_an_interaction_with_multiple_defined_provider_states() -> None:
    """
    Verifying an interaction with multiple defined provider states.
    """


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/http_provider.feature",
    "Verifying an interaction with a provider state with parameters",
)
def test_verifying_an_interaction_with_a_provider_state_with_parameters() -> None:
    """
    Verifying an interaction with a provider state with parameters.
    """


################################################################################
## Given
################################################################################


@given(
    parsers.parse("the following HTTP interactions have been defined:"),
    target_fixture="interaction_definitions",
)
def the_following_http_interactions_have_been_defined(
    datatable: list[list[str]],
) -> dict[int, InteractionDefinition]:
    """
    Parse the HTTP interactions table into a dictionary.

    The table columns are expected to be:

    - No
    - method
    - path
    - response
    - response headers
    - response content
    - response body
    - response matching rules

    The first row is ignored, as it is assumed to be the column headers. The
    order of the columns is similarly ignored.
    """
    logger.debug("Parsing interaction definitions")

    # Check that the table is well-formed
    definitions = parse_horizontal_table(datatable)
    assert len(definitions[0]) == 8, f"Expected 8 columns, got {len(definitions[0])}"
    assert "No" in definitions[0], "'No' column not found"

    # Parse the table into a more useful format
    interactions: dict[int, InteractionDefinition] = {}
    for row in definitions:
        interactions[int(row["No"])] = InteractionDefinition(**row)  # type: ignore[arg-type]
    return interactions


a_pact_file_for_interaction_is_to_be_verified_with_a_provider_states_defined("V3")
a_provider_is_started_that_returns_the_responses_from_interactions()
a_provider_state_callback_is_configured()

################################################################################
## When
################################################################################


the_verification_is_run()


################################################################################
## Then
################################################################################


the_provider_state_callback_will_be_called_after_the_verification_is_run()
the_provider_state_callback_will_be_called_before_the_verification_is_run()
the_provider_state_callback_will_receive_a_setup_call()
the_provider_state_callback_will_receive_a_setup_call_with_parameters()
