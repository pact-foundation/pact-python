"""
Tests of pact._util functions.
"""

from __future__ import annotations

import asyncio
import contextlib
import sys
import threading
from contextvars import ContextVar
from functools import partial
from typing import TYPE_CHECKING, Any, NamedTuple

import pytest

try:
    import trio  # type: ignore[import-not-found]
except ImportError:
    trio = None  # type: ignore[assignment]

try:
    import curio  # type: ignore[import-not-found,import-untyped]
except (ImportError, AttributeError):
    # curio has compatibility issues with Python 3.12+
    curio = None  # type: ignore[assignment]


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


def test_apply_args_async_simple() -> None:
    async def async_func(a: int, b: int) -> int:
        await asyncio.sleep(0.001)
        return a + b

    result = apply_args(async_func, {"a": 1, "b": 2})  # pyright: ignore[reportCallIssue]
    assert result == 3


def test_apply_args_async_with_gather() -> None:
    call_order = []

    async def async_func(value: int) -> int:
        await asyncio.sleep(0.01 * (5 - value))
        call_order.append(value)
        return value * 2

    async def orchestrator(x: int, y: int) -> int:
        results = await asyncio.gather(
            async_func(x),
            async_func(y),
        )
        return sum(results)

    result = apply_args(orchestrator, {"x": 1, "y": 2})  # pyright: ignore[reportCallIssue]
    assert result == 6
    assert sorted(call_order) == [1, 2]


def test_apply_args_async_state_handler() -> None:
    called_with = []

    async def async_state_handler(
        state: str,
        action: str,
        parameters: dict[str, Any] | None,
    ) -> None:
        await asyncio.sleep(0.001)
        called_with.append((state, action, parameters))

    apply_args(  # type: ignore[unused-coroutine]  # pyright: ignore[reportCallIssue]
        async_state_handler,
        {"state": "user exists", "action": "setup", "parameters": {"id": 123}},
    )

    assert len(called_with) == 1
    assert called_with[0] == ("user exists", "setup", {"id": 123})


def test_apply_args_async_message_handler() -> None:
    async def async_message_handler(
        _name: str,
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        await asyncio.sleep(0.001)
        return {
            "contents": b"test message",
            "metadata": metadata,
            "content_type": "application/json",
        }

    result = apply_args(  # pyright: ignore[reportCallIssue]
        async_message_handler,
        {"name": "test_message", "metadata": {"key": "value"}},
    )  # type: ignore[misc]

    assert result["contents"] == b"test message"  # type: ignore[index]
    assert result["metadata"] == {"key": "value"}  # type: ignore[index]
    assert result["content_type"] == "application/json"  # type: ignore[index]


def test_apply_args_async_parallel_operations() -> None:
    setup_order = []

    async def setup_resource(resource_id: int) -> None:
        await asyncio.sleep(0.01 * (5 - resource_id))
        setup_order.append(resource_id)

    async def parallel_setup(
        _state: str,
        action: str,
        parameters: dict[str, Any] | None,
    ) -> None:
        if action == "setup" and parameters:
            resource_ids = parameters.get("resource_ids", [])
            await asyncio.gather(*[setup_resource(rid) for rid in resource_ids])

    apply_args(  # type: ignore[unused-coroutine]  # pyright: ignore[reportCallIssue]
        parallel_setup,
        {
            "state": "resources exist",
            "action": "setup",
            "parameters": {"resource_ids": [1, 2, 3]},
        },
    )

    assert sorted(setup_order) == [1, 2, 3]


def test_apply_args_async_exception() -> None:
    async def async_func() -> None:
        await asyncio.sleep(0.001)
        msg = "Test error"
        raise ValueError(msg)

    with pytest.raises(ValueError, match="Test error"):
        apply_args(async_func, {})  # type: ignore[unused-coroutine]


def test_apply_args_async_preserves_context_vars() -> None:
    test_var: ContextVar[str] = ContextVar("test_var")
    test_var.set("original_value")

    async def async_handler(_state: str) -> str:
        await asyncio.sleep(0.001)
        return test_var.get()

    result = apply_args(async_handler, {"state": "test"})  # pyright: ignore[reportCallIssue]
    assert result == "original_value"


def test_apply_args_async_context_isolation() -> None:
    counter_var: ContextVar[int] = ContextVar("counter", default=0)

    async def async_increment() -> int:
        current = counter_var.get()
        counter_var.set(current + 1)
        await asyncio.sleep(0.001)
        return counter_var.get()

    counter_var.set(5)
    result = apply_args(async_increment, {})
    assert result == 6
    assert counter_var.get() == 5


@pytest.mark.skipif(trio is None, reason="trio not installed")
def test_apply_args_trio_simple() -> None:
    async def trio_func(x: int, y: int) -> int:
        await trio.sleep(0.001)
        return x + y

    result = apply_args(trio_func, {"x": 5, "y": 3})  # pyright: ignore[reportCallIssue]
    assert result == 8


@pytest.mark.skipif(trio is None, reason="trio not installed")
def test_apply_args_trio_with_nursery() -> None:
    results: list[int] = []

    async def trio_parallel(resources: list[int]) -> list[int]:
        async def fetch_resource(resource_id: int) -> None:
            await trio.sleep(0.001)
            results.append(resource_id)

        async with trio.open_nursery() as nursery:
            for resource_id in resources:
                nursery.start_soon(fetch_resource, resource_id)

        return sorted(results)

    result = apply_args(trio_parallel, {"resources": [3, 1, 2]})  # pyright: ignore[reportCallIssue]
    assert result == [1, 2, 3]


@pytest.mark.skipif(trio is None, reason="trio not installed")
def test_apply_args_trio_state_handler() -> None:
    called = False

    async def trio_state_handler(state: str, action: str, **_params: object) -> None:
        nonlocal called
        await trio.sleep(0.001)
        called = True
        assert state == "database initialized"
        assert action == "setup"

    apply_args(  # type: ignore[unused-coroutine]
        trio_state_handler,
        {
            "state": "database initialized",
            "action": "setup",
        },
    )
    assert called


@pytest.mark.skipif(trio is None, reason="trio not installed")
def test_apply_args_trio_message_handler() -> None:
    async def trio_message_handler() -> dict[str, str]:
        await trio.sleep(0.001)
        return {"message": "Hello from trio"}

    result = apply_args(trio_message_handler, {})  # pyright: ignore[reportCallIssue]
    assert result == {"message": "Hello from trio"}


@pytest.mark.skipif(trio is None, reason="trio not installed")
def test_apply_args_trio_exception() -> None:
    async def trio_func() -> None:
        await trio.sleep(0.001)
        msg = "Trio error"
        raise ValueError(msg)

    with pytest.raises(ValueError, match="Trio error"):
        apply_args(trio_func, {})  # type: ignore[unused-coroutine]  # pyright: ignore[reportCallIssue]


@pytest.mark.skipif(trio is None, reason="trio not installed")
def test_apply_args_trio_preserves_context_vars() -> None:
    test_var: ContextVar[str] = ContextVar("test_var_trio")
    test_var.set("trio_value")

    async def trio_handler(_state: str) -> str:
        await trio.sleep(0.001)
        return test_var.get()

    result = apply_args(trio_handler, {"state": "test"})  # pyright: ignore[reportCallIssue]
    assert result == "trio_value"


@pytest.mark.skipif(trio is None, reason="trio not installed")
def test_apply_args_trio_context_isolation() -> None:
    counter_var: ContextVar[int] = ContextVar("counter_trio", default=0)

    async def trio_increment() -> int:
        current = counter_var.get()
        counter_var.set(current + 1)
        await trio.sleep(0.001)
        return counter_var.get()

    counter_var.set(10)
    result = apply_args(trio_increment, {})  # pyright: ignore[reportCallIssue]
    assert result == 11
    assert counter_var.get() == 10


@pytest.mark.skipif(curio is None, reason="curio not installed")
def test_apply_args_curio_simple() -> None:
    async def curio_func(x: int, y: int) -> int:
        await curio.sleep(0.001)
        return x + y

    result = apply_args(curio_func, {"x": 7, "y": 4})  # pyright: ignore[reportCallIssue]
    assert result == 11


@pytest.mark.skipif(curio is None, reason="curio not installed")
def test_apply_args_curio_with_task_group() -> None:
    results: list[int] = []

    async def curio_parallel(resources: list[int]) -> list[int]:
        async def fetch_resource(resource_id: int) -> None:
            await curio.sleep(0.001)
            results.append(resource_id)

        async with curio.TaskGroup() as g:
            for resource_id in resources:
                await g.spawn(fetch_resource, resource_id)

        return sorted(results)

    result = apply_args(curio_parallel, {"resources": [3, 1, 2]})  # pyright: ignore[reportCallIssue]
    assert result == [1, 2, 3]


@pytest.mark.skipif(curio is None, reason="curio not installed")
def test_apply_args_curio_state_handler() -> None:
    called = False

    async def curio_state_handler(state: str, action: str, **_params: object) -> None:
        nonlocal called
        await curio.sleep(0.001)
        called = True
        assert state == "database initialized"
        assert action == "setup"

    apply_args(  # type: ignore[unused-coroutine]  # pyright: ignore[reportCallIssue]
        curio_state_handler,
        {
            "state": "database initialized",
            "action": "setup",
        },
    )
    assert called


@pytest.mark.skipif(curio is None, reason="curio not installed")
def test_apply_args_curio_message_handler() -> None:
    async def curio_message_handler() -> dict[str, str]:
        await curio.sleep(0.001)
        return {"message": "Hello from curio"}

    result = apply_args(curio_message_handler, {})  # pyright: ignore[reportCallIssue]
    assert result == {"message": "Hello from curio"}


@pytest.mark.skipif(curio is None, reason="curio not installed")
def test_apply_args_curio_exception() -> None:
    async def curio_func() -> None:
        await curio.sleep(0.001)
        msg = "Curio error"
        raise ValueError(msg)

    with pytest.raises(ValueError, match="Curio error"):
        apply_args(curio_func, {})  # type: ignore[unused-coroutine]  # pyright: ignore[reportCallIssue]


@pytest.mark.skipif(curio is None, reason="curio not installed")
def test_apply_args_curio_preserves_context_vars() -> None:
    test_var: ContextVar[str] = ContextVar("test_var_curio")
    test_var.set("curio_value")

    async def curio_handler(_state: str) -> str:
        await curio.sleep(0.001)
        return test_var.get()

    result = apply_args(curio_handler, {"state": "test"})  # pyright: ignore[reportCallIssue]
    assert result == "curio_value"


@pytest.mark.skipif(curio is None, reason="curio not installed")
def test_apply_args_curio_context_isolation() -> None:
    counter_var: ContextVar[int] = ContextVar("counter_curio", default=0)

    async def curio_increment() -> int:
        current = counter_var.get()
        counter_var.set(current + 1)
        await curio.sleep(0.001)
        return counter_var.get()

    counter_var.set(15)
    result = apply_args(curio_increment, {})  # pyright: ignore[reportCallIssue]
    assert result == 16
    assert counter_var.get() == 15


def test_apply_args_async_from_running_loop() -> None:
    result_holder: list[str] = []

    async def async_handler() -> str:
        await asyncio.sleep(0.001)
        return "from_thread"

    async def main() -> None:
        def run_in_thread() -> None:
            result = apply_args(async_handler, {})  # type: ignore[misc]  # pyright: ignore[reportCallIssue]
            result_holder.append(result)  # type: ignore[arg-type]

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()

    asyncio.run(main())
    assert result_holder[0] == "from_thread"


def test_apply_args_async_with_partial() -> None:
    async def async_func(a: int, b: int, c: int) -> int:
        await asyncio.sleep(0.001)
        return a + b + c

    partial_func = partial(async_func, 10)
    result = apply_args(partial_func, {"b": 20, "c": 30})  # pyright: ignore[reportCallIssue]
    assert result == 60


def test_apply_args_async_partial_detection() -> None:
    async def async_func(a: int) -> int:
        await asyncio.sleep(0.001)
        return a * 2

    partial_func = partial(async_func, a=5)
    result = apply_args(partial_func, {})
    assert result == 10


def test_apply_args_async_with_variadic_kwargs() -> None:
    async def async_state_handler(
        state: str, action: str, **params: object
    ) -> dict[str, Any]:
        await asyncio.sleep(0.001)
        return {"state": state, "action": action, "extra_params": params}

    result = apply_args(  # pyright: ignore[reportCallIssue]
        async_state_handler,
        {
            "state": "initialized",
            "action": "setup",
            "user_id": 123,
            "tenant": "test",
            "extra_flag": True,
        },
    )  # type: ignore[misc]

    assert result["state"] == "initialized"  # type: ignore[index]
    assert result["action"] == "setup"  # type: ignore[index]
    assert result["extra_params"]["user_id"] == 123  # type: ignore[index]
    assert result["extra_params"]["tenant"] == "test"  # type: ignore[index]
    assert result["extra_params"]["extra_flag"] is True  # type: ignore[index]


@pytest.mark.skipif(trio is None, reason="trio not installed")
def test_apply_args_trio_runtime_detection() -> None:
    async def trio_func_explicit() -> str:
        await trio.sleep(0.001)
        return "trio detected"

    result = apply_args(trio_func_explicit, {})  # pyright: ignore[reportCallIssue]
    assert result == "trio detected"


@pytest.mark.skipif(curio is None, reason="curio not installed")
def test_apply_args_curio_runtime_detection() -> None:
    async def curio_func_explicit() -> str:
        await curio.sleep(0.001)
        return "curio detected"

    result = apply_args(curio_func_explicit, {})  # pyright: ignore[reportCallIssue]
    assert result == "curio detected"


def test_apply_args_with_single_underscore_param() -> None:
    def func_with_single_underscore(_: str, value: int) -> int:
        return value * 2

    result = apply_args(func_with_single_underscore, {"_": "ignored", "value": 5})  # pyright: ignore[reportCallIssue]
    assert result == 10


def test_apply_args_async_no_runtime_fallback() -> None:
    async def plain_async_func(x: int) -> int:
        return x * 3

    result = apply_args(plain_async_func, {"x": 4})  # pyright: ignore[reportCallIssue]
    assert result == 12


def test_run_async_coroutine_trio_from_running_trio() -> None:
    pytest.importorskip("trio")
    from pact._util import (  # noqa: PLC0415
        _run_async_coroutine,
    )  # type: ignore[attr-defined]

    result_holder: list[int] = []

    async def trio_task() -> int:
        await trio.sleep(0.001)
        return 42

    async def trio_main() -> None:
        def run_in_thread() -> None:
            coro = trio_task()
            result = _run_async_coroutine(coro)  # type: ignore[attr-defined]
            result_holder.append(result)

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()

    trio.run(trio_main)
    assert result_holder[0] == 42


@pytest.mark.skipif(
    curio is None or sys.version_info >= (3, 12),
    reason="curio not compatible with Python 3.12+",
)
def test_run_async_coroutine_curio_from_running_curio() -> None:
    pytest.importorskip("curio", minversion="1.0")
    from pact._util import (  # noqa: PLC0415
        _run_async_coroutine,
    )  # type: ignore[attr-defined]

    async def curio_task() -> int:
        await curio.sleep(0.001)
        return 99

    async def curio_wrapper() -> int:
        coro = curio_task()
        return _run_async_coroutine(coro)  # type: ignore[attr-defined]

    result = curio.run(curio_wrapper)
    assert result == 99


def test_run_async_coroutine_trio_not_installed() -> None:
    import unittest.mock  # noqa: PLC0415

    from pact._util import (  # noqa: PLC0415  # type: ignore[attr-defined]
        _run_async_coroutine,
    )

    async def fake_trio_func() -> str:
        import trio  # noqa: PLC0415, F401

        await asyncio.sleep(0.001)
        return "test"

    coro = fake_trio_func()

    with (
        unittest.mock.patch("pact._util.trio", None),
        unittest.mock.patch("pact._util._detect_async_runtime", return_value="trio"),
        pytest.raises(RuntimeError, match="trio is not installed"),
    ):
        _run_async_coroutine(coro)  # type: ignore[attr-defined]

    with contextlib.suppress(Exception):
        coro.close()


def test_run_async_coroutine_curio_not_installed() -> None:
    import unittest.mock  # noqa: PLC0415

    from pact._util import (  # noqa: PLC0415
        _run_async_coroutine,  # type: ignore[attr-defined]
    )

    async def fake_curio_func() -> str:
        import curio  # noqa: PLC0415, F401

        await asyncio.sleep(0.001)
        return "test"

    coro = fake_curio_func()

    with (
        unittest.mock.patch("pact._util.curio", None),
        unittest.mock.patch("pact._util._detect_async_runtime", return_value="curio"),
        pytest.raises(RuntimeError, match="curio is not installed"),
    ):
        _run_async_coroutine(coro)  # type: ignore[attr-defined]

    with contextlib.suppress(Exception):
        coro.close()


def test_detect_async_runtime_sniffio_fallback() -> None:
    import unittest.mock  # noqa: PLC0415

    from pact._util import (  # noqa: PLC0415
        _detect_async_runtime,  # type: ignore[attr-defined]
    )

    try:
        import sniffio as sniffio_module  # noqa: PLC0415  # type: ignore[import-not-found]
    except ImportError:
        sniffio_module = None  # type: ignore[assignment]

    async def plain_func() -> str:
        return "test"

    coro = plain_func()

    if sniffio_module is not None:
        with unittest.mock.patch(
            "pact._util.sniffio.current_async_library",
            side_effect=sniffio_module.AsyncLibraryNotFoundError("not found"),
        ):
            runtime = _detect_async_runtime(coro)  # type: ignore[attr-defined]
            assert runtime == "asyncio"
    else:
        runtime = _detect_async_runtime(coro)  # type: ignore[attr-defined]
        assert runtime == "asyncio"

    coro.close()


@pytest.mark.skipif(
    curio is None or sys.version_info >= (3, 12),
    reason="curio not compatible with Python 3.12+ or not installed",
)
def test_detect_async_runtime_curio_indicators() -> None:
    import unittest.mock  # noqa: PLC0415

    from pact._util import (  # noqa: PLC0415
        _detect_async_runtime,  # type: ignore[attr-defined]
    )

    async def curio_like_func() -> str:
        import curio  # noqa: PLC0415, F401

        return "curio"

    coro = curio_like_func()

    with unittest.mock.patch("pact._util.sniffio", None):
        runtime = _detect_async_runtime(coro)  # type: ignore[attr-defined]
        assert runtime == "curio"

    coro.close()


@pytest.mark.skipif(
    curio is None or sys.version_info >= (3, 12),
    reason="curio not compatible with Python 3.12+ or not installed",
)
def test_run_async_coroutine_curio_await_exception() -> None:
    import unittest.mock  # noqa: PLC0415

    from pact._util import (  # noqa: PLC0415
        _run_async_coroutine,  # type: ignore[attr-defined]
    )

    async def curio_task() -> str:
        await curio.sleep(0.001)
        return "fallback"

    coro = curio_task()

    with unittest.mock.patch(
        "pact._util.curio.AWAIT",
        side_effect=RuntimeError("not in curio context"),
    ):
        result = _run_async_coroutine(coro)  # type: ignore[attr-defined]
        assert result == "fallback"


def test_detect_async_runtime_no_indicators_defaults_asyncio() -> None:
    import unittest.mock  # noqa: PLC0415

    from pact._util import (  # noqa: PLC0415
        _detect_async_runtime,  # type: ignore[attr-defined]
    )

    async def plain_func() -> str:
        x = 1 + 1
        return str(x)

    coro = plain_func()

    with unittest.mock.patch("pact._util.sniffio", None):
        runtime = _detect_async_runtime(coro)  # type: ignore[attr-defined]
        assert runtime == "asyncio"

    coro.close()


@pytest.mark.skipif(trio is None, reason="trio not installed")
def test_detect_async_runtime_trio_co_names() -> None:
    import unittest.mock  # noqa: PLC0415

    from pact._util import (  # noqa: PLC0415
        _detect_async_runtime,  # type: ignore[attr-defined]
    )

    async def trio_func() -> int:
        await trio.sleep(0.001)
        return 1

    coro = trio_func()
    with unittest.mock.patch("pact._util.sniffio", None):
        assert _detect_async_runtime(coro) == "trio"  # type: ignore[arg-type]
    coro.close()


@pytest.mark.skipif(
    curio is None or sys.version_info >= (3, 12),
    reason="curio not compatible with Python 3.12+ or not installed",
)
def test_detect_async_runtime_curio_co_names() -> None:
    import unittest.mock  # noqa: PLC0415

    from pact._util import (  # noqa: PLC0415
        _detect_async_runtime,  # type: ignore[attr-defined]
    )

    async def curio_func() -> int:
        await curio.sleep(0.001)
        return 1

    coro = curio_func()
    with unittest.mock.patch("pact._util.sniffio", None):
        assert _detect_async_runtime(coro) == "curio"  # type: ignore[arg-type]
    coro.close()


@pytest.mark.skipif(trio is None, reason="trio not installed")
def test_detect_async_runtime_trio_precedence() -> None:
    import unittest.mock  # noqa: PLC0415

    from pact._util import (  # noqa: PLC0415
        _detect_async_runtime,  # type: ignore[attr-defined]
    )

    async def func_with_both() -> None:
        await trio.sleep(0.001)  # type: ignore[union-attr]
        await curio.sleep(0.001)  # type: ignore[union-attr]  # never executed, just puts "curio" in co_names

    coro = func_with_both()
    with (
        unittest.mock.patch("pact._util.sniffio", None),
        unittest.mock.patch("pact._util.curio", object()),
    ):
        assert _detect_async_runtime(coro) == "trio"  # type: ignore[arg-type]
    coro.close()
