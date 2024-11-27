"""
Tests of pact.v3.util functions.
"""

import pytest

from pact.v3._util import strftime_to_simple_date_format


def test_convert_python_to_java_datetime_format_basic() -> None:
    assert strftime_to_simple_date_format("%Y-%m-%d") == "yyyy-MM-dd"
    assert strftime_to_simple_date_format("%H:%M:%S") == "HH:mm:ss"
    assert (
        strftime_to_simple_date_format("%Y-%m-%dT%H:%M:%S") == "yyyy-MM-dd'T'HH:mm:ss"
    )


def test_convert_python_to_java_datetime_format_with_unsupported_code() -> None:
    with pytest.raises(
        ValueError,
        match="Cannot convert locale-dependent Python format code `%c` to Java",
    ):
        strftime_to_simple_date_format("%c")


def test_convert_python_to_java_datetime_format_with_warning() -> None:
    with pytest.warns(
        UserWarning, match="The Java equivalent for `%U` is locale dependent."
    ):
        assert strftime_to_simple_date_format("%U") == "ww"


def test_convert_python_to_java_datetime_format_with_escape_characters() -> None:
    assert strftime_to_simple_date_format("'%Y-%m-%d'") == "''yyyy-MM-dd''"
    assert strftime_to_simple_date_format("%%Y") == "%'Y'"


def test_convert_python_to_java_datetime_format_with_single_quote() -> None:
    assert strftime_to_simple_date_format("%Y'%m'%d") == "yyyy''MM''dd"
