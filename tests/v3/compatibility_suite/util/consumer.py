"""
Utility functions for the consumer tests.
"""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Any

import pytest
import requests
from pytest_bdd import given, parsers, then, when
from yarl import URL

from pact.v3 import Pact
from tests.v3.compatibility_suite.util import (
    FIXTURES_ROOT,
    PactInteractionTuple,
    parse_markdown_table,
    string_to_int,
    truncate,
)

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from pact.v3.interaction._async_message_interaction import AsyncMessageInteraction
    from pact.v3.pact import PactServer
    from tests.v3.compatibility_suite.util import InteractionDefinition

logger = logging.getLogger(__name__)

################################################################################
## Given
################################################################################


def a_message_integration_is_being_defined_for_a_consumer_test(
    version: str,
    stacklevel: int = 1,
) -> None:
    @given(
        parsers.re(
            r"a message (integration|interaction) "
            r"is being defined for a consumer test"
        ),
        target_fixture="pact_interaction",
        stacklevel=stacklevel + 1,
    )
    def _() -> PactInteractionTuple[AsyncMessageInteraction]:
        """
        A message integration is being defined for a consumer test.
        """
        pact = Pact("consumer", "provider")
        pact.with_specification(version)
        return PactInteractionTuple(
            pact,
            pact.upon_receiving("an asynchronous message", "Async"),
        )


################################################################################
## When
################################################################################


def the_mock_server_is_started_with_interactions(
    version: str,
    stacklevel: int = 1,
) -> None:
    @when(
        parsers.re(
            r"the mock server is started"
            r" with interactions?"
            r' "?(?P<ids>((\d+)(,\s)?)+)"?',
        ),
        converters={"ids": lambda s: list(map(int, s.split(",")))},
        target_fixture="srv",
        stacklevel=stacklevel + 1,
    )
    def _(
        ids: list[int],
        interaction_definitions: dict[int, InteractionDefinition],
    ) -> Generator[PactServer, Any, None]:
        """The mock server is started with interactions."""
        pact = Pact("consumer", "provider")
        pact.with_specification(version)
        for iid in ids:
            definition = interaction_definitions[iid]
            logging.info("Adding interaction %s", iid)
            definition.add_to_pact(pact, f"interaction {iid}")

        with pact.serve(raises=False) as srv:
            yield srv


def the_mock_server_is_started_with_interaction_n_but_with_the_following_changes(
    version: str,
    stacklevel: int = 1,
) -> None:
    @when(
        parsers.re(
            r"the mock server is started"
            r" with interaction (?P<iid>\d+)"
            r" but with the following changes?:\n(?P<content>.*)",
            re.DOTALL,
        ),
        converters={"iid": int, "content": parse_markdown_table},
        target_fixture="srv",
        stacklevel=stacklevel + 1,
    )
    def _(
        iid: int,
        interaction_definitions: dict[int, InteractionDefinition],
        content: list[dict[str, str]],
    ) -> Generator[PactServer, Any, None]:
        """The mock server is started with interactions."""
        pact = Pact("consumer", "provider")
        pact.with_specification(version)
        definition = interaction_definitions[iid]
        definition.update(**content[0])
        logging.info("Adding modified interaction %s", iid)
        definition.add_to_pact(pact, f"interaction {iid}")

        with pact.serve(raises=False) as srv:
            yield srv


def request_n_is_made_to_the_mock_server(stacklevel: int = 1) -> None:
    @when(
        parsers.re(
            r"request (?P<request_id>\d+) is made to the mock server",
        ),
        converters={"request_id": int},
        target_fixture="response",
        stacklevel=stacklevel + 1,
    )
    def _(
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
                URL.build(query_string=definition.query).query
                if definition.query
                else None
            ),
            headers=definition.headers if definition.headers else None,  # type: ignore[arg-type]
            data=definition.body.bytes if definition.body else None,
            timeout=5,
        )


def request_n_is_made_to_the_mock_server_with_the_following_changes(
    stacklevel: int = 1,
) -> None:
    @when(
        parsers.re(
            r"request (?P<request_id>\d+) is made to the mock server"
            r" with the following changes?:\n(?P<content>.*)",
            re.DOTALL,
        ),
        converters={"request_id": int, "content": parse_markdown_table},
        target_fixture="response",
        stacklevel=stacklevel + 1,
    )
    def _(
        interaction_definitions: dict[int, InteractionDefinition],
        request_id: int,
        content: list[dict[str, str]],
        srv: PactServer,
    ) -> requests.Response:
        """
        Request n is made to the mock server with changes.

        The content is a markdown table with a subset of the columns defining the
        definition (as in the given step).
        """
        definition = interaction_definitions[request_id]
        assert len(content) == 1, "Expected exactly one row in the table"
        definition.update(**content[0])

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
                URL.build(query_string=definition.query).query
                if definition.query
                else None
            ),
            headers=definition.headers if definition.headers else None,  # type: ignore[arg-type]
            data=definition.body.bytes if definition.body else None,
            timeout=5,
        )


def the_pact_test_is_done(stacklevel: int = 1) -> None:
    @when("the pact test is done", stacklevel=stacklevel + 1)
    def _() -> None:
        """
        The pact test is done.
        """


def the_pact_file_for_the_test_is_generated(stacklevel: int = 1) -> None:
    @when(
        "the Pact file for the test is generated",
        target_fixture="pact_data",
        stacklevel=stacklevel + 1,
    )
    def _(
        temp_dir: Path,
        pact_interaction: PactInteractionTuple[Any],
    ) -> dict[str, Any]:
        """The Pact file for the test is generated."""
        pact_interaction.pact.write_file(temp_dir)
        with (temp_dir / "consumer-provider.json").open("r") as file:
            return json.load(file)


################################################################################
## Then
################################################################################


def a_response_is_returned(stacklevel: int = 1) -> None:
    @then(
        parsers.re(
            r"a (?P<code>\d+) (success|error) response is returned",
        ),
        converters={"code": int},
        stacklevel=stacklevel + 1,
    )
    def _(
        response: requests.Response,
        code: int,
        srv: PactServer,
    ) -> None:
        """
        A response is returned.
        """
        logging.info(
            "Request Information:\n%s",
            json.dumps(
                {
                    "method": response.request.method,
                    "url": response.request.url,
                    "headers": dict(**response.request.headers),
                    "body": truncate(response.request.body)
                    if response.request.body
                    else None,
                },
                indent=2,
            ),
        )
        logging.info("Mismatches:\n%s", json.dumps(srv.mismatches, indent=2))
        assert response.status_code == code


def the_payload_will_contain_the_json_document(stacklevel: int = 1) -> None:
    @then(
        parsers.re(
            r'the payload will contain the "(?P<file>[^"]+)" JSON document',
        ),
        stacklevel=stacklevel + 1,
    )
    def _(
        response: requests.Response,
        file: str,
    ) -> None:
        """
        The payload will contain the JSON document.
        """
        path = FIXTURES_ROOT / f"{file}.json"
        assert response.json() == json.loads(path.read_text())


def the_content_type_will_be_set_as(stacklevel: int = 1) -> None:
    @then(
        parsers.re(
            r'the content type will be set as "(?P<content_type>[^"]+)"',
        ),
        stacklevel=stacklevel + 1,
    )
    def _(
        response: requests.Response,
        content_type: str,
    ) -> None:
        assert response.headers["Content-Type"] == content_type


def the_mock_server_status_will_be(stacklevel: int = 1) -> None:
    @then(
        parsers.re(r"the mock server status will (?P<negated>(NOT )?)be OK"),
        converters={"negated": lambda s: s == "NOT "},
        stacklevel=stacklevel + 1,
    )
    def _(
        srv: PactServer,
        negated: bool,  # noqa: FBT001
    ) -> None:
        """
        The mock server status will be.
        """
        assert srv.matched is not negated


def the_mock_server_status_will_be_an_expected_but_not_received_error_for_interaction_n(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            r"the mock server status will be"
            r" an expected but not received error"
            r" for interaction \{(?P<n>\d+)\}",
        ),
        converters={"n": int},
        stacklevel=stacklevel + 1,
    )
    def _(
        srv: PactServer,
        n: int,
        interaction_definitions: dict[int, InteractionDefinition],
    ) -> None:
        """
        The mock server status will be an expected but not received error.
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


def the_mock_server_status_will_be_an_unexpected_request_received_for_interaction_n(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            r"the mock server status will be"
            r' an unexpected "(?P<method>[^"]+)" request received error'
            r" for interaction \{(?P<n>\d+)\}",
        ),
        converters={"n": int},
        stacklevel=stacklevel + 1,
    )
    def _(
        srv: PactServer,
        method: str,
        n: int,
        interaction_definitions: dict[int, InteractionDefinition],
    ) -> None:
        """
        The mock server status will be an expected but not received error.
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


def the_mock_server_status_will_be_an_unexpected_request_received_for_path(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            r"the mock server status will be"
            r' an unexpected "(?P<method>[^"]+)" request received error'
            r' for path "(?P<path>[^"]+)"',
        ),
        converters={"n": int},
        stacklevel=stacklevel + 1,
    )
    def _(
        srv: PactServer,
        method: str,
        path: str,
    ) -> None:
        """
        The mock server status will be an expected but not received.
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


def the_mock_server_status_will_be_mismatches(stacklevel: int = 1) -> None:
    @then(
        "the mock server status will be mismatches",
        stacklevel=stacklevel + 1,
    )
    def _(
        srv: PactServer,
    ) -> None:
        """
        The mock server status will be mismatches.
        """
        assert srv.matched is False
        assert len(srv.mismatches) > 0


def the_mismatches_will_contain_a_mismatch_with_the_error(stacklevel: int = 1) -> None:
    @then(
        parsers.re(
            r'the mismatches will contain a "(?P<mismatch_type>[^"]+)" mismatch'
            r' with error "(?P<error>[^"]+)"',
        ),
        stacklevel=stacklevel + 1,
    )
    def _(
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


def the_mismatches_will_contain_a_mismatch_with_path_with_the_error(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            r'the mismatches will contain a "(?P<mismatch_type>[^"]+)" mismatch'
            r' with path "(?P<path>[^"]+)"'
            r' with error "(?P<error>[^"]+)"',
        ),
        stacklevel=stacklevel + 1,
    )
    def _(
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


def the_mock_server_will_write_out_a_pact_file_for_the_interaction_when_done(
    stacklevel: int = 1,
) -> None:
    @then(
        parsers.re(
            r"the mock server will (?P<negated>(NOT )?)write out"
            r" a Pact file for the interactions? when done",
        ),
        converters={"negated": lambda s: s == "NOT "},
        target_fixture="pact_file",
        stacklevel=stacklevel + 1,
    )
    def _(
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


def the_pact_file_will_contain_n_interactions(stacklevel: int = 1) -> None:
    @then(
        parsers.re(r"the pact file will contain \{(?P<n>\d+)\} interactions?"),
        converters={"n": int},
        stacklevel=stacklevel + 1,
    )
    def _(
        pact_file: dict[str, Any],
        n: int,
    ) -> None:
        """
        The pact file will contain n interactions.
        """
        assert len(pact_file["interactions"]) == n


def the_nth_interaction_will_contain_the_document(stacklevel: int = 1) -> None:
    @then(
        parsers.re(
            r"the \{(?P<n>\w+)\} interaction response"
            r' will contain the "(?P<file>[^"]+)" document',
        ),
        converters={"n": string_to_int},
        stacklevel=stacklevel + 1,
    )
    def _(
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


def the_nth_interaction_request_will_be_for_method(stacklevel: int = 1) -> None:
    @then(
        parsers.re(
            r"the \{(?P<n>\w+)\} interaction request"
            r' will be for a "(?P<method>[A-Z]+)"',
        ),
        converters={"n": string_to_int},
        stacklevel=stacklevel + 1,
    )
    def _(
        pact_file: dict[str, Any],
        n: int,
        method: str,
    ) -> None:
        """
        The nth interaction request will be for a method.
        """
        assert pact_file["interactions"][n - 1]["request"]["method"] == method


def the_nth_interaction_request_query_parameters_will_be(stacklevel: int = 1) -> None:
    @then(
        parsers.re(
            r"the \{(?P<n>\w+)\} interaction request"
            r' query parameters will be "(?P<query>[^"]+)"',
        ),
        converters={"n": string_to_int},
        stacklevel=stacklevel + 1,
    )
    def _(
        pact_file: dict[str, Any],
        n: int,
        query: str,
    ) -> None:
        """
        The nth interaction request query parameters will be.
        """
        assert query == pact_file["interactions"][n - 1]["request"]["query"]


def the_nth_interaction_request_will_contain_the_header(stacklevel: int = 1) -> None:
    @then(
        parsers.re(
            r"the \{(?P<n>\w+)\} interaction request"
            r' will contain the header "(?P<key>[^"]+)"'
            r' with value "(?P<value>[^"]+)"',
        ),
        converters={"n": string_to_int},
        stacklevel=stacklevel + 1,
    )
    def _(
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


def the_nth_interaction_request_content_type_will_be(stacklevel: int = 1) -> None:
    @then(
        parsers.re(
            r"the \{(?P<n>\w+)\} interaction request"
            r' content type will be "(?P<content_type>[^"]+)"',
        ),
        converters={"n": string_to_int},
        stacklevel=stacklevel + 1,
    )
    def _(
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


def the_nth_interaction_request_will_contain_the_document(stacklevel: int = 1) -> None:
    @then(
        parsers.re(
            r"the \{(?P<n>\w+)\} interaction request"
            r' will contain the "(?P<file>[^"]+)" document',
        ),
        converters={"n": string_to_int},
        stacklevel=stacklevel + 1,
    )
    def _(
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
                pact_file["interactions"][n - 1]["request"]["body"]
                == file_path.read_text()
            )
