"""Message provider feature tests."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pytest_bdd import (
    given,
    parsers,
    scenario,
    then,
)

from pact.v3 import Pact
from tests.v3.compatibility_suite.util import (
    InteractionDefinition,
    parse_markdown_table,
)
from tests.v3.compatibility_suite.util.provider import (
    VERIFIER_ERROR_MAP,
    a_provider_is_started_that_can_generate_the_message,
    the_verification_is_run_with_start_context,
    the_verification_will_be_successful,
)

if TYPE_CHECKING:
    from pathlib import Path

    from pact.v3.verifier import Verifier

@scenario(
    "definition/features/V4/message_provider.feature",
    "Verifying a message interaction with comments"
)
def test_verifying_a_message_interaction_with_comments() -> None:
    """Verifying a message interaction with comments."""


@scenario(
    "definition/features/V4/message_provider.feature",
    "Verifying a pending message interaction"
)
def test_verifying_a_pending_message_interaction() -> None:
    """Verifying a pending message interaction."""


################################################################################
## Given
################################################################################


@given(
    parsers.re(
        r'a Pact file for "(?P<name>[^"]+)":"(?P<fixture>[^"]+)" is to be verified '
        r'with the following comments:\n(?P<comments>.+)',
        re.DOTALL,
    ),
    converters={"comments": parse_markdown_table}
)
def a_pact_file_is_to_be_verified_with_comments(
    verifier: Verifier,
    temp_dir: Path,
    name: str,
    fixture: str,
    comments: list[dict[str, str]],
) -> None:
    """A Pact file is to be verified with comments."""
    pact = Pact("consumer", "provider")
    pact.with_specification("V4")
    interaction_definition = InteractionDefinition(
        method="POST",
        path=f"/{name}",
        is_async_message=True,
        response_body=fixture,
    )
    for comment in comments:
        comment_type = comment.get("type", "text")
        if comment_type == "text":
            interaction_definition.text_comments.append(comment.get("comment"))
        elif comment_type == "testname":
            interaction_definition.test_name = comment.get("comment")
    interaction_definition.add_to_pact(pact, name, "Async")
    (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
    pact.write_file(temp_dir / "pacts")
    verifier.add_source(temp_dir / "pacts")


@given(
    parsers.parse(
        'a Pact file for "{name}":"{fixture}" is to be verified, but is marked pending'
    )
)
def a_pact_file_is_to_be_verified_but_is_marked_pending(
    verifier: Verifier,
    temp_dir: Path,
    name: str,
    fixture: str
) -> None:
    """A Pact file is to be verified, but is marked pending."""
    pact = Pact("consumer", "provider")
    pact.with_specification("V4")
    interaction_definition = InteractionDefinition(
        method="POST",
        path=f"/{name}",
        is_async_message=True,
        response_body=fixture,
        is_pending=True,
    )
    interaction_definition.add_to_pact(pact, name, "Async")
    (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
    pact.write_file(temp_dir / "pacts")
    verifier.add_source(temp_dir / "pacts")

a_provider_is_started_that_can_generate_the_message()


################################################################################
## When
################################################################################


the_verification_is_run_with_start_context()


################################################################################
## Then
################################################################################


@then(
    parsers.parse('the "{test_name}" will displayed as the original test name')
)
def the_test_name_will_displayed_as_the_original_test_name(
    verifier_result: list[any, any],
    test_name: str
) -> None:
    """The expected test name will displayed as the original test name."""
    verifier_output: str = verifier_result[0].output
    assert f"Test Name: {test_name}" in verifier_output()


@then(
    parsers.parse('the comment "{comment}" will have been printed to the console')
)
def the_comment_will_have_been_printed_to_the_console(
    verifier_result: list[any, any],
    comment: str
) -> None:
    """The expected comment will have been printed to the console."""
    verifier_output: str = verifier_result[0].output
    assert comment in verifier_output()


the_verification_will_be_successful()


@then(
    parsers.parse('there will be a pending "{pending_error}" error')
)
def there_will_be_a_pending_error(
    verifier_result: list[any, any],
    pending_error: str
) -> None:
    """There will be a pending  error."""
    expected_mismatch_type = VERIFIER_ERROR_MAP.get(pending_error)
    mismatch_types = [
        mismatch["type"]
        for error in verifier_result[0].results["pendingErrors"]
        for mismatch in error["mismatch"]["mismatches"]
    ]
    assert expected_mismatch_type in mismatch_types

