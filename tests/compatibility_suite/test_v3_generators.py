"""Test of V3 generators."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

import pytest
import requests
from pytest_bdd import (
    given,
    parsers,
    scenario,
    then,
    when,
)

from pact import Pact
from tests.compatibility_suite.util import parse_horizontal_table
from tests.compatibility_suite.util.interaction_definition import InteractionDefinition

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)


@pytest.fixture
def pact() -> Pact:
    return Pact(
        "v3-generators-consumer",
        "v3-generators-provider",
    ).with_specification("V3")


################################################################################
## Scenario
################################################################################


@scenario("definition/features/V3/generators.feature", "Supports a UUID generator")
def test_supports_a_uuid_generator() -> None:
    """Supports a UUID generator."""


@scenario("definition/features/V3/generators.feature", "Supports a boolean generator")
def test_supports_a_boolean_generator() -> None:
    """Supports a boolean generator."""


@scenario("definition/features/V3/generators.feature", "Supports a date generator")
def test_supports_a_date_generator() -> None:
    """Supports a date generator."""


@scenario("definition/features/V3/generators.feature", "Supports a date-time generator")
def test_supports_a_datetime_generator() -> None:
    """Supports a date-time generator."""


@scenario(
    "definition/features/V3/generators.feature", "Supports a random decimal generator"
)
def test_supports_a_random_decimal_generator() -> None:
    """Supports a random decimal generator."""


@scenario(
    "definition/features/V3/generators.feature",
    "Supports a random hexadecimal generator",
)
def test_supports_a_random_hexadecimal_generator() -> None:
    """Supports a random hexadecimal generator."""


@scenario(
    "definition/features/V3/generators.feature", "Supports a random integer generator"
)
def test_supports_a_random_integer_generator() -> None:
    """Supports a random integer generator."""


@scenario(
    "definition/features/V3/generators.feature", "Supports a random string generator"
)
def test_supports_a_random_string_generator() -> None:
    """Supports a random string generator."""


@scenario("definition/features/V3/generators.feature", "Supports a regex generator")
def test_supports_a_regex_generator() -> None:
    """Supports a regex generator."""


@scenario("definition/features/V3/generators.feature", "Supports a time generator")
def test_supports_a_time_generator() -> None:
    """Supports a time generator."""


################################################################################
## Given
################################################################################


@given(
    "a request configured with the following generators:",
    target_fixture="interaction",
)
def a_request_configured_with_the_following_generators(
    pact: Pact,
    datatable: list[list[str]],
) -> InteractionDefinition:
    """A request configured with the following generators."""
    data = parse_horizontal_table(datatable)
    assert len(data) == 1, "Expected a single row of data"
    row = data[0]

    # These tests only define the response
    row["response body"] = row.pop("body")
    row["response generators"] = row.pop("generators")

    interaction = InteractionDefinition(
        method="GET",
        path="/",
        response="200",
        **row,  # type: ignore[arg-type]
    )
    interaction.add_to_pact(pact, "a generators request")
    return interaction


################################################################################
## When
################################################################################


@when("the request is prepared for use", target_fixture="response")
def the_request_is_prepared_for_use(pact: Pact) -> requests.Response:
    """The request is prepared for use."""
    with pact.serve() as srv:
        response = requests.get(
            str(srv.url),
            timeout=2,
        )
        response.raise_for_status()

    return response


################################################################################
## Then
################################################################################

GENERATOR_PATTERN: dict[str, Callable[[object], bool]] = {
    "UUID": lambda v: isinstance(v, str)
    and re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", v)
    is not None,
    "boolean": lambda v: isinstance(v, bool),
    "date": lambda v: isinstance(v, str)
    and re.match(r"^\d{4}-\d{2}-\d{2}$", v) is not None,
    "time": lambda v: isinstance(v, str)
    and re.match(r"^\d{2}:\d{2}:\d{2}(\.\d+)?$", v) is not None,
    "date-time": lambda v: isinstance(v, str)
    and re.match(
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})$", v
    )
    is not None,
    "decimal number": lambda v: isinstance(v, str)
    and re.match(r"^-?\d+\.\d+$", v) is not None,
    "hexadecimal number": lambda v: isinstance(v, str)
    and re.match(r"^[0-9a-fA-F]+$", v) is not None,
    "integer": lambda v: isinstance(v, int) or (isinstance(v, str) and v.isdigit()),
    "random string": lambda v: isinstance(v, str) and len(v) > 0,
    "string from the regex": lambda v: isinstance(v, str)
    and re.match(r"^\d{1,8}$", v) is not None,
}


@then(
    parsers.re(
        r'the body value for "\$\.one" '
        r'will have been replaced with a "(?P<value>[^"]+)"'
    )
)
def the_body_value_will_have_been_replaced(
    response: requests.Response,
    value: str,
) -> None:
    """The body value for "$.one" will have been replaced with a value."""
    data = response.json()
    logger.info("Response JSON: %r", data)

    assert "one" in data, 'Response body does not contain key "one"'
    assert value in GENERATOR_PATTERN, f"Unknown generator type {value!r}"
    assert GENERATOR_PATTERN[value](data["one"])
