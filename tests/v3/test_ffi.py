"""
Tests of the FFI module.

These tests are intended to ensure that the FFI module is working correctly.
They are not intended to test the Pact API itself, as that is handled by the
client library.
"""

import re

import pytest

from pact.v3 import ffi


def test_version() -> None:
    assert isinstance(ffi.version(), str)
    assert len(ffi.version()) > 0
    assert ffi.version().count(".") == 2


def test_string_result_ok() -> None:
    result = ffi.StringResult(ffi.lib.pactffi_generate_datetime_string(b"yyyy"))
    assert result.is_ok
    assert not result.is_failed
    assert re.match(r"^\d{4}$", result.text)
    assert str(result) == result.text
    assert repr(result) == f"<StringResult: OK, {result.text!r}>"
    result.raise_exception()


def test_string_result_failed() -> None:
    result = ffi.StringResult(ffi.lib.pactffi_generate_datetime_string(b"t"))
    assert not result.is_ok
    assert result.is_failed
    assert result.text.startswith("Error parsing")
    with pytest.raises(RuntimeError):
        result.raise_exception()


def test_datetime_valid() -> None:
    ffi.validate_datetime("2023-01-01", "yyyy-MM-dd")


def test_datetime_invalid() -> None:
    with pytest.raises(ValueError, match=r"Invalid datetime value.*"):
        ffi.validate_datetime("01/01/2023", "yyyy-MM-dd")


def test_get_error_message() -> None:
    # The first bit makes sure that an error is generated.
    invalid_utf8 = b"\xc3\x28"
    ret: int = ffi.lib.pactffi_validate_datetime(invalid_utf8, invalid_utf8)
    assert ret == 2
    assert ffi.get_error_message() == "error parsing value as UTF-8"


def test_owned_string() -> None:
    string = ffi.get_tls_ca_certificate()
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
