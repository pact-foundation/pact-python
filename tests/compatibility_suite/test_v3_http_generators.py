"""Test V3 HTTP generators."""

from __future__ import annotations

import contextlib
import json
import re
from typing import TYPE_CHECKING, Literal
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
from tests.compatibility_suite.util import parse_horizontal_table
from tests.compatibility_suite.util.interaction_definition import (
    InteractionDefinition,
    InteractionState,
)
from tests.compatibility_suite.util.provider import Provider

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


@pytest.fixture
def pact() -> Pact:
    return Pact(
        "v3-http-generators-consumer",
        "v3-http-generators-provider",
    ).with_specification("V3")


@pytest.fixture
def verifier() -> Verifier:
    return Verifier("v3-http-generators-provider")


@pytest.fixture
def response() -> requests.Response | None:
    """
    Default response, which gets overridden when needed.
    """
    return None


################################################################################
## Scenario
################################################################################


@scenario(
    "definition/features/V3/http_generators.feature",
    "Supports using a generator with the request body",
)
def test_supports_using_a_generator_with_the_request_body() -> None:
    """Supports using a generator with the request body."""


@scenario(
    "definition/features/V3/http_generators.feature",
    "Supports using a generator with the request headers",
)
def test_supports_using_a_generator_with_the_request_headers() -> None:
    """Supports using a generator with the request headers."""


@scenario(
    "definition/features/V3/http_generators.feature",
    "Supports using a generator with the request path",
)
def test_supports_using_a_generator_with_the_request_path() -> None:
    """Supports using a generator with the request path."""


@scenario(
    "definition/features/V3/http_generators.feature",
    "Supports using a generator with the request query parameters",
)
def test_supports_using_a_generator_with_the_request_query_parameters() -> None:
    """Supports using a generator with the request query parameters."""


@scenario(
    "definition/features/V3/http_generators.feature",
    "Supports using a generator with the response body",
)
def test_supports_using_a_generator_with_the_response_body() -> None:
    """Supports using a generator with the response body."""


@scenario(
    "definition/features/V3/http_generators.feature",
    "Supports using a generator with the response headers",
)
def test_supports_using_a_generator_with_the_response_headers() -> None:
    """Supports using a generator with the response headers."""


@scenario(
    "definition/features/V3/http_generators.feature",
    "Supports using a generator with the response status",
)
def test_supports_using_a_generator_with_the_response_status() -> None:
    """Supports using a generator with the response status."""


################################################################################
## Given
################################################################################


@given(
    parsers.re(
        r"a (?P<part>request|response) configured with the following generators:"
    ),
    target_fixture="provider",
)
def a_request_configured_with_the_following_generators(
    part: Literal["request", "response"],
    tmp_path: Path,
    pact: Pact,
    verifier: Verifier,
    datatable: list[list[str]],
) -> Provider:
    """A request configured with the following generators."""
    data = parse_horizontal_table(datatable)
    assert len(data) == 1, "Expected a single row of data"
    row: dict[str, str | None] = data[0]  # type: ignore[assignment]

    if part == "response":
        row["response generators"] = row.pop("generators")
        if body := row.pop("body", None):
            row["response body"] = body

    interaction = InteractionDefinition(
        method="POST",
        path="/",
        response="200",
        **row,  # type: ignore[arg-type]
    )
    interaction.states.append(InteractionState("a provider state exists", {"id": 1000}))
    interaction.add_to_pact(pact, "a generators request")

    provider = Provider()
    provider.add_interaction(interaction)

    pacts_path = tmp_path / "pacts"
    pacts_path.mkdir(exist_ok=True, parents=True)
    pact.write_file(pacts_path)
    verifier.add_source(pacts_path)

    # with provider:
    #     yield provider
    return provider


@given('the generator test mode is set as "Provider"')
def the_generator_test_mode_is_set_as_provider() -> None:
    """The generator test mode is set as "Provider"."""


################################################################################
## When
################################################################################


@when(parsers.re("the request is prepared for use.*"))
def the_request_is_prepared_for_use(
    verifier: Verifier,
    provider: Provider,
) -> None:
    """The request is prepared for use."""
    verifier.add_transport(url=provider.url)

    with provider, contextlib.suppress(RuntimeError):
        verifier.verify()


@when("the response is prepared for use", target_fixture="response")
def the_response_is_prepared_for_use(
    pact: Pact,
) -> requests.Response:
    """The response is prepared for use."""
    with pact.serve() as srv:
        return requests.post(
            str(srv.url),
            json={"one": "1"},
            headers={"Content-Type": "application/json"},
            timeout=2,
        )


################################################################################
## Then
################################################################################


GENERATOR_PATTERN: dict[str, Callable[[object], bool]] = {
    "integer": lambda v: isinstance(v, int) or (isinstance(v, str) and v.isdigit()),
}


@then(
    parsers.re(
        r'the body value for "\$\.one" '
        r'will have been replaced with an? "(?P<value>[^"]+)"'
    )
)
def the_body_value_will_have_been_replaced(
    value: str,
    provider: Provider,
    response: requests.Response | None,
) -> None:
    """The body value for "$.one" will have been replaced with a value."""
    assert provider.requests or response

    if provider.requests:
        request = provider.requests[0]

        assert (body := request["body"])
        assert (data := json.loads(body))
        assert (one := data.get("one"))
        assert value in GENERATOR_PATTERN
        assert GENERATOR_PATTERN[value](one)

    if response:
        data = response.json()
        assert "one" in data
        assert value in GENERATOR_PATTERN
        assert GENERATOR_PATTERN[value](data["one"])


@then(
    parsers.re(
        r'the request "(?P<part>queryParameter|header)\[(?P<name>[^\]]+)\]" '
        r'will match "(?P<pattern>[^"]+)"'
    )
)
def the_request_header_will_match(
    part: Literal["queryParameter", "header"],
    name: str,
    pattern: str,
    provider: Provider,
) -> None:
    """The request header will match."""
    assert provider.requests
    request = provider.requests[0]

    if part == "queryParameter":
        assert (query := request["query"])
        query_dict = parse_qs(query)
        assert (value := query_dict.get(name))
        assert re.match(pattern, value[0])
        return

    if part == "header":
        assert (headers := request["headers"])
        assert (value := headers.get(name))  # type: ignore[assignment]
        assert value is not None
        assert re.match(pattern, value)


@then(
    parsers.re(
        r'the response "header\[(?P<name>[^\]]+)\]" will match "(?P<pattern>[^"]+)"'
    )
)
def the_response_header_will_match(
    name: str,
    pattern: str,
    response: requests.Response | None,
) -> None:
    """The response header will match the given pattern."""
    assert response is not None
    value = response.headers.get(name)
    assert value is not None
    assert re.match(pattern, value)


@then(parsers.re(r'the request "path" will be set as "(?P<path>[^"]+)"'))
def the_request_path_will_be_set_as(path: str, provider: Provider) -> None:
    """The request "path" will be set as "/path/1000"."""
    assert provider.requests
    request = provider.requests[0]

    assert request.get("path") == path


@then(parsers.re(r'the response "status" will match "(?P<pattern>[^"]+)"'))
def the_response_status_will_match(
    pattern: str, response: requests.Response | None
) -> None:
    """The response "status" will match a given pattern."""
    assert response is not None
    status_code = str(response.status_code)
    assert re.match(pattern, status_code)


@then(parsers.re(r'the response "status" will not be "(?P<status>\d+)"'))
def the_response_status_will_not_be_200(
    status: str, response: requests.Response | None
) -> None:
    """The response "status" will not be the given status."""
    assert response is not None
    assert str(response.status_code) != status
