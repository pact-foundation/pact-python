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
    "definition/features/V1/http_consumer.feature",
    "When all requests are made to the mock server",
)
def test_when_all_requests_are_made_to_the_mock_server() -> None:
    """
    When all requests are made to the mock server.
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "When not all requests are made to the mock server",
)
def test_when_not_all_requests_are_made_to_the_mock_server() -> None:
    """
    When not all requests are made to the mock server.
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "When an unexpected request is made to the mock server",
)
def test_when_an_unexpected_request_is_made_to_the_mock_server() -> None:
    """
    When an unexpected request is made to the mock server.
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with query parameters",
)
def test_request_with_query_parameters() -> None:
    """
    Request with query parameters.
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with invalid query parameters",
)
def test_request_with_invalid_query_parameters() -> None:
    """
    Request with invalid query parameters.
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with invalid path",
)
def test_request_with_invalid_path() -> None:
    """
    Request with invalid path.
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with invalid method",
)
def test_request_with_invalid_method() -> None:
    """
    Request with invalid method.
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with headers",
)
def test_request_with_headers() -> None:
    """
    Request with headers.
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with invalid headers",
)
def test_request_with_invalid_headers() -> None:
    """
    Request with invalid headers.
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with body",
)
def test_request_with_body() -> None:
    """
    Request with body.
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with invalid body",
)
def test_request_with_invalid_body() -> None:
    """
    Request with invalid body.
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with the incorrect type of body contents",
)
def test_request_with_the_incorrect_type_of_body_contents() -> None:
    """
    Request with the incorrect type of body contents.
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with plain text body (positive case)",
)
def test_request_with_plain_text_body_positive_case() -> None:
    """
    Request with plain text body (positive case).
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with plain text body (negative case)",
)
def test_request_with_plain_text_body_negative_case() -> None:
    """
    Request with plain text body (negative case).
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with JSON body (positive case)",
)
def test_request_with_json_body_positive_case() -> None:
    """
    Request with JSON body (positive case).
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with JSON body (negative case)",
)
def test_request_with_json_body_negative_case() -> None:
    """
    Request with JSON body (negative case).
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with XML body (positive case)",
)
def test_request_with_xml_body_positive_case() -> None:
    """
    Request with XML body (positive case).
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with XML body (negative case)",
)
def test_request_with_xml_body_negative_case() -> None:
    """
    Request with XML body (negative case).
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with a binary body (positive case)",
)
def test_request_with_a_binary_body_positive_case() -> None:
    """
    Request with a binary body (positive case).
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with a binary body (negative case)",
)
def test_request_with_a_binary_body_negative_case() -> None:
    """
    Request with a binary body (negative case).
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with a form post body (positive case)",
)
def test_request_with_a_form_post_body_positive_case() -> None:
    """
    Request with a form post body (positive case).
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with a form post body (negative case)",
)
def test_request_with_a_form_post_body_negative_case() -> None:
    """
    Request with a form post body (negative case).
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with a multipart body (positive case)",
)
def test_request_with_a_multipart_body_positive_case() -> None:
    """
    Request with a multipart body (positive case).
    """


@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with a multipart body (negative case)",
)
def test_request_with_a_multipart_body_negative_case() -> None:
    """
    Request with a multipart body (negative case).
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
    - response content
    - response body

    The first row is ignored, as it is assumed to be the column headers. The
    order of the columns is similarly ignored.
    """
    logger.info("Parsing interaction definitions")

    # Check that the table is well-formed
    definitions = parse_horizontal_table(datatable)
    assert len(definitions[0]) == 9, f"Expected 9 columns, got {len(definitions[0])}"
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
the_mock_server_is_started_with_interactions("V1")
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
