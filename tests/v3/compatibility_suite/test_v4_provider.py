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
    a_pact_file_for_interaction_is_to_be_verified,
    a_pact_file_for_interaction_is_to_be_verified_with_comments,
    a_provider_is_started_that_returns_the_responses_from_interactions,
    a_provider_is_started_that_returns_the_responses_from_interactions_with_changes,
    the_comment_will_have_been_printed_to_the_console,
    the_name_of_the_test_will_be_displayed_as_the_original_test_name,
    the_verification_is_run,
    the_verification_results_will_contain_a_error,
    the_verification_will_be_successful,
    there_will_be_a_pending_error,
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
    "definition/features/V4/http_provider.feature",
    "Verifying a pending HTTP interaction",
)
def test_verifying_a_pending_http_interaction() -> None:
    """
    Verifying a pending HTTP interaction.
    """


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V4/http_provider.feature",
    "Verifying a HTTP interaction with comments",
)
def test_verifying_a_http_interaction_with_comments() -> None:
    """
    Verifying a HTTP interaction with comments.
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
    - query
    - headers
    - body
    - response
    - response headers
    - response content
    - response body

    The first row is ignored, as it is assumed to be the column headers. The
    order of the columns is similarly ignored.
    """
    logger.debug("Parsing interaction definitions")

    # Check that the table is well-formed
    definitions = parse_horizontal_table(datatable)
    assert len(definitions[0]) == 10, f"Expected 10 columns, got {len(definitions[0])}"
    assert "No" in definitions[0], "'No' column not found"

    # Parse the table into a more useful format
    interactions: dict[int, InteractionDefinition] = {}
    for row in definitions:
        interactions[int(row["No"])] = InteractionDefinition(**row)  # type: ignore[arg-type]
    return interactions


a_pact_file_for_interaction_is_to_be_verified("V4")
a_pact_file_for_interaction_is_to_be_verified_with_comments("V4")
a_provider_is_started_that_returns_the_responses_from_interactions()
a_provider_is_started_that_returns_the_responses_from_interactions_with_changes()

################################################################################
## When
################################################################################


the_verification_is_run()


################################################################################
## Then
################################################################################


the_comment_will_have_been_printed_to_the_console()
the_name_of_the_test_will_be_displayed_as_the_original_test_name()
the_verification_results_will_contain_a_error()
the_verification_will_be_successful()
there_will_be_a_pending_error()
