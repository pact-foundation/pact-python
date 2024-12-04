"""Matching HTTP parts (request or response) feature tests."""

import re
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from pytest_bdd import (
    given,
    parsers,
    scenario,
    then,
    when,
)

from pact.v3 import Pact
from pact.v3.verifier import Verifier
from tests.v3.compatibility_suite.util.interaction_definition import (
    InteractionDefinition,
)
from tests.v3.compatibility_suite.util.provider import Provider

################################################################################
## Scenarios
################################################################################


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/http_matching.feature",
    "Comparing accept headers where the actual has additional parameters",
)
def test_comparing_accept_headers_where_the_actual_has_additional_parameters() -> None:
    """Comparing accept headers where the actual has additional parameters."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/http_matching.feature",
    "Comparing accept headers where the actual has is missing a value",
)
def test_comparing_accept_headers_where_the_actual_has_is_missing_a_value() -> None:
    """Comparing accept headers where the actual has is missing a value."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/http_matching.feature",
    "Comparing content type headers where the actual has a charset",
)
def test_comparing_content_type_headers_where_the_actual_has_a_charset() -> None:
    """Comparing content type headers where the actual has a charset."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/http_matching.feature",
    "Comparing content type headers where the actual has a different charset",
)
def test_comparing_content_type_headers_where_the_actual_has_a_different_charset() -> (
    None
):
    """Comparing content type headers where the actual has a different charset."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/http_matching.feature",
    "Comparing content type headers where the actual is missing a charset",
)
def test_comparing_content_type_headers_where_the_actual_is_missing_a_charset() -> None:
    """Comparing content type headers where the actual is missing a charset."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/http_matching.feature",
    "Comparing content type headers where they have the same charset",
)
def test_comparing_content_type_headers_where_they_have_the_same_charset() -> None:
    """Comparing content type headers where they have the same charset."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/http_matching.feature",
    "Comparing content type headers which are equal",
)
def test_comparing_content_type_headers_which_are_equal() -> None:
    """Comparing content type headers which are equal."""


################################################################################
## Given
################################################################################


@given(
    parsers.re(
        r'a request is received with an? "(?P<name>[^"]+)" header of "(?P<value>[^"]+)"'
    ),
    target_fixture="interaction_definition",
)
def a_request_is_received_with_header(name: str, value: str) -> InteractionDefinition:
    """A request is received with a "content-type" header of "application/json"."""
    interaction_definition = InteractionDefinition(method="GET", path="/", type="HTTP")
    interaction_definition.response_headers.update({name: value})
    return interaction_definition


@given(
    parsers.re(
        r'an expected request with an? "(?P<name>[^"]+)" header of "(?P<value>[^"]+)"'
    )
)
def an_expected_request_with_header(name: str, value: str, temp_dir: Path) -> None:
    """An expected request with a "content-type" header of "application/json"."""
    pact = Pact("consumer", "provider")
    pact.with_specification("V3")
    interaction_definition = InteractionDefinition(method="GET", path="/", type="HTTP")
    interaction_definition.response_headers.update({name: value})
    interaction_definition.add_to_pact(pact, name)
    (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
    pact.write_file(temp_dir / "pacts")


################################################################################
## When
################################################################################


@when("the request is compared to the expected one", target_fixture="provider")
def the_request_is_compared_to_the_expected_one(
    interaction_definition: InteractionDefinition,
) -> Generator[Provider, None, None]:
    """The request is compared to the expected one."""
    provider = Provider()
    provider.add_interaction(interaction_definition)

    with provider:
        yield provider


################################################################################
## Then
################################################################################


@then(
    parsers.re("the comparison should(?P<negated>( NOT)?) be OK"),
    converters={"negated": lambda x: x == " NOT"},
    target_fixture="verifier_result",
)
def the_comparison_should_not_be_ok(
    provider: Provider,
    verifier: Verifier,
    temp_dir: Path,
    negated: bool,  # noqa: FBT001
) -> Verifier:
    """The comparison should NOT be OK."""
    verifier.add_transport(url=provider.url)
    verifier.add_transport(
        protocol="http",
        port=provider.url.port,
        path="/",
    )
    verifier.add_source(temp_dir / "pacts")
    if negated:
        with pytest.raises(RuntimeError):
            verifier.verify()
    else:
        verifier.verify()
    return verifier


@then(
    parsers.parse(
        'the mismatches will contain a mismatch with error "{mismatch_key}" '
        "-> \"Expected header '{header_name}' to have value '{expected_value}' "
        "but was '{actual_value}'\""
    )
)
def the_mismatches_will_contain_a_mismatch_with_error(
    verifier_result: Verifier,
    mismatch_key: str,
    header_name: str,
    expected_value: str,
    actual_value: str,
) -> None:
    """Mismatches will contain a mismatch with error."""
    expected_value_matcher = re.compile(expected_value)
    actual_value_matcher = re.compile(actual_value)
    expected_error_matcher = re.compile(
        rf"Mismatch with header \'{mismatch_key}\': Expected header \'{header_name}\' "
        rf"to have value \'{expected_value}\' but was \'{actual_value}\'"
    )
    mismatch = verifier_result.results["errors"][0]["mismatch"]["mismatches"][0]
    assert mismatch["key"] == mismatch_key
    assert mismatch["type"] == "HeaderMismatch"
    assert expected_value_matcher.match(mismatch["expected"]) is not None
    assert actual_value_matcher.match(mismatch["actual"]) is not None
    assert expected_error_matcher.match(mismatch["mismatch"]) is not None
