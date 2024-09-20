"""
Implementation of matchers for the V3 and V4 Pact specification.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from json import JSONEncoder
from typing import Any, Dict, List, Literal, Mapping, Sequence, Tuple

from pact.v3.generators import (
    Generator,
    date_time,
    random_boolean,
    random_decimal,
    random_int,
    random_string,
)
from pact.v3.generators import (
    date as date_generator,
)
from pact.v3.generators import (
    regex as regex_generator,
)
from pact.v3.generators import (
    time as time_generator,
)

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

MatcherTypeV4 = (
    MatcherTypeV3
    | Literal[
        "statusCode",
        "notEmpty",
        "semver",
        "eachKey",
        "eachValue",
    ]
)


class Matcher(ABC):
    """
    Matcher interface for exporting.
    """

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the matcher to a dictionary for json serialization.
        """


AtomicType = str | int | float | bool | None
MatchType = (
    AtomicType
    | Dict[AtomicType, AtomicType]
    | List[AtomicType]
    | Tuple[AtomicType]
    | Sequence[AtomicType]
    | Mapping[AtomicType, AtomicType]
)


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
        **kwargs: AtomicType,
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

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the matcher to a dictionary for json serialization.
        """
        data: Dict[str, Any] = {
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


def integer(
    value: int | None = None,
    min_val: int | None = None,
    max_val: int | None = None,
) -> Matcher:
    """
    Returns a matcher that matches an integer value.

    Args:
        value:
            The value to return when running a consumer test. Defaults to None.
        min_val:
            The minimum value of the integer to generate. Defaults to None.
        max_val:
            The maximum value of the integer to generate. Defaults to None.
    """
    return ConcreteMatcher(
        "integer",
        value,
        generator=random_int(min_val, max_val),
    )


def decimal(value: float | None = None, digits: int | None = None) -> Matcher:
    """
    Returns a matcher that matches a decimal value.

    Args:
        value:
            The value to return when running a consumer test. Defaults to None.
        digits:
            The number of decimal digits to generate. Defaults to None.
    """
    return ConcreteMatcher("decimal", value, generator=random_decimal(digits))


def number(
    value: float | None = None,
    min_val: float | None = None,
    max_val: float | None = None,
    digits: int | None = None,
) -> Matcher:
    """
    Returns a matcher that matches a number value.

    If all arguments are None, a random_decimal generator will be used.
    If value argument is an integer or either min_val or max_val are provided,
    a random_int generator will be used.

    Args:
        value:
            The value to return when running a consumer test.
            Defaults to None.
        min_val:
            The minimum value of the number to generate. Only used when
            value is an integer. Defaults to None.
        max_val:
            The maximum value of the number to generate. Only used when
            value is an integer. Defaults to None.
        digits:
            The number of decimal digits to generate. Only used when
            value is a float. Defaults to None.
    """
    if min_val is not None and digits is not None:
        msg = "min_val and digits cannot be used together"
        raise ValueError(msg)

    if isinstance(value, int) or any(v is not None for v in [min_val, max_val]):
        generator = random_int(min_val, max_val)
    else:
        generator = random_decimal(digits)
    return ConcreteMatcher("number", value, generator=generator)


def string(
    value: str | None = None,
    size: int | None = None,
    generator: Generator | None = None,
) -> Matcher:
    """
    Returns a matcher that matches a string value.

    Args:
        value:
            The value to return when running a consumer test. Defaults to None.
        size:
            The size of the string to generate. Defaults to None.
        generator:
            The generator to use when generating the value. Defaults to None. If
            no generator is provided and value is not provided, a random string
            generator will be used.
    """
    if generator is not None:
        return ConcreteMatcher("type", value, generator=generator, force_generator=True)
    return ConcreteMatcher("type", value, generator=random_string(size))


def boolean(*, value: bool | None = True) -> Matcher:
    """
    Returns a matcher that matches a boolean value.

    Args:
        value:
            The value to return when running a consumer test. Defaults to True.
    """
    return ConcreteMatcher("boolean", value, generator=random_boolean())


def date(format_str: str, value: str | None = None) -> Matcher:
    """
    Returns a matcher that matches a date value.

    Args:
        format_str:
            The format of the date. See
            [Java SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
            for details on the format string.
        value:
            The value to return when running a consumer test. Defaults to None.
    """
    return ConcreteMatcher(
        "date", value, format=format_str, generator=date_generator(format_str)
    )


def time(format_str: str, value: str | None = None) -> Matcher:
    """
    Returns a matcher that matches a time value.

    Args:
        format_str:
            The format of the time. See
            [Java SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
            for details on the format string.
        value:
            The value to return when running a consumer test. Defaults to None.
    """
    return ConcreteMatcher(
        "time", value, format=format_str, generator=time_generator(format_str)
    )


def timestamp(format_str: str, value: str | None = None) -> Matcher:
    """
    Returns a matcher that matches a timestamp value.

    Args:
        format_str:
            The format of the timestamp. See
            [Java SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
            for details on the format string.
        value:
            The value to return when running a consumer test. Defaults to None.
    """
    return ConcreteMatcher(
        "timestamp",
        value,
        format=format_str,
        generator=date_time(format_str),
    )


def null() -> Matcher:
    """
    Returns a matcher that matches a null value.
    """
    return ConcreteMatcher("null")


def like(
    value: MatchType,
    min_count: int | None = None,
    max_count: int | None = None,
    generator: Generator | None = None,
) -> Matcher:
    """
    Returns a matcher that matches the given template.

    Args:
        value:
            The template to match against. This can be a primitive value, a
            dictionary, or a list and matching will be done by type.
        min_count:
            The minimum number of items that must match the value. Defaults to None.
        max_count:
            The maximum number of items that must match the value. Defaults to None.
        generator:
            The generator to use when generating the value. Defaults to None.
    """
    return ConcreteMatcher(
        "type", value, min=min_count, max=max_count, generator=generator
    )


def each_like(
    value: MatchType,
    min_count: int | None = 1,
    max_count: int | None = None,
) -> Matcher:
    """
    Returns a matcher that matches each item in an array against a given value.

    Note that the matcher will validate the array length be at least one.
    Also, the argument passed will be used as a template to match against
    each item in the array and generally should not itself be an array.

    Args:
        value:
            The value to match against.
        min_count:
            The minimum number of items that must match the value. Default is 1.
        max_count:
            The maximum number of items that must match the value.
    """
    return ConcreteMatcher("type", [value], min=min_count, max=max_count)


def includes(value: str, generator: Generator | None = None) -> Matcher:
    """
    Returns a matcher that matches a string that includes the given value.

    Args:
        value:
            The value to match against.
        generator:
            The generator to use when generating the value. Defaults to None.
    """
    return ConcreteMatcher("include", value, generator=generator, force_generator=True)


def array_containing(variants: List[MatchType]) -> Matcher:
    """
    Returns a matcher that matches the items in an array against a number of variants.

    Matching is successful if each variant occurs once in the array. Variants may be
    objects containing matching rules.

    Args:
        variants:
            A list of variants to match against.
    """
    return ConcreteMatcher("arrayContains", variants=variants)


def regex(regex: str, value: str | None = None) -> Matcher:
    """
    Returns a matcher that matches a string against a regular expression.

    If no value is provided, a random string will be generated that matches
    the regular expression.

    Args:
        regex:
            The regular expression to match against.
        value:
            The value to return when running a consumer test. Defaults to None.
    """
    return ConcreteMatcher(
        "regex",
        value,
        generator=regex_generator(regex),
        regex=regex,
    )


def each_key_matches(value: MatchType, rules: Matcher | List[Matcher]) -> Matcher:
    """
    Returns a matcher that matches each key in a dictionary against a set of rules.

    Args:
        value:
            The value to match against.
        rules:
            The matching rules to match against each key.
    """
    if isinstance(rules, Matcher):
        rules = [rules]
    return ConcreteMatcher("eachKey", value, rules=rules)


def each_value_matches(value: MatchType, rules: Matcher | List[Matcher]) -> Matcher:
    """
    Returns a matcher that matches each value in a dictionary against a set of rules.

    Args:
        value:
            The value to match against.
        rules:
            The matching rules to match against each value.
    """
    if isinstance(rules, Matcher):
        rules = [rules]
    return ConcreteMatcher("eachValue", value, rules=rules)
