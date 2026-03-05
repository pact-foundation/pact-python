"""
Test the FFI interface.

Note that these tests are not intended to be exhaustive, as the full
functionality should be tested through the core Pact Python library.

Instead, these tests fall under two broad categories:

-  Tests that ensure the FFI interface is working correctly.
-  Tests that ensure some of the thin wrappers around the FFI interface
   are functioning as expected.
"""

from __future__ import annotations

import re

import pytest

import pact_ffi
from pact_ffi.ffi import lib


def test_version() -> None:
    assert isinstance(pact_ffi.version(), str)
    assert len(pact_ffi.version()) > 0
    assert pact_ffi.version().count(".") == 2


def test_string_result_ok() -> None:
    result = pact_ffi.StringResult(lib.pactffi_generate_datetime_string(b"yyyy"))
    assert result.is_ok
    assert not result.is_failed
    assert re.match(r"^\d{4}$", result.text)
    assert str(result) == result.text
    assert repr(result) == f"<StringResult: OK, {result.text!r}>"
    result.raise_exception()


def test_string_result_failed() -> None:
    result = pact_ffi.StringResult(lib.pactffi_generate_datetime_string(b"t"))
    assert not result.is_ok
    assert result.is_failed
    assert result.text.startswith("Error parsing")
    with pytest.raises(RuntimeError):
        result.raise_exception()


def test_datetime_valid() -> None:
    pact_ffi.validate_datetime("2023-01-01", "yyyy-MM-dd")


def test_datetime_invalid() -> None:
    with pytest.raises(ValueError, match=r"Invalid datetime value.*"):
        pact_ffi.validate_datetime("01/01/2023", "yyyy-MM-dd")


def test_get_error_message() -> None:
    # The first bit makes sure that an error is generated.
    invalid_utf8 = b"\xc3\x28"
    ret: int = lib.pactffi_validate_datetime(invalid_utf8, invalid_utf8)
    assert ret == 2
    assert pact_ffi.get_error_message() == "error parsing value as UTF-8"


def test_owned_string() -> None:
    string = pact_ffi.get_tls_ca_certificate()
    assert isinstance(string, str)
    assert len(string) > 0
    assert str(string) == string
    assert repr(string).startswith("<OwnedString: ")
    assert repr(string).endswith(">")
    assert string.startswith("-----BEGIN CERTIFICATE-----")
    assert string.endswith(
        (
            "-----END CERTIFICATE-----\n",
            "-----END CERTIFICATE-----\r\n",
        ),
    )


class TestInteractionIteration:
    """
    Test interaction iteration functionality.
    """

    @pytest.fixture
    def pact(self) -> pact_ffi.PactHandle:
        """Create a V4 pact for testing."""
        pact = pact_ffi.new_pact("consumer", "provider")
        pact_ffi.with_specification(pact, pact_ffi.PactSpecification.V4)
        return pact

    def test_interaction_iterator_repr(self, pact: pact_ffi.PactHandle) -> None:
        iterator = pact_ffi.pact_model_interaction_iterator(pact.pointer())
        assert str(iterator) == "PactInteractionIterator"
        assert repr(iterator).startswith("PactInteractionIterator(")

    def test_http_iterator_repr(self, pact: pact_ffi.PactHandle) -> None:
        iterator = pact_ffi.pact_handle_get_sync_http_iter(pact)
        assert str(iterator) == "PactSyncHttpIterator"
        assert repr(iterator).startswith("PactSyncHttpIterator(")

    def test_async_message_iterator_repr(self, pact: pact_ffi.PactHandle) -> None:
        iterator = pact_ffi.pact_handle_get_async_message_iter(pact)
        assert str(iterator) == "PactAsyncMessageIterator"
        assert repr(iterator).startswith("PactAsyncMessageIterator(")

    def test_sync_message_iterator_repr(self, pact: pact_ffi.PactHandle) -> None:
        iterator = pact_ffi.pact_handle_get_sync_message_iter(pact)
        assert str(iterator) == "PactSyncMessageIterator"
        assert repr(iterator).startswith("PactSyncMessageIterator(")

    def test_empty_iterators(self, pact: pact_ffi.PactHandle) -> None:
        inter_iter = pact_ffi.pact_model_interaction_iterator(pact.pointer())
        assert sum(1 for _ in inter_iter) == 0

        http_iterator = pact_ffi.pact_handle_get_sync_http_iter(pact)
        assert sum(1 for _ in http_iterator) == 0

        async_iterator = pact_ffi.pact_handle_get_async_message_iter(pact)
        assert sum(1 for _ in async_iterator) == 0

        sync_iterator = pact_ffi.pact_handle_get_sync_message_iter(pact)
        assert sum(1 for _ in sync_iterator) == 0

    def test_iterators(self, pact: pact_ffi.PactHandle) -> None:
        pact_ffi.new_interaction(pact, "http")
        pact_ffi.new_message_interaction(pact, "async")
        pact_ffi.new_sync_message_interaction(pact, "sync")

        # Test each iterator type
        interaction_iter = pact_ffi.pact_model_interaction_iterator(pact.pointer())
        assert sum(1 for _ in interaction_iter) == 3
        assert sum(1 for _ in interaction_iter) == 0  # exhausted

        http_iter = pact_ffi.pact_handle_get_sync_http_iter(pact)
        assert sum(1 for _ in http_iter) == 1
        assert sum(1 for _ in http_iter) == 0  # exhausted

        async_iter = pact_ffi.pact_handle_get_async_message_iter(pact)
        assert sum(1 for _ in async_iter) == 1
        assert sum(1 for _ in async_iter) == 0  # exhausted

        sync_iter = pact_ffi.pact_handle_get_sync_message_iter(pact)
        assert sum(1 for _ in sync_iter) == 1
        assert sum(1 for _ in sync_iter) == 0  # exhausted

    def test_iterator_types(self, pact: pact_ffi.PactHandle) -> None:
        pact_ffi.new_interaction(pact, "http")
        pact_ffi.new_message_interaction(pact, "async")
        pact_ffi.new_sync_message_interaction(pact, "sync")

        interaction_iter = pact_ffi.pact_model_interaction_iterator(pact.pointer())
        assert all(
            isinstance(interaction, pact_ffi.PactInteraction)
            for interaction in interaction_iter
        )

        http_iter = pact_ffi.pact_handle_get_sync_http_iter(pact)
        assert all(
            isinstance(interaction, pact_ffi.SynchronousHttp)
            for interaction in http_iter
        )

        async_iter = pact_ffi.pact_handle_get_async_message_iter(pact)
        assert all(
            isinstance(interaction, pact_ffi.AsynchronousMessage)
            for interaction in async_iter
        )

        sync_iter = pact_ffi.pact_handle_get_sync_message_iter(pact)
        assert all(
            isinstance(interaction, pact_ffi.SynchronousMessage)
            for interaction in sync_iter
        )


class TestPactModelHandle:
    """
    Test basic Pact model pointer handling.
    """

    @pytest.fixture
    def pact(self) -> pact_ffi.PactHandle:
        """Create a V4 pact for testing."""
        pact = pact_ffi.new_pact("consumer", "provider")
        pact_ffi.with_specification(pact, pact_ffi.PactSpecification.V4)
        return pact

    def test_pact_handle_repr(self, pact: pact_ffi.PactHandle) -> None:
        assert str(pact).startswith("PactHandle(")
        assert repr(pact).startswith("PactHandle(")

    def test_pact_repr(self, pact: pact_ffi.PactHandle) -> None:
        pact_model = pact_ffi.pact_handle_to_pointer(pact)

        assert isinstance(pact_model, pact_ffi.Pact)
        assert str(pact_model) == "Pact"
        assert repr(pact_model).startswith("Pact(")


class TestPactInteractionCasting:
    """
    Test casting interactions to specific subtypes via iterators.
    """

    @pytest.fixture
    def pact(self) -> pact_ffi.PactHandle:
        """Create a V4 pact for testing."""
        pact = pact_ffi.new_pact("consumer", "provider")
        pact_ffi.with_specification(pact, pact_ffi.PactSpecification.V4)
        return pact

    def test_synchronous_http_casting(self, pact: pact_ffi.PactHandle) -> None:
        """Test SynchronousHttp interaction casting and representation."""
        pact_ffi.new_interaction(pact, "http")

        # Test HTTP iterator yields SynchronousHttp
        interaction_iter = pact_ffi.pact_model_interaction_iterator(pact.pointer())
        interaction = next(interaction_iter)
        assert isinstance(interaction, pact_ffi.PactInteraction)
        http = interaction.as_synchronous_http()
        assert isinstance(http, pact_ffi.SynchronousHttp)

        with pytest.raises(TypeError):
            interaction.as_asynchronous_message()
        with pytest.raises(TypeError):
            interaction.as_synchronous_message()

    def test_asynchronous_message_casting(self, pact: pact_ffi.PactHandle) -> None:
        """Test AsynchronousMessage interaction casting and representation."""
        pact_ffi.new_message_interaction(pact, "async")

        # Test async message iterator yields AsynchronousMessage
        interaction_iter = pact_ffi.pact_model_interaction_iterator(pact.pointer())
        interaction = next(interaction_iter)
        assert isinstance(interaction, pact_ffi.PactInteraction)
        async_msg = interaction.as_asynchronous_message()
        assert isinstance(async_msg, pact_ffi.AsynchronousMessage)

        with pytest.raises(TypeError):
            interaction.as_synchronous_http()
        with pytest.raises(TypeError):
            interaction.as_synchronous_message()

    def test_synchronous_message_casting(self, pact: pact_ffi.PactHandle) -> None:
        """Test SynchronousMessage interaction casting and representation."""
        pact_ffi.new_sync_message_interaction(pact, "sync")

        # Test sync message iterator yields SynchronousMessage
        interaction_iter = pact_ffi.pact_model_interaction_iterator(pact.pointer())
        interaction = next(interaction_iter)
        assert isinstance(interaction, pact_ffi.PactInteraction)
        sync_msg = interaction.as_synchronous_message()
        assert isinstance(sync_msg, pact_ffi.SynchronousMessage)

        with pytest.raises(TypeError):
            interaction.as_synchronous_http()
        with pytest.raises(TypeError):
            interaction.as_asynchronous_message()
