"""
Basic HTTP provider feature test.
"""

from __future__ import annotations

import logging

from pytest_bdd import given, parsers, scenario

from tests.v3.compatibility_suite.util import (
    InteractionDefinition,
    parse_markdown_table,
)
from tests.v3.compatibility_suite.util.provider import (
    a_pact_file_for_interaction_is_to_be_verified,
    a_provider_is_started_that_returns_the_responses_from_interactions_with_changes,
    the_verification_is_run,
    the_verification_results_will_contain_a_error,
    the_verification_will_be_successful,
)

logger = logging.getLogger(__name__)


################################################################################
## Scenario
################################################################################


@scenario(
    "definition/features/V2/http_provider.feature",
    "Supports matching rules for the response headers (positive case)",
)
def test_supports_matching_rules_for_the_response_headers_positive_case() -> None:
    """
    Supports matching rules for the response headers (positive case).
    """


@scenario(
    "definition/features/V2/http_provider.feature",
    "Supports matching rules for the response headers (negative case)",
)
def test_supports_matching_rules_for_the_response_headers_negative_case() -> None:
    """
    Supports matching rules for the response headers (negative case).
    """


@scenario(
    "definition/features/V2/http_provider.feature",
    "Verifies the response body (positive case)",
)
def test_verifies_the_response_body_positive_case() -> None:
    """
    Verifies the response body (positive case).
    """


@scenario(
    "definition/features/V2/http_provider.feature",
    "Verifies the response body (negative case)",
)
def test_verifies_the_response_body_negative_case() -> None:
    """
    Verifies the response body (negative case).
    """


################################################################################
## Given
################################################################################


@given(
    parsers.parse("the following HTTP interactions have been defined:\n{content}"),
    target_fixture="interaction_definitions",
    converters={"content": parse_markdown_table},
)
def the_following_http_interactions_have_been_defined(
    content: list[dict[str, str]],
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
    assert len(content[0]) == 8, f"Expected 8 columns, got {len(content[0])}"
    assert "No" in content[0], "'No' column not found"

    # Parse the table into a more useful format
    interactions: dict[int, InteractionDefinition] = {}
    for row in content:
        interactions[int(row["No"])] = InteractionDefinition(**row)
    return interactions


a_pact_file_for_interaction_is_to_be_verified("V2")
a_provider_is_started_that_returns_the_responses_from_interactions_with_changes()

################################################################################
## When
################################################################################


the_verification_is_run()


################################################################################
## Then
################################################################################


the_verification_results_will_contain_a_error()
the_verification_will_be_successful()
