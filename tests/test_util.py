"""
Tests of pact._util functions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NamedTuple

import pytest

from pact._util import apply_args, strftime_to_simple_date_format

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


class Args(NamedTuple):
    """
    Named tuple to hold the arguments passed to a function.
    """

    args: dict[str, Any]
    kwargs: dict[str, Any]
    variadic_args: list[Any]
    variadic_kwargs: dict[str, Any]


def no_annotations(a, b, c, d=b"d"):  # noqa: ANN001, ANN201  # type: ignore[reportUnknownArgumentType]
    return Args(
        args={"a": a, "b": b, "c": c, "d": d},
        kwargs={},
        variadic_args=[],
        variadic_kwargs={},
    )


def annotated(a: int, b: str, c: float, d: bytes = b"d") -> Args:
    return Args(
        args={"a": a, "b": b, "c": c, "d": d},
        kwargs={},
        variadic_args=[],
        variadic_kwargs={},
    )


def mixed(a: int, /, b: str, *, c: float, d: bytes = b"d") -> Args:
    return Args(
        args={"a": a, "b": b, "c": c, "d": d},
        kwargs={},
        variadic_args=[],
        variadic_kwargs={},
    )


def variadic_args(*args: Any) -> Args:  # noqa: ANN401
    return Args(
        args={},
        kwargs={},
        variadic_args=list(args),
        variadic_kwargs={},
    )


def variadic_kwargs(**kwargs: Any) -> Args:  # noqa: ANN401
    return Args(
        args={},
        kwargs=kwargs,
        variadic_args=[],
        variadic_kwargs={**kwargs},
    )


def variadic_args_kwargs(*args: Any, **kwargs: Any) -> Args:  # noqa: ANN401
    return Args(
        args={},
        kwargs=kwargs,
        variadic_args=list(args),
        variadic_kwargs={**kwargs},
    )


def mixed_variadic_args(a: int, *args: Any, d: bytes = b"d") -> Args:  # noqa: ANN401
    return Args(
        args={"a": a, "d": d},
        kwargs={},
        variadic_args=list(args),
        variadic_kwargs={},
    )


def mixed_variadic_kwargs(a: int, d: bytes = b"d", **kwargs: Any) -> Args:  # noqa: ANN401
    return Args(
        args={"a": a, "d": d},
        kwargs=kwargs,
        variadic_args=[],
        variadic_kwargs={**kwargs},
    )


def mixed_variadic_args_kwargs(
    a: int,
    *args: Any,  # noqa: ANN401
    d: bytes = b"d",
    **kwargs: Any,  # noqa: ANN401
) -> Args:
    return Args(
        args={"a": a, "d": d},
        kwargs=kwargs,
        variadic_args=list(args),
        variadic_kwargs={**kwargs},
    )


class Foo:  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        pass

    def __call__(self, a: int, b: str, c: float, d: bytes = b"d") -> Args:  # noqa: D102
        return Args(
            args={"a": a, "b": b, "c": c, "d": d},
            kwargs={},
            variadic_args=[],
            variadic_kwargs={},
        )

    def method(self, a: int, b: str, c: float, d: bytes = b"d") -> Args:  # noqa: D102
        return Args(
            args={"a": a, "b": b, "c": c, "d": d},
            kwargs={},
            variadic_args=[],
            variadic_kwargs={},
        )

    @classmethod
    def class_method(cls, a: int, b: str, c: float, d: bytes = b"d") -> Args:  # noqa: D102
        return Args(
            args={"a": a, "b": b, "c": c, "d": d},
            kwargs={},
            variadic_args=[],
            variadic_kwargs={},
        )

    @staticmethod
    def static_method(a: int, b: str, c: float, d: bytes = b"d") -> Args:  # noqa: D102
        return Args(
            args={"a": a, "b": b, "c": c, "d": d},
            kwargs={},
            variadic_args=[],
            variadic_kwargs={},
        )


@pytest.mark.parametrize(
    ("func", "args", "expected"),
    [
        (
            no_annotations,
            {"a": 1, "b": "b", "c": 3.14},
            Args({"a": 1, "b": "b", "c": 3.14, "d": b"d"}, {}, [], {}),
        ),
        (
            no_annotations,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            Args({"a": 1, "b": "b", "c": 3.14, "d": b"e"}, {}, [], {}),
        ),
        (
            annotated,
            {"a": 1, "b": "b", "c": 3.14},
            Args({"a": 1, "b": "b", "c": 3.14, "d": b"d"}, {}, [], {}),
        ),
        (
            annotated,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            Args({"a": 1, "b": "b", "c": 3.14, "d": b"e"}, {}, [], {}),
        ),
        (
            mixed,
            {"a": 1, "b": "b", "c": 3.14},
            Args({"a": 1, "b": "b", "c": 3.14, "d": b"d"}, {}, [], {}),
        ),
        (
            mixed,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            Args({"a": 1, "b": "b", "c": 3.14, "d": b"e"}, {}, [], {}),
        ),
        (
            variadic_args,
            {"a": 1, "b": "b", "c": 3.14},
            Args({}, {}, [1, "b", 3.14], {}),
        ),
        (
            variadic_args,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            Args({}, {}, [1, "b", 3.14, b"e"], {}),
        ),
        (
            variadic_kwargs,
            {"a": 1, "b": "b", "c": 3.14},
            Args({}, {"a": 1, "b": "b", "c": 3.14}, [], {"a": 1, "b": "b", "c": 3.14}),
        ),
        (
            variadic_kwargs,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            Args(
                {},
                {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
                [],
                {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            ),
        ),
        (
            variadic_args_kwargs,
            {"a": 1, "b": "b", "c": 3.14},
            Args({}, {"a": 1, "b": "b", "c": 3.14}, [], {"a": 1, "b": "b", "c": 3.14}),
        ),
        (
            variadic_args_kwargs,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            Args(
                {},
                {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
                [],
                {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            ),
        ),
        (
            mixed_variadic_args,
            {"a": 1, "b": "b", "c": 3.14},
            Args({"a": 1, "d": b"d"}, {}, ["b", 3.14], {}),
        ),
        (
            mixed_variadic_args,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            Args({"a": 1, "d": b"e"}, {}, ["b", 3.14], {}),
        ),
        (
            mixed_variadic_kwargs,
            {"a": 1, "b": "b", "c": 3.14},
            Args({"a": 1, "d": b"d"}, {"b": "b", "c": 3.14}, [], {"b": "b", "c": 3.14}),
        ),
        (
            mixed_variadic_kwargs,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            Args({"a": 1, "d": b"e"}, {"b": "b", "c": 3.14}, [], {"b": "b", "c": 3.14}),
        ),
        (
            mixed_variadic_args_kwargs,
            {"a": 1, "b": "b", "c": 3.14},
            Args({"a": 1, "d": b"d"}, {"b": "b", "c": 3.14}, [], {"b": "b", "c": 3.14}),
        ),
        (
            mixed_variadic_args_kwargs,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            Args({"a": 1, "d": b"e"}, {"b": "b", "c": 3.14}, [], {"b": "b", "c": 3.14}),
        ),
        (
            Foo(),
            {"a": 1, "b": "b", "c": 3.14},
            Args({"a": 1, "b": "b", "c": 3.14, "d": b"d"}, {}, [], {}),
        ),
        (
            Foo(),
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            Args({"a": 1, "b": "b", "c": 3.14, "d": b"e"}, {}, [], {}),
        ),
        (
            Foo().class_method,
            {"a": 1, "b": "b", "c": 3.14},
            Args({"a": 1, "b": "b", "c": 3.14, "d": b"d"}, {}, [], {}),
        ),
        (
            Foo().class_method,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            Args({"a": 1, "b": "b", "c": 3.14, "d": b"e"}, {}, [], {}),
        ),
        (
            Foo().static_method,
            {"a": 1, "b": "b", "c": 3.14},
            Args({"a": 1, "b": "b", "c": 3.14, "d": b"d"}, {}, [], {}),
        ),
        (
            Foo().static_method,
            {"a": 1, "b": "b", "c": 3.14, "d": b"e"},
            Args({"a": 1, "b": "b", "c": 3.14, "d": b"e"}, {}, [], {}),
        ),
    ],  # type: ignore[reportUnknownArgumentType]
)
def test_apply_expected(
    func: Callable[..., Args],
    args: dict[str, Any],
    expected: Args,
) -> None:
    assert apply_args(func, args) == expected
