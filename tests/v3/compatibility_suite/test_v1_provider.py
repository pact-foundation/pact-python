"""
Basic HTTP provider feature test.
"""

from __future__ import annotations

import copy
import json
import logging
import pickle
import re
import signal
import subprocess
import sys
import time
from pathlib import Path
from threading import Thread
from typing import Any, Generator, NoReturn

import pytest
import requests
from pytest_bdd import given, parsers, scenario, then, when
from testcontainers.compose import DockerCompose  # type: ignore[import-untyped]
from yarl import URL

from pact.v3.pact import Pact
from pact.v3.verifier import Verifier
from tests.v3.compatibility_suite.util import (
    InteractionDefinition,
    parse_headers,
    parse_markdown_table,
)
from tests.v3.compatibility_suite.util.provider import PactBroker

logger = logging.getLogger(__name__)


@pytest.fixture()
def verifier() -> Verifier:
    """Return a new Verifier."""
    return Verifier()


################################################################################
## Scenario
################################################################################


@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying a simple HTTP request",
)
def test_verifying_a_simple_http_request() -> None:
    """Verifying a simple HTTP request."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying multiple Pact files",
)
def test_verifying_multiple_pact_files() -> None:
    """Verifying multiple Pact files."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Incorrect request is made to provider",
)
def test_incorrect_request_is_made_to_provider() -> None:
    """Incorrect request is made to provider."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying a simple HTTP request via a Pact broker",
)
def test_verifying_a_simple_http_request_via_a_pact_broker() -> None:
    """Verifying a simple HTTP request via a Pact broker."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying a simple HTTP request via a Pact broker with publishing results enabled",
)
def test_verifying_a_simple_http_request_via_a_pact_broker_with_publishing() -> None:
    """Verifying a simple HTTP request via a Pact broker with publishing."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying multiple Pact files via a Pact broker",
)
def test_verifying_multiple_pact_files_via_a_pact_broker() -> None:
    """Verifying multiple Pact files via a Pact broker."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Incorrect request is made to provider via a Pact broker",
)
def test_incorrect_request_is_made_to_provider_via_a_pact_broker() -> None:
    """Incorrect request is made to provider via a Pact broker."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying an interaction with a defined provider state",
)
def test_verifying_an_interaction_with_a_defined_provider_state() -> None:
    """Verifying an interaction with a defined provider state."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying an interaction with no defined provider state",
)
def test_verifying_an_interaction_with_no_defined_provider_state() -> None:
    """Verifying an interaction with no defined provider state."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying an interaction where the provider state callback fails",
)
def test_verifying_an_interaction_where_the_provider_state_callback_fails() -> None:
    """Verifying an interaction where the provider state callback fails."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying an interaction where a provider state callback is not configured",
)
def test_verifying_an_interaction_where_no_provider_state_callback_configured() -> None:
    """Verifying an interaction where a provider state callback is not configured."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifying a HTTP request with a request filter configured",
)
def test_verifying_a_http_request_with_a_request_filter_configured() -> None:
    """Verifying a HTTP request with a request filter configured."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifies the response status code",
)
def test_verifies_the_response_status_code() -> None:
    """Verifies the response status code."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Verifies the response headers",
)
def test_verifies_the_response_headers() -> None:
    """Verifies the response headers."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with plain text body (positive case)",
)
def test_response_with_plain_text_body_positive_case() -> None:
    """Response with plain text body (positive case)."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with plain text body (negative case)",
)
def test_response_with_plain_text_body_negative_case() -> None:
    """Response with plain text body (negative case)."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with JSON body (positive case)",
)
def test_response_with_json_body_positive_case() -> None:
    """Response with JSON body (positive case)."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with JSON body (negative case)",
)
def test_response_with_json_body_negative_case() -> None:
    """Response with JSON body (negative case)."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with XML body (positive case)",
)
def test_response_with_xml_body_positive_case() -> None:
    """Response with XML body (positive case)."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with XML body (negative case)",
)
def test_response_with_xml_body_negative_case() -> None:
    """Response with XML body (negative case)."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with binary body (positive case)",
)
def test_response_with_binary_body_positive_case() -> None:
    """Response with binary body (positive case)."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with binary body (negative case)",
)
def test_response_with_binary_body_negative_case() -> None:
    """Response with binary body (negative case)."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with form post body (positive case)",
)
def test_response_with_form_post_body_positive_case() -> None:
    """Response with form post body (positive case)."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with form post body (negative case)",
)
def test_response_with_form_post_body_negative_case() -> None:
    """Response with form post body (negative case)."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with multipart body (positive case)",
)
def test_response_with_multipart_body_positive_case() -> None:
    """Response with multipart body (positive case)."""


@scenario(
    "definition/features/V1/http_provider.feature",
    "Response with multipart body (negative case)",
)
def test_response_with_multipart_body_negative_case() -> None:
    """Response with multipart body (negative case)."""


################################################################################
## Given
################################################################################


@given(
    parsers.parse("the following HTTP interactions have been defined:\n{content}"),
    target_fixture="interaction_definitions",
    converters={"content": parse_markdown_table},
)
def the_following_http_interactions_have_been_defined(
    content: list[dict[str, str]],
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
    - response headers
    - response content
    - response body

    The first row is ignored, as it is assumed to be the column headers. The
    order of the columns is similarly ignored.
    """
    logger.debug("Parsing interaction definitions")

    # Check that the table is well-formed
    assert len(content[0]) == 10, f"Expected 10 columns, got {len(content[0])}"
    assert "No" in content[0], "'No' column not found"

    # Parse the table into a more useful format
    interactions: dict[int, InteractionDefinition] = {}
    for row in content:
        interactions[int(row["No"])] = InteractionDefinition(**row)
    return interactions


@given(
    parsers.re(
        r"a provider is started that returns the responses? "
        r'from interactions? "?(?P<interactions>[0-9, ]+)"?',
    ),
    converters={"interactions": lambda x: [int(i) for i in x.split(",") if i]},
    target_fixture="provider_url",
)
def a_provider_is_started_that_returns_the_responses_from_interactions(
    interaction_definitions: dict[int, InteractionDefinition],
    interactions: list[int],
    temp_dir: Path,
) -> Generator[URL, None, None]:
    """
    Start a provider that returns the responses from the given interactions.
    """
    logger.debug("Starting provider for interactions %s", interactions)

    for i in interactions:
        logger.debug("Interaction %d: %s", i, interaction_definitions[i])

    with (temp_dir / "interactions.pkl").open("wb") as pkl_file:
        pickle.dump([interaction_definitions[i] for i in interactions], pkl_file)

    yield from start_provider(temp_dir)


@given(
    parsers.re(
        r"a provider is started that returns the responses?"
        r' from interactions? "?(?P<interactions>[0-9, ]+)"?'
        r" with the following changes:\n(?P<changes>.+)",
        re.DOTALL,
    ),
    converters={
        "interactions": lambda x: [int(i) for i in x.split(",") if i],
        "changes": parse_markdown_table,
    },
    target_fixture="provider_url",
)
def a_provider_is_started_that_returns_the_responses_from_interactions_with_changes(
    interaction_definitions: dict[int, InteractionDefinition],
    interactions: list[int],
    changes: list[dict[str, str]],
    temp_dir: Path,
) -> Generator[URL, None, None]:
    """
    Start a provider that returns the responses from the given interactions.
    """
    logger.debug("Starting provider for interactions %s", interactions)

    assert len(changes) == 1, "Only one set of changes is supported"
    defns: list[InteractionDefinition] = []
    for interaction in interactions:
        defn = copy.deepcopy(interaction_definitions[interaction])
        defn.update(**changes[0])
        defns.append(defn)
        logger.debug(
            "Update interaction %d: %s",
            interaction,
            defn,
        )

    with (temp_dir / "interactions.pkl").open("wb") as pkl_file:
        pickle.dump(defns, pkl_file)

    yield from start_provider(temp_dir)


def start_provider(provider_dir: str | Path) -> Generator[URL, None, None]:  # noqa: C901
    """Start the provider app with the given interactions."""
    process = subprocess.Popen(
        [  # noqa: S603
            sys.executable,
            Path(__file__).parent / "util" / "provider.py",
            str(provider_dir),
        ],
        cwd=Path.cwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )

    pattern = re.compile(r" \* Running on (?P<url>[^ ]+)")
    while True:
        if process.poll() is not None:
            logger.error("Provider process exited with code %d", process.returncode)
            logger.error(
                "Provider stdout: %s", process.stdout.read() if process.stdout else ""
            )
            logger.error(
                "Provider stderr: %s", process.stderr.read() if process.stderr else ""
            )
            msg = f"Provider process exited with code {process.returncode}"
            raise RuntimeError(msg)
        if (
            process.stderr
            and (line := process.stderr.readline())
            and (match := pattern.match(line))
        ):
            break
        time.sleep(0.1)

    url = URL(match.group("url"))
    logger.debug("Provider started on %s", url)
    for _ in range(50):
        try:
            response = requests.get(str(url / "_test" / "ping"), timeout=1)
            assert response.text == "pong"
            break
        except (requests.RequestException, AssertionError):
            time.sleep(0.1)
            continue
    else:
        msg = "Failed to ping provider"
        raise RuntimeError(msg)

    def redirect() -> NoReturn:
        while True:
            if process.stdout:
                while line := process.stdout.readline():
                    logger.debug("Provider stdout: %s", line.strip())
            if process.stderr:
                while line := process.stderr.readline():
                    logger.debug("Provider stderr: %s", line.strip())

    thread = Thread(target=redirect, daemon=True)
    thread.start()

    yield url

    process.send_signal(signal.SIGINT)


@given(
    parsers.re(
        r"a Pact file for interaction (?P<interaction>\d+) is to be verified",
    ),
    converters={"interaction": int},
)
def a_pact_file_for_interaction_is_to_be_verified(
    interaction_definitions: dict[int, InteractionDefinition],
    verifier: Verifier,
    interaction: int,
    temp_dir: Path,
) -> None:
    """
    Verify the Pact file for the given interaction.
    """
    logger.debug(
        "Adding interaction %d to be verified: %s",
        interaction,
        interaction_definitions[interaction],
    )

    defn = interaction_definitions[interaction]

    pact = Pact("consumer", "provider")
    pact.with_specification("V1")
    defn.add_to_pact(pact, f"interaction {interaction}")
    (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
    pact.write_file(temp_dir / "pacts")

    verifier.add_source(temp_dir / "pacts")


@given(
    parsers.re(
        r"a Pact file for interaction (?P<interaction>\d+)"
        r" is to be verified from a Pact broker",
    ),
    converters={"interaction": int},
    target_fixture="pact_broker",
)
def a_pact_file_for_interaction_is_to_be_verified_from_a_pact_broker(
    interaction_definitions: dict[int, InteractionDefinition],
    verifier: Verifier,
    interaction: int,
    temp_dir: Path,
) -> Generator[PactBroker, None, None]:
    """
    Verify the Pact file for the given interaction from a Pact broker.
    """
    logger.debug("Adding interaction %d to be verified from a Pact broker", interaction)

    defn = interaction_definitions[interaction]

    pact = Pact("consumer", "provider")
    pact.with_specification("V1")
    defn.add_to_pact(pact, f"interaction {interaction}")

    pacts_dir = temp_dir / "pacts"
    pacts_dir.mkdir(exist_ok=True, parents=True)
    pact.write_file(pacts_dir)

    with DockerCompose(
        Path(__file__).parent / "util",
        compose_file_name="pact-broker.yml",
        pull=True,
    ) as _:
        pact_broker = PactBroker(URL("http://pactbroker:pactbroker@localhost:9292"))
        pact_broker.publish(pacts_dir)
        verifier.broker_source(pact_broker.url)
        yield pact_broker


@given("publishing of verification results is enabled")
def publishing_of_verification_results_is_enabled(verifier: Verifier) -> None:
    """
    Enable publishing of verification results.
    """
    logger.debug("Publishing verification results")

    verifier.set_publish_options(
        "0.0.0",
    )


@given(
    parsers.re(
        r"a provider state callback is configured"
        r"(?P<failure>(, but will return a failure)?)",
    ),
    converters={"failure": lambda x: x != ""},
)
def a_provider_state_callback_is_configured(
    verifier: Verifier,
    provider_url: URL,
    temp_dir: Path,
    failure: bool,  # noqa: FBT001
) -> None:
    """
    Configure a provider state callback.
    """
    logger.debug("Configuring provider state callback")

    if failure:
        with (temp_dir / "fail_callback").open("w") as f:
            f.write("true")

    verifier.set_state(
        provider_url / "_test" / "callback",
        teardown=True,
    )


@given(
    parsers.re(
        r"a Pact file for interaction (?P<interaction>\d+) is to be verified"
        r' with a provider state "(?P<state>[^"]+)" defined',
    ),
    converters={"interaction": int},
)
def a_pact_file_for_interaction_is_to_be_verified_with_a_provider_state_define(
    interaction_definitions: dict[int, InteractionDefinition],
    verifier: Verifier,
    interaction: int,
    state: str,
    temp_dir: Path,
) -> None:
    """
    Verify the Pact file for the given interaction with a provider state defined.
    """
    logger.debug(
        "Adding interaction %d to be verified with provider state %s",
        interaction,
        state,
    )

    defn = interaction_definitions[interaction]
    defn.state = state

    pact = Pact("consumer", "provider")
    pact.with_specification("V1")
    defn.add_to_pact(pact, f"interaction {interaction}")
    (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
    pact.write_file(temp_dir / "pacts")

    verifier.add_source(temp_dir / "pacts")

    with (temp_dir / "provider_state").open("w") as f:
        logger.debug("Writing provider state to %s", temp_dir / "provider_state")
        f.write(state)


@given(
    parsers.parse(
        "a request filter is configured to make the following changes:\n{content}"
    ),
    converters={"content": parse_markdown_table},
)
def a_request_filter_is_configured_to_make_the_following_changes(
    content: list[dict[str, str]],
    verifier: Verifier,
) -> None:
    """
    Configure a request filter to make the given changes.
    """
    logger.debug("Configuring request filter")

    if "headers" in content[0]:
        verifier.add_custom_headers(parse_headers(content[0]["headers"]).items())
    else:
        msg = "Unsupported filter type"
        raise RuntimeError(msg)


################################################################################
## When
################################################################################


@when("the verification is run", target_fixture="verifier_result")
def the_verification_is_run(
    verifier: Verifier,
    provider_url: URL,
) -> tuple[Verifier, Exception | None]:
    """
    Run the verification.
    """
    logger.debug("Running verification on %r", verifier)

    verifier.set_info("provider", url=provider_url)
    try:
        verifier.verify()
    except Exception as e:  # noqa: BLE001
        return verifier, e
    return verifier, None


################################################################################
## Then
################################################################################


@then(
    parsers.re(r"the verification will(?P<negated>( NOT)?) be successful"),
    converters={"negated": lambda x: x == " NOT"},
)
def the_verification_will_be_successful(
    verifier_result: tuple[Verifier, Exception | None],
    negated: bool,  # noqa: FBT001
) -> None:
    """
    Check that the verification was successful.
    """
    logger.debug("Checking verification result")
    logger.debug("Verifier result: %s", verifier_result)

    if negated:
        assert verifier_result[1] is not None
    else:
        assert verifier_result[1] is None


@then(
    parsers.re(r'the verification results will contain a "(?P<error>[^"]+)" error'),
)
def the_verification_results_will_contain_a_error(
    verifier_result: tuple[Verifier, Exception | None], error: str
) -> None:
    """
    Check that the verification results contain the given error.
    """
    logger.debug("Checking that verification results contain error %s", error)

    verifier = verifier_result[0]
    logger.debug("Verification results: %s", json.dumps(verifier.results, indent=2))

    if error == "Response status did not match":
        mismatch_type = "StatusMismatch"
    elif error == "Headers had differences":
        mismatch_type = "HeaderMismatch"
    elif error == "Body had differences":
        mismatch_type = "BodyMismatch"
    elif error == "State change request failed":
        assert "One or more of the setup state change handlers has failed" in [
            error["mismatch"]["message"] for error in verifier.results["errors"]
        ]
        return
    else:
        msg = f"Unknown error type: {error}"
        raise ValueError(msg)

    assert mismatch_type in [
        mismatch["type"]
        for error in verifier.results["errors"]
        for mismatch in error["mismatch"]["mismatches"]
    ]


@then(
    parsers.re(r"a verification result will NOT be published back"),
)
def a_verification_result_will_not_be_published_back(pact_broker: PactBroker) -> None:
    """
    Check that the verification result was published back to the Pact broker.
    """
    logger.debug("Checking that verification result was not published back")

    response = pact_broker.latest_verification_results()
    if response:
        with pytest.raises(requests.HTTPError, match="404 Client Error"):
            response.raise_for_status()


@then(
    parsers.re(
        "a successful verification result "
        "will be published back "
        r"for interaction \{(?P<interaction>\d+)\}",
    ),
    converters={"interaction": int},
)
def a_successful_verification_result_will_be_published_back(
    pact_broker: PactBroker,
    interaction: int,
) -> None:
    """
    Check that the verification result was published back to the Pact broker.
    """
    logger.debug(
        "Checking that verification result was published back for interaction %d",
        interaction,
    )

    interaction_id = pact_broker.interaction_id(interaction)
    response = pact_broker.latest_verification_results()
    assert response is not None
    assert response.ok
    data: dict[str, Any] = response.json()
    assert data["success"]

    for test_result in data["testResults"]:
        if test_result["interactionId"] == interaction_id:
            assert test_result["success"]
            break
    else:
        msg = f"Interaction {interaction} not found in verification results"
        raise ValueError(msg)


@then(
    parsers.re(
        "a failed verification result "
        "will be published back "
        r"for the interaction \{(?P<interaction>\d+)\}",
    ),
    converters={"interaction": int},
)
def a_failed_verification_result_will_be_published_back(
    pact_broker: PactBroker,
    interaction: int,
) -> None:
    """
    Check that the verification result was published back to the Pact broker.
    """
    logger.debug(
        "Checking that failed verification result"
        " was published back for interaction %d",
        interaction,
    )

    interaction_id = pact_broker.interaction_id(interaction)
    response = pact_broker.latest_verification_results()
    assert response is not None
    assert response.ok
    data: dict[str, Any] = response.json()
    assert not data["success"]

    for test_result in data["testResults"]:
        if test_result["interactionId"] == interaction_id:
            assert not test_result["success"]
            break
    else:
        msg = f"Interaction {interaction} not found in verification results"
        raise ValueError(msg)


@then("the provider state callback will be called before the verification is run")
def the_provider_state_callback_will_be_called_before_the_verification_is_run() -> None:
    """
    Check that the provider state callback was called before the verification was run.
    """
    logger.debug("Checking provider state callback was called before verification")


@then(
    parsers.re(
        r"the provider state callback will receive a (?P<action>setup|teardown) call"
        r' (with )?"(?P<state>[^"]*)" as the provider state parameter',
    ),
)
def the_provider_state_callback_will_receive_a_setup_call(
    temp_dir: Path,
    action: str,
    state: str,
) -> None:
    """
    Check that the provider state callback received a setup call.
    """
    logger.info("Checking provider state callback received a %s call", action)
    logger.info("Callback files: %s", list(temp_dir.glob("callback.*.json")))
    for file in temp_dir.glob("callback.*.json"):
        with file.open("r") as f:
            data: dict[str, Any] = json.load(f)
            logger.debug("Checking callback data: %s", data)
            if (
                "action" in data["query_params"]
                and data["query_params"]["action"] == action
                and data["query_params"]["state"] == state
            ):
                break
    else:
        msg = f"No {action} call found"
        raise AssertionError(msg)


@then(
    parsers.re(
        r"the provider state callback will "
        r"NOT receive a (?P<action>setup|teardown) call"
    )
)
def the_provider_state_callback_will_not_receive_a_setup_call(
    temp_dir: Path,
    action: str,
) -> None:
    """
    Check that the provider state callback did not receive a setup call.
    """
    for file in temp_dir.glob("callback.*.json"):
        with file.open("r") as f:
            data: dict[str, Any] = json.load(f)
            logger.debug("Checking callback data: %s", data)
            if (
                "action" in data["query_params"]
                and data["query_params"]["action"] == action
            ):
                msg = f"Unexpected {action} call found"
                raise AssertionError(msg)


@then("the provider state callback will be called after the verification is run")
def the_provider_state_callback_will_be_called_after_the_verification_is_run() -> None:
    """
    Check that the provider state callback was called after the verification was run.
    """


@then(
    parsers.re(
        r"a warning will be displayed "
        r"that there was no provider state callback configured "
        r'for provider state "(?P<state>[^"]*)"',
    )
)
def a_warning_will_be_displayed_that_there_was_no_callback_configured(
    state: str,
) -> None:
    """
    Check that a warning was displayed that there was no callback configured.
    """
    logger.debug("Checking for warning about missing provider state callback")
    assert state


@then(
    parsers.re(
        r'the request to the provider will contain the header "(?P<header>[^"]+)"',
    ),
    converters={"header": lambda x: parse_headers(f"'{x}'")},
)
def the_request_to_the_provider_will_contain_the_header(
    verifier_result: tuple[Verifier, Exception | None],
    header: dict[str, str],
    temp_dir: Path,
) -> None:
    """
    Check that the request to the provider contained the given header.
    """
    verifier = verifier_result[0]
    logger.debug("verifier output: %s", verifier.output(strip_ansi=True))
    logger.debug("verifier results: %s", json.dumps(verifier.results, indent=2))
    for request in temp_dir.glob("request.*.json"):
        with request.open("r") as f:
            data: dict[str, Any] = json.load(f)
            if data["path"].startswith("/_test"):
                continue
            logger.debug("Checking request data: %s", data)
            assert all([k, v] in data["headers_list"] for k, v in header.items())
            break
    else:
        msg = "No request found"
        raise AssertionError(msg)
