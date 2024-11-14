"""Basic HTTP consumer feature tests."""

from __future__ import annotations

import logging

from pytest_bdd import given, parsers, scenario

from tests.v3.compatibility_suite.util import parse_horizontal_table
from tests.v3.compatibility_suite.util.consumer import (
    a_response_is_returned,
    request_n_is_made_to_the_mock_server,
    request_n_is_made_to_the_mock_server_with_the_following_changes,
    the_content_type_will_be_set_as,
    the_mismatches_will_contain_a_mismatch_with_path_with_the_error,
    the_mismatches_will_contain_a_mismatch_with_the_error,
    the_mock_server_is_started_with_interaction_n_but_with_the_following_changes,
    the_mock_server_is_started_with_interactions,
    the_mock_server_status_will_be,
    the_mock_server_status_will_be_an_expected_but_not_received_error_for_interaction_n,
    the_mock_server_status_will_be_an_unexpected_request_received_for_interaction_n,
    the_mock_server_status_will_be_an_unexpected_request_received_for_path,
    the_mock_server_status_will_be_mismatches,
    the_mock_server_will_write_out_a_pact_file_for_the_interaction_when_done,
    the_nth_interaction_request_content_type_will_be,
    the_nth_interaction_request_query_parameters_will_be,
    the_nth_interaction_request_will_be_for_method,
    the_nth_interaction_request_will_contain_the_document,
    the_nth_interaction_request_will_contain_the_header,
    the_nth_interaction_will_contain_the_document,
    the_pact_file_will_contain_n_interactions,
    the_pact_test_is_done,
    the_payload_will_contain_the_json_document,
)
from tests.v3.compatibility_suite.util.interaction_definition import (
    InteractionDefinition,
)

logger = logging.getLogger(__name__)

################################################################################
## Scenario
################################################################################


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Supports a regex matcher (negative case)",
)
def test_supports_a_regex_matcher_negative_case() -> None:
    """Supports a regex matcher (negative case)."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Supports a regex matcher (positive case)",
)
def test_supports_a_regex_matcher_positive_case() -> None:
    """Supports a regex matcher (positive case)."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Supports a type matcher (negative case)",
)
def test_supports_a_type_matcher_negative_case() -> None:
    """Supports a type matcher (negative case)."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Supports a type matcher (positive case)",
)
def test_supports_a_type_matcher_positive_case() -> None:
    """Supports a type matcher (positive case)."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Supports matchers for repeated request headers (negative case)",
)
def test_supports_matchers_for_repeated_request_headers_negative_case() -> None:
    """Supports matchers for repeated request headers (negative case)."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Supports matchers for repeated request headers (positive case)",
)
def test_supports_matchers_for_repeated_request_headers_positive_case() -> None:
    """Supports matchers for repeated request headers (positive case)."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Supports matchers for repeated request query parameters (negative case)",
)
def test_supports_matchers_for_repeated_request_query_parameters_negative_case() -> (
    None
):
    """Supports matchers for repeated request query parameters (negative case)."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Supports matchers for repeated request query parameters (positive case)",
)
def test_supports_matchers_for_repeated_request_query_parameters_positive_case() -> (
    None
):
    """Supports matchers for repeated request query parameters (positive case)."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Supports matchers for request bodies",
)
def test_supports_matchers_for_request_bodies() -> None:
    """Supports matchers for request bodies."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Supports matchers for request headers",
)
def test_supports_matchers_for_request_headers() -> None:
    """Supports matchers for request headers."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Supports matchers for request query parameters",
)
def test_supports_matchers_for_request_query_parameters() -> None:
    """Supports matchers for request query parameters."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Type matchers cascade to children (negative case)",
)
def test_type_matchers_cascade_to_children_negative_case() -> None:
    """Type matchers cascade to children (negative case)."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Type matchers cascade to children (positive case)",
)
def test_type_matchers_cascade_to_children_positive_case() -> None:
    """Type matchers cascade to children (positive case)."""


@scenario(
    "definition/features/V2/http_consumer.feature",
    "Supports a matcher for request paths",
)
def test_supports_a_matcher_for_request_paths() -> None:
    """Supports a matcher for request paths."""


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
    - matching rules

    The first row is ignored, as it is assumed to be the column headers. The
    order of the columns is similarly ignored.
    """
    logger.debug("Parsing interaction definitions")

    # Check that the table is well-formed
    definitions = parse_horizontal_table(datatable)
    assert len(definitions[0]) == 7, f"Expected 7 columns, got {len(definitions[0])}"
    assert "No" in definitions[0], "'No' column not found"

    # Parse the table into a more useful format
    interactions: dict[int, InteractionDefinition] = {}
    for row in definitions:
        interactions[int(row["No"])] = InteractionDefinition(**row)  # type: ignore[arg-type]

    return interactions


################################################################################
## When
################################################################################

request_n_is_made_to_the_mock_server()
request_n_is_made_to_the_mock_server_with_the_following_changes()
the_mock_server_is_started_with_interactions("V2")
the_mock_server_is_started_with_interaction_n_but_with_the_following_changes("V2")
the_pact_test_is_done()

################################################################################
## Then
################################################################################

a_response_is_returned()
the_content_type_will_be_set_as()
the_mismatches_will_contain_a_mismatch_with_path_with_the_error()
the_mismatches_will_contain_a_mismatch_with_the_error()
the_mock_server_status_will_be()
the_mock_server_status_will_be_an_expected_but_not_received_error_for_interaction_n()
the_mock_server_status_will_be_an_unexpected_request_received_for_interaction_n()
the_mock_server_status_will_be_an_unexpected_request_received_for_path()
the_mock_server_status_will_be_mismatches()
the_mock_server_will_write_out_a_pact_file_for_the_interaction_when_done()
the_nth_interaction_request_content_type_will_be()
the_nth_interaction_request_query_parameters_will_be()
the_nth_interaction_request_will_be_for_method()
the_nth_interaction_request_will_contain_the_document()
the_nth_interaction_request_will_contain_the_header()
the_nth_interaction_will_contain_the_document()
the_pact_file_will_contain_n_interactions()
the_payload_will_contain_the_json_document()
