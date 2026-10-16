"""
Tests of pact._util functions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NamedTuple

import pytest

from pact._util import (
    apply_args,
    strftime_to_simple_date_format,
    strip_url_credentials,
)

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        pytest.param(
            "http://localhost:8080",
            ("http://localhost:8080", None, None),
            id="no-credentials",
        ),
        pytest.param(
            "http://user@broker:9292",
            ("http://broker:9292", "user", None),
            id="username",
        ),
        pytest.param(
            "http://user:pass@broker:9292/",
            ("http://broker:9292/", "user", "pass"),
            id="username-password",
        ),
        pytest.param(
            "http://:pass@broker/",
            ("http://broker/", None, "pass"),
            id="password-only",
        ),
        pytest.param(
            "https://us%40er:p%3Ass@broker.example.com/pacts?latest=true",
            ("https://broker.example.com/pacts?latest=true", "us@er", "p:ss"),
            id="percent-encoded",
        ),
        pytest.param(
            "http://LocalHost:8000/api/v1",
            ("http://localhost:8000/api/v1", None, None),
            id="uppercase-host",
        ),
        pytest.param(
            "https://example.com:443/a%20b/c",
            ("https://example.com/a%20b/c", None, None),
            id="default-port",
        ),
        pytest.param(
            "http://user:pass@[::1]:8080/",
            ("http://[::1]:8080/", "user", "pass"),
            id="ipv6",
        ),
    ],
)
def test_strip_url_credentials(
    url: str,
    expected: tuple[str, str | None, str | None],
) -> None:
    assert strip_url_credentials(url) == expected


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


def test_convert_python_to_java_datetime_format_with_utc_offset_with_colon() -> None:
    assert strftime_to_simple_date_format("%:z") == "XXX"
    assert (
        strftime_to_simple_date_format("%Y-%m-%dT%H:%M:%S%:z")
        == "yyyy-MM-dd'T'HH:mm:ssXXX"
    )


@pytest.mark.parametrize("python_format", ["%", "%Y-%m-%d%", "%:", "%Y%:"])
def test_convert_python_to_java_datetime_format_with_incomplete_code(
    python_format: str,
) -> None:
    with pytest.raises(ValueError, match="Incomplete Python format code"):
        strftime_to_simple_date_format(python_format)


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

    def __call__(self, a: int, b: str, c: float, d: bytes = b"d") -> Args:
        return Args(
            args={"a": a, "b": b, "c": c, "d": d},
            kwargs={},
            variadic_args=[],
            variadic_kwargs={},
        )

    def method(self, a: int, b: str, c: float, d: bytes = b"d") -> Args:
        return Args(
            args={"a": a, "b": b, "c": c, "d": d},
            kwargs={},
            variadic_args=[],
            variadic_kwargs={},
        )

    @classmethod
    def class_method(cls, a: int, b: str, c: float, d: bytes = b"d") -> Args:
        return Args(
            args={"a": a, "b": b, "c": c, "d": d},
            kwargs={},
            variadic_args=[],
            variadic_kwargs={},
        )

    @staticmethod
    def static_method(a: int, b: str, c: float, d: bytes = b"d") -> Args:
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
