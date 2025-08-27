"""V3 matching rules tests."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs

import pytest
import requests
from pytest_bdd import (
    given,
    parsers,
    scenario,
    then,
    when,
)

from pact.pact import Pact
from tests.compatibility_suite.util import (
    FIXTURES_ROOT,
    parse_horizontal_table,
)
from tests.compatibility_suite.util.interaction_definition import (
    InteractionDefinition,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from pact.error import Mismatch

TEST_PACT_FILE_DIRECTORY = Path(Path(__file__).parent / "pacts")
EXT_TO_CONTENT_TYPE = {
    "jpg": "image/jpeg",
    "pdf": "application/pdf",
    "json": "application/json",
}

logger = logging.getLogger(__name__)


@pytest.fixture
def pact() -> Pact:
    return Pact(
        "v3-matching-rules-consumer",
        "v3-matching-rules-provider",
    ).with_specification("V3")


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a Boolean matcher (negative case)",
)
def test_supports_a_boolean_matcher_negative_case() -> None:
    """Supports a Boolean matcher (negative case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a Boolean matcher (positive case)",
)
def test_supports_a_boolean_matcher_positive_case() -> None:
    """Supports a Boolean matcher (positive case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a ContentType matcher (negative case)",
)
def test_supports_a_contenttype_matcher_negative_case() -> None:
    """Supports a ContentType matcher (negative case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a ContentType matcher (positive case)",
)
def test_supports_a_contenttype_matcher_positive_case() -> None:
    """Supports a ContentType matcher (positive case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a Date and Time matcher (negative case)",
)
def test_supports_a_date_and_time_matcher_negative_case() -> None:
    """Supports a Date and Time matcher (negative case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a Date and Time matcher (positive case)",
)
def test_supports_a_date_and_time_matcher_positive_case() -> None:
    """Supports a Date and Time matcher (positive case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a Values matcher (negative case, final type is wrong)",
)
def test_supports_a_values_matcher_negative_case_final_type_is_wrong() -> None:
    """Supports a Values matcher (negative case, final type is wrong)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a Values matcher (positive case, ignores missing and additional keys)",
)
def test_values_matcher_positive_case_missing_and_additional_keys() -> None:
    """Supports a Values matcher (ignores missing and additional keys)."""


@pytest.mark.skip(
    reason="Waiting on an upstream change in FFI and/or Compatibility Suite"
)
@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a decimal type matcher "
    "where it is acceptable to coerce values from string form",
)
def test_decimal_matcher_coerce_string_form() -> None:
    """Supports a decimal type matcher string form."""


@pytest.mark.skip(
    reason="Waiting on an upstream change in FFI and/or Compatibility Suite"
)
@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a decimal type matcher, "
    "must have significant digits after the decimal point (negative case)",
)
def test_decimal_matcher_significant_digits_negative() -> None:
    """Supports a decimal type matcher with decimal digits (negative case)."""


@pytest.mark.skip(
    reason="Waiting on an upstream change in FFI and/or Compatibility Suite"
)
@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a integer type matcher, "
    "no digits after the decimal point (negative case)",
)
def test_integer_matcher_no_decimal_digits_negative() -> None:
    """Tests integer matcher with no decimal digits (negative case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a minmax type matcher (negative case)",
)
def test_supports_a_minmax_type_matcher_negative_case() -> None:
    """Supports a minmax type matcher (negative case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a minmax type matcher (positive case)",
)
def test_supports_a_minmax_type_matcher_positive_case() -> None:
    """Supports a minmax type matcher (positive case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a null matcher (positive case)",
)
def test_supports_a_null_matcher_positive_case() -> None:
    """Supports a null matcher (positive case)."""


@pytest.mark.skip(
    reason="Waiting on an upstream change in FFI and/or Compatibility Suite"
)
@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a number type matcher (negative case)",
)
def test_supports_a_number_type_matcher_negative_case() -> None:
    """Supports a number type matcher (negative case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a number type matcher (positive case)",
)
def test_supports_a_number_type_matcher_positive_case() -> None:
    """Supports a number type matcher (positive case)."""


@pytest.mark.skip(
    reason="Waiting on an upstream change in FFI and/or Compatibility Suite"
)
@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports a number type matcher "
    "where it is acceptable to coerce values from string form",
)
def test_number_type_matcher_coerce_string_form() -> None:
    """Tests number type matcher coerce string form."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports an decimal type matcher, "
    "must have significant digits after the decimal point (positive case)",
)
def test_decimal_matcher_significant_digits_positive() -> None:
    """Tests decimal matcher with significant digits (positive case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports an equality matcher to reset cascading rules",
)
def test_supports_an_equality_matcher_to_reset_cascading_rules() -> None:
    """Supports an equality matcher to reset cascading rules."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports an include matcher (negative case)",
)
def test_supports_an_include_matcher_negative_case() -> None:
    """Supports an include matcher (negative case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports an include matcher (positive case)",
)
def test_supports_an_include_matcher_positive_case() -> None:
    """Supports an include matcher (positive case)."""


@pytest.mark.skip(
    reason="Waiting on an upstream change in FFI and/or Compatibility Suite"
)
@scenario(
    "definition/features/V3/matching_rules.feature",
    (
        "Supports an integer type matcher "
        "where it is acceptable to coerce values from string form"
    ),
)
def test_integer_type_matcher_coerce_string_form() -> None:
    """Supports an integer type matcher coerce string form."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports an integer type matcher, "
    "no digits after the decimal point (positive case)",
)
def test_integer_type_matcher_no_decimal_digits_positive() -> None:
    """Tests integer type matcher no decimal digits (positive case)."""


@scenario(
    "definition/features/V3/matching_rules.feature",
    "Supports an null matcher (negative case)",
)
def test_supports_an_null_matcher_negative_case() -> None:
    """Supports an null matcher (negative case)."""


################################################################################
## Given
################################################################################


@given(
    parsers.re(
        r"^("
        r"a request is received with the following:|"
        r"the following requests are received:"
        r")$"
    ),
    target_fixture="request_calls",
)
def a_request_is_received_with_the_following(
    datatable: list[list[str]],
) -> list[Callable[[str], requests.Response]]:
    """A request is received with the following:."""
    data = parse_horizontal_table(datatable)
    assert len(data) > 0, "Expected at least one row in the table"

    body: Any
    request_calls: list[Callable[[str], requests.Response]] = []
    for row in data:
        content_type = row.pop("content type", None)

        if body := row.pop("body", None):
            if body.startswith("JSON: "):
                content_type = content_type or "application/json"
                body = body.replace("JSON: ", "")
            elif body.startswith("file: "):
                content_type = (
                    content_type or EXT_TO_CONTENT_TYPE[body.rsplit(".")[-1].lower()]
                )
                body = (FIXTURES_ROOT / body.replace("file: ", "")).read_bytes()

        query: dict[str, list[str]] = (
            parse_qs(s) if (s := row.pop("query", None)) else {}
        )
        headers = (
            dict(s.split(": ") for s in hs.strip("'").split("; "))
            if (hs := row.pop("headers", None))
            else {}
        )

        # Ignore description field
        row.pop("desc", None)

        if row:
            msg = f"Unexpected extra columns in table: {row!r}"
            raise ValueError(msg)

        logger.debug(
            "Configured POST request: %r",
            {
                "body": body,
                "content_type": content_type,
                "query": query,
                "headers": headers,
            },
        )

        request_calls.append(
            lambda url,  # type: ignore[misc]
            body=body,
            content_type=content_type,
            headers=headers,
            query=query: requests.post(
                url,
                body,
                timeout=2,
                headers={
                    **({"Content-Type": content_type} if content_type else {}),
                    **(headers),
                },
                params=query,
            )
        )

    return request_calls


@given("an expected request configured with the following:")
def an_expected_request_configured_with(
    pact: Pact,
    datatable: list[list[str]],
) -> None:
    """An expected request configured with."""
    data = parse_horizontal_table(datatable)
    assert len(data) == 1, "Expected exactly one row in the table"

    interaction = InteractionDefinition(
        method="POST",
        path="/",
        **data[0],  # type: ignore[arg-type]
    )
    interaction.add_to_pact(pact, "a matching rules request")


################################################################################
## When
################################################################################


@when(
    parsers.re("the (request is|requests are) compared to the expected one"),
    target_fixture="mismatches",
)
def the_request_is_compared_to_the_expected_one(
    pact: Pact,
    request_calls: list[Callable[[str], requests.Response]],
) -> list[Mismatch]:
    """The request is compared to the expected one."""
    with pact.serve(raises=False) as srv:
        for f in request_calls:
            f(str(srv.url))

    return srv.mismatches


################################################################################
## Then
################################################################################


@then(
    parsers.re(r"the comparison should (?P<negated>(NOT )?)be OK"),
    converters={"negated": lambda s: s == "NOT "},
)
def the_comparison_should_be_ok(
    negated: bool,  # noqa: FBT001
    mismatches: list[Mismatch],
) -> None:
    """The comparison should be OK."""
    if negated:
        assert len(mismatches) > 0
    else:
        assert len(mismatches) == 0


@then(
    parsers.re(
        r"the mismatches will contain a mismatch "
        r'with error "(?P<path>[^"]+)" -> "(?P<message>[^"]+)"'
    )
)
def the_mismatches_will_contain_a_mismatch_with_error(
    path: str,
    message: str,
    mismatches: list[Mismatch],
) -> None:
    """The mismatches will contain a mismatch with error."""
    logger.info("Searching for mismatch with path=%r, error=%r", path, message)
    for mismatch in mismatches:
        for submismatch in getattr(mismatch, "mismatches", []):
            logger.info("Checking submismatch: %r", submismatch)
            if (
                (s_path := getattr(submismatch, "path", None))
                and path == s_path
                and (s_message := getattr(submismatch, "mismatch", None))
                and message in s_message
            ):
                logger.info("Found matching submismatch: %r", submismatch)
                return

    msg = f"Mismatch not found: path={path!r}, error={message!r}"
    raise AssertionError(msg)
