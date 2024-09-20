"""V3 Message provider feature tests."""

from __future__ import annotations

import json
import logging
import pickle
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pytest_bdd import (
    given,
    parsers,
    scenario,
)

from pact.v3.pact import Pact
from tests.v3.compatibility_suite.util import (
    parse_horizontal_markdown_table,
    parse_markdown_table,
)
from tests.v3.compatibility_suite.util.interaction_definition import (
    InteractionDefinition,
    InteractionState,
)
from tests.v3.compatibility_suite.util.provider import (
    a_pact_file_for_message_is_to_be_verified,
    a_provider_is_started_that_can_generate_the_message,
    a_provider_state_callback_is_configured,
    start_provider,
    the_provider_state_callback_will_be_called_after_the_verification_is_run,
    the_provider_state_callback_will_be_called_before_the_verification_is_run,
    the_provider_state_callback_will_receive_a_setup_call,
    the_verification_is_run,
    the_verification_results_will_contain_a_error,
    the_verification_will_be_successful,
)

if TYPE_CHECKING:
    from collections.abc import Generator

    from yarl import URL

    from pact.v3.verifier import Verifier

TEST_PACT_FILE_DIRECTORY = Path(Path(__file__).parent / "pacts")

logger = logging.getLogger(__name__)


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Incorrect message is generated by the provider",
)
def test_incorrect_message_is_generated_by_the_provider() -> None:
    """Incorrect message is generated by the provider."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Message with JSON body (negative case)",
)
def test_message_with_json_body_negative_case() -> None:
    """Message with JSON body (negative case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Message with JSON body (positive case)",
)
def test_message_with_json_body_positive_case() -> None:
    """Message with JSON body (positive case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Message with XML body (negative case)",
)
def test_message_with_xml_body_negative_case() -> None:
    """Message with XML body (negative case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Message with XML body (positive case)",
)
def test_message_with_xml_body_positive_case() -> None:
    """Message with XML body (positive case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Message with binary body (negative case)",
)
def test_message_with_binary_body_negative_case() -> None:
    """Message with binary body (negative case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Message with binary body (positive case)",
)
def test_message_with_binary_body_positive_case() -> None:
    """Message with binary body (positive case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Message with plain text body (negative case)",
)
def test_message_with_plain_text_body_negative_case() -> None:
    """Message with plain text body (negative case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Message with plain text body (positive case)",
)
def test_message_with_plain_text_body_positive_case() -> None:
    """Message with plain text body (positive case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Supports matching rules for the message body (negative case)",
)
def test_supports_matching_rules_for_the_message_body_negative_case() -> None:
    """Supports matching rules for the message body (negative case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Supports matching rules for the message body (positive case)",
)
def test_supports_matching_rules_for_the_message_body_positive_case() -> None:
    """Supports matching rules for the message body (positive case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Supports matching rules for the message metadata (negative case)",
)
def test_supports_matching_rules_for_the_message_metadata_negative_case() -> None:
    """Supports matching rules for the message metadata (negative case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Supports matching rules for the message metadata (positive case)",
)
def test_supports_matching_rules_for_the_message_metadata_positive_case() -> None:
    """Supports matching rules for the message metadata (positive case)."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@pytest.mark.skip("Currently unable to implement")
@scenario(
    "definition/features/V3/message_provider.feature",
    "Supports messages with body formatted for the Kafka schema registry",
)
def test_supports_messages_with_body_formatted_for_the_kafka_schema_registry() -> None:
    """Supports messages with body formatted for the Kafka schema registry."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Verifies the message metadata",
)
def test_verifies_the_message_metadata() -> None:
    """Verifies the message metadata."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Verifying a simple message",
)
def test_verifying_a_simple_message() -> None:
    """Verifying a simple message."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Verifying an interaction with a defined provider state",
)
def test_verifying_an_interaction_with_a_defined_provider_state() -> None:
    """Verifying an interaction with a defined provider state."""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="See pact-foundation/pact-python#639",
)
@scenario(
    "definition/features/V3/message_provider.feature",
    "Verifying multiple Pact files",
)
def test_verifying_multiple_pact_files() -> None:
    """Verifying multiple Pact files."""


################################################################################
## Given
################################################################################


a_provider_is_started_that_can_generate_the_message()
a_provider_state_callback_is_configured()
a_pact_file_for_message_is_to_be_verified("V3")


@given(
    parsers.re(
        r'a Pact file for "(?P<name>[^"]+)" is to be verified with the following:\n'
        r"(?P<table>.+)",
        re.DOTALL,
    ),
    converters={"table": parse_horizontal_markdown_table},
)
def a_pact_file_for_is_to_be_verified_with_the_following(
    verifier: Verifier,
    temp_dir: Path,
    name: str,
    table: dict[str, str | dict[str, str]],
) -> None:
    """
    A Pact file for "basic" is to be verified with the following.
    """
    pact = Pact("consumer", "provider")
    pact.with_specification("V3")

    if "metadata" in table:
        assert isinstance(table["metadata"], str)
        metadata = {
            k: json.loads(v.replace("JSON: ", "")) if v.startswith("JSON: ") else v
            for k, _, v in (s.partition("=") for s in table["metadata"].split("; "))
        }
        table["metadata"] = metadata

    interaction_definition = InteractionDefinition(
        type="Async",
        description=name,
        **table,  # type: ignore[arg-type]
    )
    interaction_definition.add_to_pact(pact, name)
    (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
    pact.write_file(temp_dir / "pacts")
    verifier.add_source(temp_dir / "pacts")


@given(
    parsers.re(
        r'a Pact file for "(?P<name>[^"]+)":"(?P<fixture>[^"]+)"'
        r' is to be verified with provider state "(?P<provider_state>[^"]+)"'
    )
)
def a_pact_file_for_is_to_be_verified_with_provider_state(
    temp_dir: Path,
    verifier: Verifier,
    name: str,
    fixture: str,
    provider_state: str,
) -> None:
    """A Pact file is to be verified with provider state."""
    pact = Pact("consumer", "provider")
    pact.with_specification("V3")
    interaction_definition = InteractionDefinition(
        type="Async",
        description=name,
        body=fixture,
    )
    interaction_definition.states = [InteractionState(provider_state)]
    interaction_definition.add_to_pact(pact, name)
    (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
    pact.write_file(temp_dir / "pacts")
    verifier.add_source(temp_dir / "pacts")
    with (temp_dir / "provider_states").open("w") as f:
        logger.debug("Writing provider state to %s", temp_dir / "provider_states")
        json.dump([s.as_dict() for s in [InteractionState(provider_state)]], f)


@given(
    parsers.re(
        r'a Pact file for "(?P<name>[^"]+)":"(?P<fixture>[^"]+)" is '
        "to be verified with the following metadata:\n"
        r"(?P<metadata>.+)",
        re.DOTALL,
    ),
    converters={"metadata": parse_markdown_table},
)
def a_pact_file_for_is_to_be_verified_with_the_following_metadata(
    temp_dir: Path,
    verifier: Verifier,
    name: str,
    fixture: str,
    metadata: list[dict[str, str]],
) -> None:
    """A Pact file is to be verified with the following metadata."""
    pact = Pact("consumer", "provider")
    pact.with_specification("V3")
    interaction_definition = InteractionDefinition(
        type="Async",
        description=name,
        body=fixture,
        metadata={
            row["key"]: json.loads(row["value"].replace("JSON: ", ""))
            if row["value"].startswith("JSON: ")
            else row["value"]
            for row in metadata
        },
    )
    interaction_definition.add_to_pact(pact, name)
    (temp_dir / "pacts").mkdir(exist_ok=True, parents=True)
    pact.write_file(temp_dir / "pacts")
    verifier.add_source(temp_dir / "pacts")


@given(
    parsers.re(
        r'a provider is started that can generate the "(?P<name>[^"]+)" '
        r'message with "(?P<fixture>[^"]+)" and the following metadata:\n'
        r"(?P<metadata>.+)",
        re.DOTALL,
    ),
    converters={"metadata": parse_markdown_table},
    target_fixture="provider_url",
)
def a_provider_is_started_that_can_generate_the_message_with_the_following_metadata(
    temp_dir: Path,
    name: str,
    fixture: str,
    metadata: list[dict[str, str]],
) -> Generator[URL, None, None]:
    """A provider is started that can generate the message with the following metadata."""  # noqa: E501
    interaction_definitions: list[InteractionDefinition] = []
    if (temp_dir / "interactions.pkl").exists():
        with (temp_dir / "interactions.pkl").open("rb") as pkl_file:
            interaction_definitions = pickle.load(pkl_file)  # noqa: S301

    interaction_definition = InteractionDefinition(
        type="Async",
        description=name,
        body=fixture,
        metadata={
            row["key"]: json.loads(row["value"].replace("JSON: ", ""))
            if row["value"].startswith("JSON: ")
            else row["value"]
            for row in metadata
        },
    )
    interaction_definitions.append(interaction_definition)

    with (temp_dir / "interactions.pkl").open("wb") as pkl_file:
        pickle.dump(interaction_definitions, pkl_file)

    yield from start_provider(temp_dir)


################################################################################
## When
################################################################################


the_verification_is_run()


################################################################################
## Then
################################################################################


the_provider_state_callback_will_be_called_before_the_verification_is_run()
the_provider_state_callback_will_be_called_after_the_verification_is_run()
the_provider_state_callback_will_receive_a_setup_call()
the_verification_will_be_successful()
the_verification_results_will_contain_a_error()
