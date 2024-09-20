"""
Matching functionality for Pact.

Matchers are used in Pact to allow for more flexible matching of data. While the
consumer defines the expected request and response, there are circumstances
where the provider may return dynamically generated data. In these cases, the
consumer should use a matcher to define the expected data.
"""

from __future__ import annotations

from json import JSONEncoder
from typing import TYPE_CHECKING, Any, Literal, Union

from pact.v3.match.types import Matcher

if TYPE_CHECKING:
    from pact.v3.generators import Generator
    from pact.v3.match.types import MatchType

MatcherTypeV3 = Literal[
    "equality",
    "regex",
    "type",
    "include",
    "integer",
    "decimal",
    "number",
    "timestamp",
    "time",
    "date",
    "null",
    "boolean",
    "contentType",
    "values",
    "arrayContains",
]

MatcherTypeV4 = Union[
    MatcherTypeV3,
    Literal[
        "statusCode",
        "notEmpty",
        "semver",
        "eachKey",
        "eachValue",
    ],
]


class ConcreteMatcher(Matcher):
    """
    ConcreteMatcher class.
    """

    def __init__(
        self,
        matcher_type: MatcherTypeV4,
        value: Any | None = None,  # noqa: ANN401
        generator: Generator | None = None,
        *,
        force_generator: bool | None = False,
        **kwargs: MatchType,
    ) -> None:
        """
        Initialize the matcher class.

        Args:
            matcher_type:
                The type of the matcher.
            value:
                The value to return when running a consumer test.
                Defaults to None.
            generator:
                The generator to use when generating the value. The generator will
                generally only be used if value is not provided. Defaults to None.
            force_generator:
                If True, the generator will be used to generate a value even if
                a value is provided. Defaults to False.
            **kwargs:
                Additional configuration elements to pass to the matcher.
        """
        self.type = matcher_type
        self.value = value
        self.generator = generator
        self.force_generator = force_generator
        self.extra_attrs = {k: v for k, v in kwargs.items() if v is not None}

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the matcher to a dictionary for json serialization.
        """
        data: dict[str, Any] = {
            "pact:matcher:type": self.type,
        }
        data["value"] = self.value if self.value is not None else ""
        if self.generator is not None and (self.value is None or self.force_generator):
            data.update(self.generator.to_dict())
        data.update(self.extra_attrs)
        return data


class MatcherEncoder(JSONEncoder):
    """
    Matcher encoder class for json serialization.
    """

    def default(self, o: Any) -> Any:  # noqa: ANN401
        """
        Encode the object to json.
        """
        if isinstance(o, Matcher):
            return o.to_dict()
        return super().default(o)
