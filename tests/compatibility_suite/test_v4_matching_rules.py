"""V4 matching rules tests."""

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

from pact import Pact, Verifier
from tests.compatibility_suite.util import (
    FIXTURES_ROOT,
    parse_horizontal_table,
)
from tests.compatibility_suite.util.interaction_definition import (
    InteractionDefinition,
)
from tests.compatibility_suite.util.provider import Provider

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
        "v4-matching-rules-consumer",
        "v4-matching-rules-provider",
    ).with_specification("V4")


@pytest.fixture
def verifier() -> Verifier:
    return Verifier("v4-matching-rules-provider")


################################################################################
## Scenario
################################################################################


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports a ArrayContains matcher (negative case)",
)
def test_supports_a_arraycontains_matcher_negative_case() -> None:
    """Supports a ArrayContains matcher (negative case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports a EachValue matcher (negative case)",
)
def test_supports_a_eachvalue_matcher_negative_case() -> None:
    """Supports a EachValue matcher (negative case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports a not empty matcher (negative case 2, types are different)",
)
def test_supports_a_not_empty_matcher_negative_case_2_types_are_different() -> None:
    """Supports a not empty matcher (negative case 2, types are different)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports a not empty matcher (negative case)",
)
def test_supports_a_not_empty_matcher_negative_case() -> None:
    """Supports a not empty matcher (negative case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports a not empty matcher (positive case)",
)
def test_supports_a_not_empty_matcher_positive_case() -> None:
    """Supports a not empty matcher (positive case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports a not empty matcher with binary data (negative case)",
)
def test_supports_a_not_empty_matcher_with_binary_data_negative_case() -> None:
    """Supports a not empty matcher with binary data (negative case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports a not empty matcher with binary data (positive case)",
)
def test_supports_a_not_empty_matcher_with_binary_data_positive_case() -> None:
    """Supports a not empty matcher with binary data (positive case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports a semver matcher (negative case)",
)
def test_supports_a_semver_matcher_negative_case() -> None:
    """Supports a semver matcher (negative case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports a semver matcher (positive case)",
)
def test_supports_a_semver_matcher_positive_case() -> None:
    """Supports a semver matcher (positive case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports a status code matcher (negative case)",
)
def test_supports_a_status_code_matcher_negative_case() -> None:
    """Supports a status code matcher (negative case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports a status code matcher (positive case)",
)
def test_supports_a_status_code_matcher_positive_case() -> None:
    """Supports a status code matcher (positive case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports an ArrayContains matcher (positive case)",
)
def test_supports_an_arraycontains_matcher_positive_case() -> None:
    """Supports an ArrayContains matcher (positive case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports an EachKey matcher (negative case)",
)
def test_supports_an_eachkey_matcher_negative_case() -> None:
    """Supports an EachKey matcher (negative case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports an EachKey matcher (positive case)",
)
def test_supports_an_eachkey_matcher_positive_case() -> None:
    """Supports an EachKey matcher (positive case)."""


@scenario(
    "definition/features/V4/matching_rules.feature",
    "Supports an EachValue matcher (positive case)",
)
def test_supports_an_eachvalue_matcher_positive_case() -> None:
    """Supports an EachValue matcher (positive case)."""


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
            elif body == "EMPTY":
                body = None

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


@given("an expected response configured with the following:")
def an_expected_response_configured_with_the_following(
    pact: Pact,
    datatable: list[list[str]],
    tmp_path: Path,
    verifier: Verifier,
) -> None:
    """An expected response configured with the following."""
    data = parse_horizontal_table(datatable)
    assert len(data) == 1, "Expected exactly one row in the table"
    row = data[0]

    interaction = InteractionDefinition(
        method="POST",
        path="/",
        status=row["status"],
        response_matching_rules=row["matching rules"],
    )
    interaction.add_to_pact(pact, "a matching rules response")
    (tmp_path / "pacts").mkdir(exist_ok=True, parents=True)
    pact.write_file(tmp_path / "pacts")

    with (
        tmp_path
        / "pacts"
        / "v4-matching-rules-consumer-v4-matching-rules-provider.json"
    ).open(
        "r",
        encoding="utf-8",
    ) as f:
        for line in f:
            logger.info("Pact file: %s", line.rstrip())

    verifier.add_source(tmp_path / "pacts")


@given(
    parsers.re(r"a status (?P<status_code>\d{3}) response is received"),
    target_fixture="provider",
)
def a_response_is_received(
    status_code: str,
    verifier: Verifier,
) -> Provider:
    """A response is received."""
    provider = Provider()
    interaction = InteractionDefinition(
        method="POST",
        path="/",
        response=status_code,
    )
    provider.add_interaction(interaction)
    verifier.add_transport(url=provider.url)
    return provider


################################################################################
## When
################################################################################


@when(
    "the response is compared to the expected one",
    target_fixture="verifier_result",
)
def the_response_is_compared_to_the_expected_one(
    provider: Provider,
    verifier: Verifier,
) -> tuple[Verifier, Exception | None]:
    """The response is compared to the expected one."""
    with provider:
        try:
            verifier.verify()
        except Exception as e:  # noqa: BLE001
            return verifier, e
        return verifier, None


@when(
    parsers.re(r"the (request is|requests are) compared to the expected one"),
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
        r'with error "(?P<path>[^"]+)" -> "(?P<message>.+)"$'
    )
)
def the_mismatches_will_contain_a_mismatch_with_error(
    path: str,
    message: str,
    mismatches: list[Mismatch],
) -> None:
    """The mismatches will contain a mismatch with error."""
    # To account for slight differences in wording between implementations
    # we map some expected values here.
    path, message = {
        (
            "$",
            "Expected [] (0 bytes) to not be empty",
        ): ("/", "Expected body Present(28058 bytes, image/jpeg) but was empty"),
        (
            "$.actions",
            'Variant at index 1 ({\\"href\\":\\"http://api.x.io/orders/42/items\\",'
            '\\"method\\":\\"DELETE\\",\\"name\\":\\"delete-item\\",'
            '\\"title\\":\\"Delete Item\\"}) was not found in the actual list',
        ): (
            "$.actions",
            'Variant at index 1 ({"href":"http://api.x.io/orders/42/items",'
            '"method":"DELETE","name":"delete-item","title":"Delete Item"}) was '
            "not found in the actual list",
        ),
        (
            "$.two",
            "Type mismatch: Expected 'b' (String) "
            'to be the same type as [\\"b\\"] (Array)',
        ): (
            "$.two",
            "Type mismatch: Expected 'b' (String) "
            'to be the same type as ["b"] (Array)',
        ),
    }.get((path, message), (path, message))
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


@then(
    parsers.re(r"the response comparison should (?P<negated>(NOT )?)be OK"),
    converters={"negated": lambda s: s == "NOT "},
)
def the_response_comparison_should_be_maybe_ok(
    negated: bool,  # noqa: FBT001
    verifier_result: tuple[Verifier, Exception | None],
) -> None:
    """The response comparison should maybe be OK."""
    _, result = verifier_result
    if negated:
        assert result is not None
    else:
        assert result is None


@then(
    parsers.re(
        r'the response mismatches will contain a "(?P<mismatch_type>[^"]+)" mismatch '
        r'with error "(?P<message>.+)"$'
    )
)
def the_response_mismatches_will_contain_a_mismatch_with_error(
    mismatch_type: str,
    message: str,
    verifier_result: tuple[Verifier, Exception | None],
) -> None:
    """The response mismatches will contain a mismatch with error."""
    mismatch_type = {"status": "StatusMismatch"}[mismatch_type]

    verifier, mismatches = verifier_result
    assert mismatches is not None, "Expected mismatches to be present"
    for error in verifier.results["errors"]:
        if (mismatch := error.get("mismatch")) and (
            mismatches := mismatch.get("mismatches")
        ):
            for submismatch in mismatches:
                if submismatch.get(
                    "type"
                ) == mismatch_type and message in submismatch.get("mismatch", ""):
                    logger.info("Found matching submismatch: %r", submismatch)
                    return
    msg = f"Mismatch {mismatch_type!r} not found with error={message!r}"
    raise AssertionError(msg)
