"""
Basic HTTP provider feature test.
"""

from __future__ import annotations

import logging
import sys

import pytest
from pytest_bdd import scenario

from tests.v3.compatibility_suite.util.provider import (
    a_pact_file_for_message_is_to_be_verified,
    a_pact_file_for_message_is_to_be_verified_with_comments,
    a_provider_is_started_that_can_generate_the_message,
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
    "definition/features/V4/message_provider.feature",
    "Verifying a pending message interaction",
)
def test_verifying_a_pending_message_interaction() -> None:
    """
    Verifying a pending message interaction.
    """


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V4/message_provider.feature",
    "Verifying a message interaction with comments",
)
def test_verifying_a_message_interaction_with_comments() -> None:
    """
    Verifying a message interaction with comments.
    """


################################################################################
## Given
################################################################################


a_provider_is_started_that_can_generate_the_message()
a_pact_file_for_message_is_to_be_verified("V4")
a_pact_file_for_message_is_to_be_verified_with_comments("V4")


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
