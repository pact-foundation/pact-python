"""Basic HTTP consumer feature tests."""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Any, Generator

import pytest
import requests
from pytest_bdd import given, parsers, scenario, then, when
from yarl import URL

from pact.v3 import Pact
from tests.v3.compatiblity_suite.util import (
    FIXTURES_ROOT,
    InteractionDefinition,
    string_to_int,
    truncate,
)

if TYPE_CHECKING:
    from pathlib import Path

    from pact.v3.pact import PactServer

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


# TODO: Enable this test when the upstream issue is resolved:
# https://github.com/pact-foundation/pact-compatibility-suite/issues/3
@pytest.mark.skip("Waiting on upstream fix")
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


# TODO: Enable this test when the upstream issue is resolved:
# https://github.com/pact-foundation/pact-reference/issues/336
@pytest.mark.skip("Waiting on upstream fix")
@scenario(
    "definition/features/V1/http_consumer.feature",
    "Request with a binary body (positive case)",
)
def test_request_with_a_binary_body_positive_case() -> None:
    """
    Request with a binary body (positive case).
    """


# TODO: Enable this test when the upstream issue is resolved:
# https://github.com/pact-foundation/pact-reference/issues/336
@pytest.mark.skip("Waiting on upstream fix")
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
    parsers.parse("the following HTTP interactions have been defined:\n{content}"),
    target_fixture="interaction_definitions",
)
def the_following_http_interactions_have_been_defined(
    content: str,
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
    rows = [
        list(map(str.strip, row.split("|")))[1:-1]
        for row in content.split("\n")
        if row.strip()
    ]

    # Check that the table is well-formed
    assert len(rows[0]) == 9
    assert rows[0][0] == "No"

    # Parse the table into a more useful format
    interactions: dict[int, InteractionDefinition] = {}
    for row in rows[1:]:
        interactions[int(row[0])] = InteractionDefinition(**dict(zip(rows[0], row)))
    return interactions


################################################################################
## When
################################################################################


@when(
    parsers.re(
        r"the mock server is started"
        r" with interactions?"
        r' "?(?P<ids>((\d+)(,\s)?)+)"?',
    ),
    converters={"ids": lambda s: list(map(int, s.split(",")))},
    target_fixture="srv",
)
def the_mock_server_is_started_with_interactions(  # noqa: C901
    ids: list[int],
    interaction_definitions: dict[int, InteractionDefinition],
) -> Generator[PactServer, Any, None]:
    """The mock server is started with interactions."""
    pact = Pact("consumer", "provider")
    pact.with_specification("V1")
    for iid in ids:
        definition = interaction_definitions[iid]
        logging.info("Adding interaction %s", iid)

        interaction = pact.upon_receiving(f"interactions {iid}")
        logging.info("-> with_request(%s, %s)", definition.method, definition.path)
        interaction.with_request(definition.method, definition.path)

        if definition.query:
            query = URL.build(query_string=definition.query).query
            logging.info("-> with_query_parameters(%s)", query.items())
            interaction.with_query_parameters(query.items())

        if definition.headers:
            logging.info("-> with_headers(%s)", definition.headers.items())
            interaction.with_headers(definition.headers.items())

        if definition.body:
            if definition.body.string:
                logging.info(
                    "-> with_body(%s, %s)",
                    truncate(definition.body.string),
                    definition.body.mime_type,
                )
                interaction.with_body(
                    definition.body.string,
                    definition.body.mime_type,
                )
            elif definition.body.bytes:
                logging.info(
                    "-> with_binary_file(%s, %s)",
                    truncate(definition.body.bytes),
                    definition.body.mime_type,
                )
                interaction.with_binary_body(
                    definition.body.bytes,
                    definition.body.mime_type,
                )
            else:
                msg = "Unexpected body definition"
                raise RuntimeError(msg)

        logging.info("-> will_respond_with(%s)", definition.response)
        interaction.will_respond_with(definition.response)

        if definition.response_content:
            if definition.response_body is None:
                msg = "Expected response body along with response content type"
                raise ValueError(msg)

            if definition.response_body.string:
                logging.info(
                    "-> with_body(%s, %s)",
                    truncate(definition.response_body.string),
                    definition.response_content,
                )
                interaction.with_body(
                    definition.response_body.string,
                    definition.response_content,
                )
            elif definition.response_body.bytes:
                logging.info(
                    "-> with_binary_file(%s, %s)",
                    truncate(definition.response_body.bytes),
                    definition.response_content,
                )
                interaction.with_binary_body(
                    definition.response_body.bytes,
                    definition.response_content,
                )
            else:
                msg = "Unexpected body definition"
                raise RuntimeError(msg)

    with pact.serve(raises=False) as srv:
        yield srv


@when(
    parsers.re(
        r"request (?P<request_id>\d+) is made to the mock server",
    ),
    converters={"request_id": int},
    target_fixture="response",
)
def request_n_is_made_to_the_mock_server(
    interaction_definitions: dict[int, InteractionDefinition],
    request_id: int,
    srv: PactServer,
) -> requests.Response:
    """
    Request n is made to the mock server.
    """
    definition = interaction_definitions[request_id]
    if (
        definition.body
        and definition.body.mime_type
        and "Content-Type" not in definition.headers
    ):
        definition.headers.add("Content-Type", definition.body.mime_type)

    return requests.request(
        definition.method,
        str(srv.url.with_path(definition.path)),
        params=(
            URL.build(query_string=definition.query).query if definition.query else None
        ),
        headers=definition.headers if definition.headers else None,  # type: ignore[arg-type]
        data=definition.body.bytes if definition.body else None,
    )


@when(
    parsers.re(
        r"request (?P<request_id>\d+) is made to the mock server"
        r" with the following changes?:\n(?P<content>.*)",
        re.DOTALL,
    ),
    converters={"request_id": int},
    target_fixture="response",
)
def request_n_is_made_to_the_mock_server_with_the_following_changes(
    interaction_definitions: dict[int, InteractionDefinition],
    request_id: int,
    content: str,
    srv: PactServer,
) -> requests.Response:
    """
    Request n is made to the mock server with changes.

    The content is a markdown table with a subset of the columns defining the
    definition (as in the given step).
    """
    definition = interaction_definitions[request_id]
    rows = [
        list(map(str.strip, row.split("|")))[1:-1]
        for row in content.split("\n")
        if row.strip()
    ]
    assert len(rows) == 2, "Expected two rows in the table"
    updates = dict(zip(rows[0], rows[1]))
    definition.update(**updates)

    if (
        definition.body
        and definition.body.mime_type
        and "Content-Type" not in definition.headers
    ):
        definition.headers.add("Content-Type", definition.body.mime_type)

    return requests.request(
        definition.method,
        str(srv.url.with_path(definition.path)),
        params=(
            URL.build(query_string=definition.query).query if definition.query else None
        ),
        headers=definition.headers if definition.headers else None,  # type: ignore[arg-type]
        data=definition.body.bytes if definition.body else None,
    )


################################################################################
## Then
################################################################################


@then(
    parsers.re(
        r"a (?P<code>\d+) (success|error) response is returned",
    ),
    converters={"code": int},
)
def a_response_is_returned(
    response: requests.Response,
    code: int,
    srv: PactServer,
) -> None:
    """
    A response is returned.
    """
    logging.info("Request Information:")
    logging.info("-> Method: %s", response.request.method)
    logging.info("-> URL: %s", response.request.url)
    logging.info(
        "-> Headers: %s",
        json.dumps(
            dict(**response.request.headers),
            indent=2,
        ),
    )
    logging.info(
        "-> Body: %s",
        truncate(response.request.body) if response.request.body else None,
    )
    logging.info("Mismatches:\n%s", json.dumps(srv.mismatches, indent=2))
    assert response.status_code == code


@then(
    parsers.re(
        r'the payload will contain the "(?P<file>[^"]+)" JSON document',
    ),
)
def the_payload_will_contain_the_json_document(
    response: requests.Response,
    file: str,
) -> None:
    """
    The payload will contain the JSON document.
    """
    path = FIXTURES_ROOT / f"{file}.json"
    assert response.json() == json.loads(path.read_text())


@then(
    parsers.re(
        r'the content type will be set as "(?P<content_type>[^"]+)"',
    ),
)
def the_content_type_will_be_set_as(
    response: requests.Response,
    content_type: str,
) -> None:
    assert response.headers["Content-Type"] == content_type


@when("the pact test is done")
def the_pact_test_is_done() -> None:
    """
    The pact test is done.
    """


@then(
    parsers.re(r"the mock server status will (?P<negated>(NOT )?)be OK"),
    converters={"negated": lambda s: s == "NOT "},
)
def the_mock_server_status_will_be(
    srv: PactServer,
    negated: bool,  # noqa: FBT001
) -> None:
    """
    The mock server status will be.
    """
    assert srv.matched is not negated


@then(
    parsers.re(
        r"the mock server status will be"
        r" an expected but not received error"
        r" for interaction \{(?P<n>\d+)\}",
    ),
    converters={"n": int},
)
def the_mock_server_status_will_be_an_expected_but_not_received_error_for_interaction_n(
    srv: PactServer,
    n: int,
    interaction_definitions: dict[int, InteractionDefinition],
) -> None:
    """
    The mock server status will be an expected but not received error for interaction n.
    """
    assert srv.matched is False
    assert len(srv.mismatches) > 0

    for mismatch in srv.mismatches:
        if (
            mismatch["method"] == interaction_definitions[n].method
            and mismatch["path"] == interaction_definitions[n].path
            and mismatch["type"] == "missing-request"
        ):
            return
    pytest.fail("Expected mismatch not found")


@then(
    parsers.re(
        r"the mock server status will be"
        r' an unexpected "(?P<method>[^"]+)" request received error'
        r" for interaction \{(?P<n>\d+)\}",
    ),
    converters={"n": int},
)
def the_mock_server_status_will_be_an_unexpected_request_received_for_interaction_n(
    srv: PactServer,
    method: str,
    n: int,
    interaction_definitions: dict[int, InteractionDefinition],
) -> None:
    """
    The mock server status will be an expected but not received error for interaction n.
    """
    assert srv.matched is False
    assert len(srv.mismatches) > 0

    for mismatch in srv.mismatches:
        if (
            mismatch["method"] == interaction_definitions[n].method
            and mismatch["request"]["method"] == method
            and mismatch["path"] == interaction_definitions[n].path
            and mismatch["type"] == "request-not-found"
        ):
            return
    pytest.fail("Expected mismatch not found")


@then(
    parsers.re(
        r"the mock server status will be"
        r' an unexpected "(?P<method>[^"]+)" request received error'
        r' for path "(?P<path>[^"]+)"',
    ),
    converters={"n": int},
)
def the_mock_server_status_will_be_an_unexpected_request_received_for_path(
    srv: PactServer,
    method: str,
    path: str,
) -> None:
    """
    The mock server status will be an expected but not received error for interaction n.
    """
    assert srv.matched is False
    assert len(srv.mismatches) > 0

    for mismatch in srv.mismatches:
        if (
            mismatch["request"]["method"] == method
            and mismatch["path"] == path
            and mismatch["type"] == "request-not-found"
        ):
            return
    pytest.fail("Expected mismatch not found")


@then("the mock server status will be mismatches")
def the_mock_server_status_will_be_mismatches(
    srv: PactServer,
) -> None:
    """
    The mock server status will be mismatches.
    """
    assert srv.matched is False
    assert len(srv.mismatches) > 0


@then(
    parsers.re(
        r'the mismatches will contain a "(?P<mismatch_type>[^"]+)" mismatch'
        r' with error "(?P<error>[^"]+)"',
    ),
)
def the_mismatches_will_contain_a_mismatch_with_the_error(
    srv: PactServer,
    mismatch_type: str,
    error: str,
) -> None:
    """
    The mismatches will contain a mismatch with the error.
    """
    if mismatch_type == "query":
        mismatch_type = "QueryMismatch"
    elif mismatch_type == "header":
        mismatch_type = "HeaderMismatch"
    elif mismatch_type == "body":
        mismatch_type = "BodyMismatch"
    elif mismatch_type == "body-content-type":
        mismatch_type = "BodyTypeMismatch"
    else:
        msg = f"Unexpected mismatch type: {mismatch_type}"
        raise ValueError(msg)

    logger.info("Expecting mismatch: %s", mismatch_type)
    logger.info("With error: %s", error)
    for mismatch in srv.mismatches:
        for sub_mismatch in mismatch["mismatches"]:
            if (
                error in sub_mismatch["mismatch"]
                and sub_mismatch["type"] == mismatch_type
            ):
                return
    pytest.fail("Expected mismatch not found")


@then(
    parsers.re(
        r'the mismatches will contain a "(?P<mismatch_type>[^"]+)" mismatch'
        r' with path "(?P<path>[^"]+)"'
        r' with error "(?P<error>[^"]+)"',
    ),
)
def the_mismatches_will_contain_a_mismatch_with_path_with_the_error(
    srv: PactServer,
    mismatch_type: str,
    path: str,
    error: str,
) -> None:
    """
    The mismatches will contain a mismatch with the error.
    """
    mismatch_type = "BodyMismatch" if mismatch_type == "body" else mismatch_type
    for mismatch in srv.mismatches:
        for sub_mismatch in mismatch["mismatches"]:
            if (
                sub_mismatch["mismatch"] == error
                and sub_mismatch["type"] == mismatch_type
                and sub_mismatch["path"] == path
            ):
                return
    pytest.fail("Expected mismatch not found")


@then(
    parsers.re(
        r"the mock server will (?P<negated>(NOT )?)write out"
        r" a Pact file for the interactions? when done",
    ),
    converters={"negated": lambda s: s == "NOT "},
    target_fixture="pact_file",
)
def the_mock_server_will_write_out_a_pact_file_for_the_interaction_when_done(
    srv: PactServer,
    temp_dir: Path,
    negated: bool,  # noqa: FBT001
) -> dict[str, Any] | None:
    """
    The mock server will write out a Pact file for the interaction when done.
    """
    if not negated:
        srv.write_file(temp_dir)
        output = temp_dir / "consumer-provider.json"
        assert output.is_file()
        return json.load(output.open())
    return None


@then(
    parsers.re(r"the pact file will contain \{(?P<n>\d+)\} interactions?"),
    converters={"n": int},
)
def the_pact_file_will_contain_n_interactions(
    pact_file: dict[str, Any],
    n: int,
) -> None:
    """
    The pact file will contain n interactions.
    """
    assert len(pact_file["interactions"]) == n


@then(
    parsers.re(
        r"the \{(?P<n>\w+)\} interaction response"
        r' will contain the "(?P<file>[^"]+)" document',
    ),
    converters={"n": string_to_int},
)
def the_nth_interaction_will_contain_the_document(
    pact_file: dict[str, Any],
    n: int,
    file: str,
) -> None:
    """
    The nth interaction response will contain the document.
    """
    file_path = FIXTURES_ROOT / file
    if file.endswith(".json"):
        assert pact_file["interactions"][n - 1]["response"]["body"] == json.load(
            file_path.open(),
        )


@then(
    parsers.re(
        r'the \{(?P<n>\w+)\} interaction request will be for a "(?P<method>[A-Z]+)"',
    ),
    converters={"n": string_to_int},
)
def the_nth_interaction_request_will_be_for_method(
    pact_file: dict[str, Any],
    n: int,
    method: str,
) -> None:
    """
    The nth interaction request will be for a method.
    """
    assert pact_file["interactions"][n - 1]["request"]["method"] == method


@then(
    parsers.re(
        r"the \{(?P<n>\w+)\} interaction request"
        r' query parameters will be "(?P<query>[^"]+)"',
    ),
    converters={"n": string_to_int},
)
def the_nth_interaction_request_query_parameters_will_be(
    pact_file: dict[str, Any],
    n: int,
    query: str,
) -> None:
    """
    The nth interaction request query parameters will be.
    """
    assert query == pact_file["interactions"][n - 1]["request"]["query"]


@then(
    parsers.re(
        r"the \{(?P<n>\w+)\} interaction request"
        r' will contain the header "(?P<key>[^"]+)"'
        r' with value "(?P<value>[^"]+)"',
    ),
    converters={"n": string_to_int},
)
def the_nth_interaction_request_will_contain_the_header(
    pact_file: dict[str, Any],
    n: int,
    key: str,
    value: str,
) -> None:
    """
    The nth interaction request will contain the header.
    """
    expected = {key: value}
    actual = pact_file["interactions"][n - 1]["request"]["headers"]
    assert expected.keys() == actual.keys()
    for key in expected:
        assert expected[key] == actual[key] or [expected[key]] == actual[key]


@then(
    parsers.re(
        r"the \{(?P<n>\w+)\} interaction request"
        r' content type will be "(?P<content_type>[^"]+)"',
    ),
    converters={"n": string_to_int},
)
def the_nth_interaction_request_content_type_will_be(
    pact_file: dict[str, Any],
    n: int,
    content_type: str,
) -> None:
    """
    The nth interaction request will contain the header.
    """
    assert (
        pact_file["interactions"][n - 1]["request"]["headers"]["Content-Type"]
        == content_type
    )


@then(
    parsers.re(
        r"the \{(?P<n>\w+)\} interaction request"
        r' will contain the "(?P<file>[^"]+)" document',
    ),
    converters={"n": string_to_int},
)
def the_nth_interaction_request_will_contain_the_document(
    pact_file: dict[str, Any],
    n: int,
    file: str,
) -> None:
    """
    The nth interaction request will contain the document.
    """
    file_path = FIXTURES_ROOT / file
    if file.endswith(".json"):
        assert pact_file["interactions"][n - 1]["request"]["body"] == json.load(
            file_path.open(),
        )
    else:
        assert (
            pact_file["interactions"][n - 1]["request"]["body"] == file_path.read_text()
        )
