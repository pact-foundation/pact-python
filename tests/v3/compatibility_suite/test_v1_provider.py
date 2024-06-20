"""
Basic HTTP provider feature test.
"""

from __future__ import annotations

import logging
import sys

import pytest
from pytest_bdd import given, parsers, scenario

from tests.v3.compatibility_suite.util import (
    InteractionDefinition,
    parse_markdown_table,
)
from tests.v3.compatibility_suite.util.provider import (
    a_failed_verification_result_will_be_published_back,
    a_pact_file_for_interaction_is_to_be_verified,
    a_pact_file_for_interaction_is_to_be_verified_from_a_pact_broker,
    a_pact_file_for_interaction_is_to_be_verified_with_a_provider_state_defined,
    a_provider_is_started_that_returns_the_responses_from_interactions,
    a_provider_is_started_that_returns_the_responses_from_interactions_with_changes,
    a_provider_state_callback_is_configured,
    a_request_filter_is_configured_to_make_the_following_changes,
    a_successful_verification_result_will_be_published_back,
    a_verification_result_will_not_be_published_back,
    a_warning_will_be_displayed_that_there_was_no_callback_configured,
    publishing_of_verification_results_is_enabled,
    reset_broker_var,
    the_provider_state_callback_will_be_called_after_the_verification_is_run,
    the_provider_state_callback_will_be_called_before_the_verification_is_run,
    the_provider_state_callback_will_not_receive_a_setup_call,
    the_provider_state_callback_will_receive_a_setup_call,
    the_request_to_the_provider_will_contain_the_header,
    the_verification_is_run,
    the_verification_results_will_contain_a_error,
    the_verification_will_be_successful,
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
    "definition/features/V1/http_provider.feature",
    "Verifying a simple HTTP request",
)
def test_verifying_a_simple_http_request() -> None:
    """Verifying a simple HTTP request."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying multiple Pact files",
)
def test_verifying_multiple_pact_files() -> None:
    """Verifying multiple Pact files."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Incorrect request is made to provider",
)
def test_incorrect_request_is_made_to_provider() -> None:
    """Incorrect request is made to provider."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@pytest.mark.container()
@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying a simple HTTP request via a Pact broker",
)
def test_verifying_a_simple_http_request_via_a_pact_broker() -> None:
    """Verifying a simple HTTP request via a Pact broker."""
    reset_broker_var.set(True)


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@pytest.mark.container()
@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying a simple HTTP request via a Pact broker with publishing results enabled",
)
def test_verifying_a_simple_http_request_via_a_pact_broker_with_publishing() -> None:
    """Verifying a simple HTTP request via a Pact broker with publishing."""
    reset_broker_var.set(True)


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@pytest.mark.container()
@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying multiple Pact files via a Pact broker",
)
def test_verifying_multiple_pact_files_via_a_pact_broker() -> None:
    """Verifying multiple Pact files via a Pact broker."""
    reset_broker_var.set(True)


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@pytest.mark.container()
@scenario(
    "definition/features/V1/http_provider.feature",
    "Incorrect request is made to provider via a Pact broker",
)
def test_incorrect_request_is_made_to_provider_via_a_pact_broker() -> None:
    """Incorrect request is made to provider via a Pact broker."""
    reset_broker_var.set(True)


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying an interaction with a defined provider state",
)
def test_verifying_an_interaction_with_a_defined_provider_state() -> None:
    """Verifying an interaction with a defined provider state."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying an interaction with no defined provider state",
)
def test_verifying_an_interaction_with_no_defined_provider_state() -> None:
    """Verifying an interaction with no defined provider state."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying an interaction where the provider state callback fails",
)
def test_verifying_an_interaction_where_the_provider_state_callback_fails() -> None:
    """Verifying an interaction where the provider state callback fails."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying an interaction where a provider state callback is not configured",
)
def test_verifying_an_interaction_where_no_provider_state_callback_configured() -> None:
    """Verifying an interaction where a provider state callback is not configured."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying a HTTP request with a request filter configured",
)
def test_verifying_a_http_request_with_a_request_filter_configured() -> None:
    """Verifying a HTTP request with a request filter configured."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifies the response status code",
)
def test_verifies_the_response_status_code() -> None:
    """Verifies the response status code."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifies the response headers",
)
def test_verifies_the_response_headers() -> None:
    """Verifies the response headers."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with plain text body (positive case)",
)
def test_response_with_plain_text_body_positive_case() -> None:
    """Response with plain text body (positive case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with plain text body (negative case)",
)
def test_response_with_plain_text_body_negative_case() -> None:
    """Response with plain text body (negative case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with JSON body (positive case)",
)
def test_response_with_json_body_positive_case() -> None:
    """Response with JSON body (positive case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with JSON body (negative case)",
)
def test_response_with_json_body_negative_case() -> None:
    """Response with JSON body (negative case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with XML body (positive case)",
)
def test_response_with_xml_body_positive_case() -> None:
    """Response with XML body (positive case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with XML body (negative case)",
)
def test_response_with_xml_body_negative_case() -> None:
    """Response with XML body (negative case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with binary body (positive case)",
)
def test_response_with_binary_body_positive_case() -> None:
    """Response with binary body (positive case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with binary body (negative case)",
)
def test_response_with_binary_body_negative_case() -> None:
    """Response with binary body (negative case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with form post body (positive case)",
)
def test_response_with_form_post_body_positive_case() -> None:
    """Response with form post body (positive case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with form post body (negative case)",
)
def test_response_with_form_post_body_negative_case() -> None:
    """Response with form post body (negative case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with multipart body (positive case)",
)
def test_response_with_multipart_body_positive_case() -> None:
    """Response with multipart body (positive case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with multipart body (negative case)",
)
def test_response_with_multipart_body_negative_case() -> None:
    """Response with multipart body (negative case)."""


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
    assert len(content[0]) == 10, f"Expected 10 columns, got {len(content[0])}"
    assert "No" in content[0], "'No' column not found"

    # Parse the table into a more useful format
    interactions: dict[int, InteractionDefinition] = {}
    for row in content:
        interactions[int(row["No"])] = InteractionDefinition(**row)
    return interactions


a_pact_file_for_interaction_is_to_be_verified("V1")
a_pact_file_for_interaction_is_to_be_verified_from_a_pact_broker("V1")
a_pact_file_for_interaction_is_to_be_verified_with_a_provider_state_defined("V1")
a_provider_is_started_that_returns_the_responses_from_interactions()
a_provider_is_started_that_returns_the_responses_from_interactions_with_changes()
a_provider_state_callback_is_configured()
a_request_filter_is_configured_to_make_the_following_changes()
publishing_of_verification_results_is_enabled()


################################################################################
## When
################################################################################


the_verification_is_run()


################################################################################
## Then
################################################################################


a_failed_verification_result_will_be_published_back()
a_successful_verification_result_will_be_published_back()
a_verification_result_will_not_be_published_back()
a_warning_will_be_displayed_that_there_was_no_callback_configured()
the_provider_state_callback_will_be_called_after_the_verification_is_run()
the_provider_state_callback_will_be_called_before_the_verification_is_run()
the_provider_state_callback_will_not_receive_a_setup_call()
the_provider_state_callback_will_receive_a_setup_call()
the_request_to_the_provider_will_contain_the_header()
the_verification_results_will_contain_a_error()
the_verification_will_be_successful()
