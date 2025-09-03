"""Test of V4 generators."""

from __future__ import annotations

import json
import logging
import re
from contextvars import ContextVar
from typing import TYPE_CHECKING, Literal

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
from tests.compatibility_suite.util import parse_horizontal_table
from tests.compatibility_suite.util.interaction_definition import (
    InteractionDefinition,
    InteractionState,
)
from tests.compatibility_suite.util.provider import Provider

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

logger = logging.getLogger(__name__)

SERVER_URL: ContextVar[str | None] = ContextVar("SERVER_URL", default=None)


@pytest.fixture
def pact() -> Pact:
    return Pact(
        "v4-generators-consumer",
        "v4-generators-provider",
    ).with_specification("V4")


@pytest.fixture
def verifier() -> Verifier:
    return Verifier("v4-generators-provider")


def test_provider_state_generator(
    pact: Pact, tmp_path: Path, verifier: Verifier
) -> None:
    """Test the provider state generator."""
    (
        pact.upon_receiving("a generators request")
        .given("a provider state exists", {"id": 1000})
        .with_request("POST", "/")
        .with_body({"one": "a", "two": "b"})
        .with_generators({
            "body": {
                "$.one": {
                    "type": "ProviderState",
                    "expression": "${id}",
                }
            }
        })
        .will_respond_with(200)
    )

    pacts_path = tmp_path / "pacts"
    pacts_path.mkdir(exist_ok=True, parents=True)
    pact.write_file(pacts_path)
    verifier.add_source(pacts_path)

    provider = Provider()
    provider.add_interaction(
        InteractionDefinition(
            method="POST",
            path="/",
            response="200",
        )
    )
    verifier.add_transport(url=provider.url)

    with provider:
        verifier.verify()

    assert provider.requests
    assert len(provider.requests) == 1
    request = provider.requests[0]
    assert request["body"]
    assert json.loads(request["body"]) == {"one": 1000, "two": "b"}


################################################################################
## Scenario
################################################################################


@scenario(
    "definition/features/V4/generators.feature",
    "Supports a Mock server URL generator",
)
def test_supports_a_mock_server_url_generator() -> None:
    """Supports a Mock server URL generator."""


@pytest.mark.skip(reason="Manually implemented outside of pytest-bdd")
@scenario(
    "definition/features/V4/generators.feature",
    "Supports a Provider State generator",
)
def test_supports_a_provider_state_generator() -> None:
    """Supports a Provider State generator."""


@scenario(
    "definition/features/V4/generators.feature",
    "Supports a URN UUID generator",
)
def test_supports_a_urn_uuid_generator() -> None:
    """Supports a URN UUID generator."""


@scenario(
    "definition/features/V4/generators.feature",
    "Supports a lower-case-hyphenated UUID generator",
)
def test_supports_a_lowercasehyphenated_uuid_generator() -> None:
    """Supports a lower-case-hyphenated UUID generator."""


@scenario(
    "definition/features/V4/generators.feature",
    "Supports a simple UUID generator",
)
def test_supports_a_simple_uuid_generator() -> None:
    """Supports a simple UUID generator."""


@scenario(
    "definition/features/V4/generators.feature",
    "Supports a upper-case-hyphenated UUID generator",
)
def test_supports_a_uppercasehyphenated_uuid_generator() -> None:
    """Supports a upper-case-hyphenated UUID generator."""


################################################################################
## Scenario
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
    interaction.states.append(InteractionState("a provider state exists", {"id": 1000}))
    interaction.add_to_pact(pact, "a generators request")
    return interaction


@given(
    parsers.re(r'the generator test mode is set as "(?P<mode>Consumer|Provider)"'),
    target_fixture="mode",
)
def the_generator_test_mode_is_set(
    mode: Literal["Consumer", "Provider"],
) -> Literal["Consumer", "Provider"]:
    """The generator test mode is set."""
    return mode


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


@when(
    parsers.re(
        r"the request is prepared for use "
        r'with a "(?P<context>mockServer)" context:'
    ),
    target_fixture="response",
)
def the_request_is_prepared_with_context(
    pact: Pact,
    context: Literal["mockServer"],
    datatable: list[list[str]],
) -> requests.Response | Provider:
    """The request is prepared for use with a context:."""
    if context == "mockServer":
        data = json.loads(datatable[0][0])
        assert data
        with pact.serve() as srv:
            SERVER_URL.set(str(srv.url))
            response = requests.get(
                str(srv.url),
                timeout=2,
            )
            response.raise_for_status()

        return response

    msg = f"Unknown context {context!r}"
    raise ValueError(msg)


################################################################################
## Then
################################################################################


GENERATOR_PATTERN: dict[str, Callable[[object], bool]] = {
    "upper-case-hyphenated UUID": lambda v: isinstance(v, str)
    and re.match(r"^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$", v)
    is not None,
    "lower-case-hyphenated UUID": lambda v: isinstance(v, str)
    and re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", v)
    is not None,
    "simple UUID": lambda v: isinstance(v, str)
    and re.match(r"^[0-9a-fA-F]{32}$", v) is not None,
    "URN UUID": lambda v: isinstance(v, str)
    and re.match(
        r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", v
    )
    is not None,
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


@then(
    parsers.re(
        r'the body value for "\$\.one" will have been replaced with "(?P<value>[^"]+)"'
    )
)
def the_body_value_will_have_been_replaced_with_value(
    response: requests.Response | Provider,
) -> None:
    """The body value for "$.one" will have been replaced."""
    assert isinstance(response, requests.Response)
    data = response.json()
    logger.info("Response JSON: %r", data)

    assert "one" in data, 'Response body does not contain key "one"'
    assert (url := SERVER_URL.get())
    logger.info("Server URL: %r", url)
    # Note: IPv6 requires the square brackets, but there is currently a bug in
    #       the mock server that may result in the brackets being omitted.
    url_pattern = re.escape(url).replace(
        r"localhost", r"(127\.0\.0\.1|\[?::1\]?|localhost)"
    )
    logger.info("URL Pattern: %r", url_pattern)
    assert (
        re.match(
            url_pattern,
            data["one"],
        )
        is not None
    )
