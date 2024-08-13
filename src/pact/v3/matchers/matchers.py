from __future__ import annotations

from json import JSONEncoder
from typing import Any, Dict, Optional, Union


class Matcher:
    def __init__(
        self,
        matcher_type: str,
        value: Optional[Any] = None, # noqa: ANN401
        generator: Optional[str] = None,
        **kwargs: Optional[str | int | float | bool],
    ) -> None:
        self.type = matcher_type
        self.value = value
        self.generator = generator
        self.extra_attrs = {k: v for k, v in kwargs.items() if v is not None}

    def to_json(self) -> Union[str, Dict[str, Any]]:
        json_data: Dict[str, Any] = {
            "pact:matcher:type": self.type,
        }
        if self.value is not None:
            json_data["value"] = self.value
        if self.generator is not None:
            json_data["pact:generator:type"] = self.generator
        [json_data.update({k: v}) for k, v in self.extra_attrs.items() if v is not None]
        return json_data


class MatcherEncoder(JSONEncoder):
    def default(self, obj: Any) -> Union[str, Dict[str, Any]]: # noqa: ANN401
        if isinstance(obj, Matcher):
            return obj.to_json()
        return super().default(obj)


def decimal(value: float) -> Matcher:
    return Matcher("decimal", value)


def each_like(
    value: Any, # noqa: ANN401
    min_count: Optional[int] = None,
    max_count: Optional[int] = None,
) -> Matcher:
    return Matcher("type", [value], min=min_count, max=max_count)


def include(value: str, include: str) -> Matcher:
    return Matcher("include", value, include=include)


def integer(value: int) -> Matcher:
    return Matcher("integer", value)


def like(
    value: Any, # noqa: ANN401
    min_count: Optional[int] = None,
    max_count: Optional[int] = None,
) -> Matcher:
    return Matcher("type", value, min=min_count, max=max_count)


def regex(value: str, regex: str, generator: Optional[str] = None) -> Matcher:
    return Matcher("regex", value, regex=regex, generator=generator)
