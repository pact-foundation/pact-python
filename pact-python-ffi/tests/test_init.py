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
