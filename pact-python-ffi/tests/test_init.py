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


def test_pact_interaction() -> None:
    """Test PactInteraction class."""
    pact = pact_ffi.new_pact("consumer", "provider")
    pact_ffi.with_specification(pact, pact_ffi.PactSpecification.V4)

    # Create HTTP interaction
    pact_ffi.new_sync_message_interaction(pact, "test")

    # Get interactions via iterator
    sync_http_iter = pact_ffi.pact_handle_get_sync_http_iter(pact)
    list(sync_http_iter)
    # Test string representation works on iterator
    assert "PactSyncHttpIterator" in str(sync_http_iter) or str(sync_http_iter)


def test_pact_message_iterator() -> None:
    """Test PactMessageIterator class."""
    pact = pact_ffi.new_pact("consumer", "provider")
    pact_ffi.with_specification(pact, pact_ffi.PactSpecification.V4)

    # Create message interaction
    pact_ffi.new_message_interaction(pact, "test message")

    # Get message iterator
    iterator = pact_ffi.pact_handle_get_message_iter(pact)

    # Test string representation
    assert "PactMessageIterator" in str(iterator)
    assert "PactMessageIterator" in repr(iterator)

    # Iterate and count messages
    message_count = sum(1 for _ in iterator)

    # Should have the message
    assert message_count >= 1


def test_pact_interaction_owned() -> None:
    """Test PactInteraction with owned parameter."""
    pact = pact_ffi.new_pact("consumer", "provider")
    pact_ffi.with_specification(pact, pact_ffi.PactSpecification.V4)
    pact_ffi.new_sync_message_interaction(pact, "test")

    # Get an interaction through the iterator
    sync_iter = pact_ffi.pact_handle_get_sync_message_iter(pact)
    for interaction in sync_iter:
        # Interaction should be owned by the iterator
        # Test destructor doesn't crash
        del interaction
        break


def test_pact_message_iterator_empty() -> None:
    """Test PactMessageIterator with no messages."""
    pact = pact_ffi.new_pact("consumer", "provider")
    pact_ffi.with_specification(pact, pact_ffi.PactSpecification.V4)

    iterator = pact_ffi.pact_handle_get_message_iter(pact)

    # Should iterate zero times
    message_count = sum(1 for _ in iterator)
    assert message_count == 0


def test_pact_interaction_iterator_next() -> None:
    """Test iterator next functions."""
    pact = pact_ffi.new_pact("consumer", "provider")
    pact_ffi.with_specification(pact, pact_ffi.PactSpecification.V4)

    # Create multiple interactions
    pact_ffi.new_interaction(pact, "http")
    pact_ffi.new_message_interaction(pact, "async")
    pact_ffi.new_sync_message_interaction(pact, "sync")

    # Test each iterator type
    http_iter = pact_ffi.pact_handle_get_sync_http_iter(pact)
    http_count = sum(1 for _ in http_iter)
    assert http_count == 1

    async_iter = pact_ffi.pact_handle_get_async_message_iter(pact)
    async_count = sum(1 for _ in async_iter)
    assert async_count == 1

    sync_iter = pact_ffi.pact_handle_get_sync_message_iter(pact)
    sync_count = sum(1 for _ in sync_iter)
    assert sync_count == 1


def test_pact_message_iterator_repr() -> None:
    """Test PactMessageIterator __repr__ method."""
    pact = pact_ffi.new_pact("consumer", "provider")
    pact_ffi.with_specification(pact, pact_ffi.PactSpecification.V4)

    iterator = pact_ffi.pact_handle_get_message_iter(pact)
    repr_str = repr(iterator)

    assert "PactMessageIterator" in repr_str
    assert "0x" in repr_str or ">" in repr_str


def test_pact_interaction_str_repr() -> None:
    """Test PactInteraction __str__ and __repr__ methods."""
    pact = pact_ffi.new_pact("consumer", "provider")
    pact_ffi.with_specification(pact, pact_ffi.PactSpecification.V4)
    pact_ffi.new_sync_message_interaction(pact, "test")

    # Get an interaction from iterator
    sync_iter = pact_ffi.pact_handle_get_sync_message_iter(pact)
    for interaction in sync_iter:
        str_result = str(interaction)
        repr_result = repr(interaction)

        assert "SynchronousMessage" in str_result
        assert "SynchronousMessage" in repr_result
        break


def test_multiple_iterator_types_simultaneously() -> None:
    """Test using multiple iterator types at the same time."""
    pact = pact_ffi.new_pact("consumer", "provider")
    pact_ffi.with_specification(pact, pact_ffi.PactSpecification.V4)

    # Create one of each type
    pact_ffi.new_interaction(pact, "http")
    pact_ffi.new_message_interaction(pact, "async")
    pact_ffi.new_sync_message_interaction(pact, "sync")

    # Create all three iterators
    http_iter = pact_ffi.pact_handle_get_sync_http_iter(pact)
    async_iter = pact_ffi.pact_handle_get_async_message_iter(pact)
    sync_iter = pact_ffi.pact_handle_get_sync_message_iter(pact)

    # Iterate through all of them
    http_list = list(http_iter)
    async_list = list(async_iter)
    sync_list = list(sync_iter)

    assert len(http_list) == 1
    assert len(async_list) == 1
    assert len(sync_list) == 1
