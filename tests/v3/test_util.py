"""
Tests of pact.v3.util functions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from pact.v3._util import apply_args, strftime_to_simple_date_format

if TYPE_CHECKING:
    from collections.abc import Callable


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


def no_annotations(a, b, c, d=b"d"):  # noqa: ANN001, ANN201  # type: ignore[reportUnknownArgumentType]
    return f"{a}:{b}:{c}:{d!r}"


def annotated(a: int, b: str, c: float, d: bytes = b"d") -> str:
    return f"{a}:{b}:{c}:{d!r}"


def mixed(a: int, /, b: str, *, c: float, d: bytes = b"d") -> str:
    return f"{a}:{b}:{c}:{d!r}"


def variadic_args(*args: Any) -> str:  # noqa: ANN401
    return ":".join(str(arg) for arg in args)


def variadic_kwargs(**kwargs: Any) -> str:  # noqa: ANN401
    return ":".join(str(v) for v in kwargs.values())


def variadic_args_kwargs(*args: Any, **kwargs: Any) -> list[str]:  # noqa: ANN401
    return [
        ":".join(str(arg) for arg in args),
        ":".join(str(v) for v in kwargs.values()),
    ]


def mixed_variadic_args(a: int, *args: Any, d: bytes = b"d") -> list[str]:  # noqa: ANN401
    return [f"{a}:{d!r}", ":".join(str(arg) for arg in args)]


def mixed_variadic_kwargs(a: int, d: bytes = b"d", **kwargs: Any) -> list[str]:  # noqa: ANN401
    return [f"{a}:{d!r}", ":".join(str(v) for v in kwargs.values())]


def mixed_variadic_args_kwargs(
    a: int,
    *args: Any,  # noqa: ANN401
    d: bytes = b"d",
    **kwargs: Any,  # noqa: ANN401
) -> list[str]:
    return [
        f"{a}:{d!r}",
        ":".join(str(arg) for arg in args),
        ":".join(str(v) for v in kwargs.values()),
    ]


class Foo:  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        pass

    def __call__(self, a: int, b: str, c: float, d: bytes = b"d") -> str:  # noqa: D102
        return f"{a}:{b}:{c}:{d!r}"

    def method(self, a: int, b: str, c: float, d: bytes = b"d") -> str:  # noqa: D102
        return f"{a}:{b}:{c}:{d!r}"

    @classmethod
    def class_method(cls, a: int, b: str, c: float, d: bytes = b"d") -> str:  # noqa: D102
        return f"{a}:{b}:{c}:{d!r}"

    @staticmethod
    def static_method(a: int, b: str, c: float, d: bytes = b"d") -> str:  # noqa: D102
        return f"{a}:{b}:{c}:{d!r}"


@pytest.mark.parametrize(
    ("func", "args", "expected"),
    [
        (no_annotations, {"a": 1, "b": "b", "c": 3.14}, "1:b:3.14:b'd'"),
        (no_annotations, {"a": 1, "b": "b", "c": 3.14, "d": b"e"}, "1:b:3.14:b'e'"),
        (annotated, {"a": 1, "b": "b", "c": 3.14}, "1:b:3.14:b'd'"),
        (annotated, {"a": 1, "b": "b", "c": 3.14, "d": b"e"}, "1:b:3.14:b'e'"),
        (mixed, {"a": 1, "b": "b", "c": 3.14}, "1:b:3.14:b'd'"),
        (mixed, {"a": 1, "b": "b", "c": 3.14, "d": b"e"}, "1:b:3.14:b'e'"),
        (variadic_args, {"a": 1, "b": "b", "c": 3.14}, "1:b:3.14"),
        (variadic_args, {"a": 1, "b": "b", "c": 3.14, "d": b"e"}, "1:b:3.14:b'e'"),
        (variadic_kwargs, {"a": 1, "b": "b", "c": 3.14}, "1:b:3.14"),
        (variadic_kwargs, {"a": 1, "b": "b", "c": 3.14, "d": b"e"}, "1:b:3.14:b'e'"),
        (variadic_args_kwargs, {"a": 1, "b": "b", "c": 3.14}, ["", "1:b:3.14"]),
        (
            variadic_args_kwargs,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            ["", "1:b:3.14:b'e'"],
        ),
        (mixed_variadic_args, {"a": 1, "b": "b", "c": 3.14}, ["1:b'd'", "b:3.14"]),
        (
            mixed_variadic_args,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            ["1:b'e'", "b:3.14"],
        ),
        (mixed_variadic_kwargs, {"a": 1, "b": "b", "c": 3.14}, ["1:b'd'", "b:3.14"]),
        (
            mixed_variadic_kwargs,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            ["1:b'e'", "b:3.14"],
        ),
        (
            mixed_variadic_args_kwargs,
            {"a": 1, "b": "b", "c": 3.14},
            ["1:b'd'", "", "b:3.14"],
        ),
        (
            mixed_variadic_args_kwargs,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            ["1:b'e'", "", "b:3.14"],
        ),
        (
            mixed_variadic_args_kwargs,
            {"a": 1, "b": "b", "c": 3.14, "e": "f"},
            ["1:b'd'", "", "b:3.14:f"],
        ),
        (
            mixed_variadic_args_kwargs,
            {"a": 1, "b": "b", "c": 3.14, "e": "f", "d": b"e"},
            ["1:b'e'", "", "b:3.14:f"],
        ),
        (
            Foo(),
            {"a": 1, "b": "b", "c": 3.14},
            "1:b:3.14:b'd'",
        ),
        (
            Foo(),
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            "1:b:3.14:b'e'",
        ),
        (
            Foo().class_method,
            {"a": 1, "b": "b", "c": 3.14},
            "1:b:3.14:b'd'",
        ),
        (
            Foo().class_method,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            "1:b:3.14:b'e'",
        ),
        (
            Foo().static_method,
            {"a": 1, "b": "b", "c": 3.14},
            "1:b:3.14:b'd'",
        ),
        (
            Foo().static_method,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            "1:b:3.14:b'e'",
        ),
    ],  # type: ignore[reportUnknownArgumentType]
)
def test_apply_expected(
    func: Callable[..., Any],
    args: dict[str, Any],
    expected: str | list[str],
) -> None:
    assert apply_args(func, args) == expected
