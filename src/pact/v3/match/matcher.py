"""
Matching functionality for Pact.

Matchers are used in Pact to allow for more flexible matching of data. While the
consumer defines the expected request and response, there are circumstances
where the provider may return dynamically generated data. In these cases, the
consumer should use a matcher to define the expected data.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from itertools import chain
from json import JSONEncoder
from typing import Any, Generic, TypeVar

from pact.v3.generate.generator import Generator
from pact.v3.types import UNSET, Matchable, MatcherType, Unset

_T = TypeVar("_T")


class Matcher(ABC, Generic[_T]):
    """
    Abstract matcher.

    In Pact, a matcher is used to define how a value should be compared. This
    allows for more flexible matching of data, especially when the provider
    returns dynamically generated data.

    This class is abstract and should not be used directly. Instead, use one of
    the concrete matcher classes. Alternatively, you can create your own matcher
    by subclassing this class.

    The matcher provides methods to convert into an integration JSON object and
    a matching rule. These methods are used internally by the Pact library when
    communicating with the FFI and generating the Pact file.
    """

    @abstractmethod
    def to_integration_json(self) -> dict[str, Any]:
        """
        Convert the matcher to an integration JSON object.

        This method is used internally to convert the matcher to a JSON object
        which can be embedded directly in a number of places in the Pact FFI.

        For more information about this format, see the docs:

        > https://docs.pact.io/implementation_guides/rust/pact_ffi/integrationjson

        Returns:
            The matcher as an integration JSON object.
        """

    @abstractmethod
    def to_matching_rule(self) -> dict[str, Any]:
        """
        Convert the matcher to a matching rule.

        This method is used internally to convert the matcher to a matching rule
        which can be embedded directly in a Pact file.

        For more information about this format, see the docs:

        > https://github.com/pact-foundation/pact-specification/tree/version-4

        and

        > https://github.com/pact-foundation/pact-specification/tree/version-2?tab=readme-ov-file#matchers

        Returns:
            The matcher as a matching rule.
        """


class GenericMatcher(Matcher[_T]):
    """
    Generic matcher.

    A generic matcher, with the ability to define arbitrary additional fields
    for inclusion in the integration JSON object and matching rule.
    """

    def __init__(
        self,
        type: MatcherType,  # noqa: A002
        /,
        value: _T | Unset = UNSET,
        generator: Generator | None = None,
        extra_fields: Mapping[str, Any] | None = None,
        **kwargs: Matchable,
    ) -> None:
        """
        Initialize the matcher.

        Args:
            type:
                The type of the matcher.

            value:
                The value to match. If not provided, the Pact library will
                generate a value based on the matcher type (or use the generator
                if provided). To ensure reproducibility, it is _highly_
                recommended to provide a value when creating a matcher.

            generator:
                The generator to use when generating the value. The generator
                will generally only be used if value is not provided.

            extra_fields:
                Additional configuration elements to pass to the matcher. These
                fields will be used when converting the matcher to both an
                integration JSON object and a matching rule.

            **kwargs:
                Alternative way to define extra fields. See the `extra_fields`
                argument for more information.
        """
        self.type = type
        """
        The type of the matcher.
        """

        self.value: _T | Unset = value
        """
        Default value used by Pact when executing tests.
        """

        self.generator = generator
        """
        Generator used to generate a value when the value is not provided.
        """

        self._extra_fields: Mapping[str, Any] = dict(
            chain((extra_fields or {}).items(), kwargs.items())
        )

    def has_value(self) -> bool:
        """
        Check if the matcher has a value.
        """
        return not isinstance(self.value, Unset)

    def to_integration_json(self) -> dict[str, Any]:
        """
        Convert the matcher to an integration JSON object.

        This method is used internally to convert the matcher to a JSON object
        which can be embedded directly in a number of places in the Pact FFI.

        For more information about this format, see the docs:

        > https://docs.pact.io/implementation_guides/rust/pact_ffi/integrationjson

        Returns:
            dict[str, Any]:
                The matcher as an integration JSON object.
        """
        return {
            "pact:matcher:type": self.type,
            **({"value": self.value} if not isinstance(self.value, Unset) else {}),
            **(
                self.generator.to_integration_json()
                if self.generator is not None
                else {}
            ),
            **self._extra_fields,
        }

    def to_matching_rule(self) -> dict[str, Any]:
        """
        Convert the matcher to a matching rule.

        This method is used internally to convert the matcher to a matching rule
        which can be embedded directly in a Pact file.

        For more information about this format, see the docs:

        > https://github.com/pact-foundation/pact-specification/tree/version-4

        and

        > https://github.com/pact-foundation/pact-specification/tree/version-2?tab=readme-ov-file#matchers

        Returns:
            dict[str, Any]:
                The matcher as a matching rule.
        """
        return {
            "match": self.type,
            **({"value": self.value} if not isinstance(self.value, Unset) else {}),
            **self._extra_fields,
        }


class ArrayContainsMatcher(Matcher[Sequence[_T]]):
    """
    Array contains matcher.

    A matcher that checks if an array contains a value.
    """

    def __init__(self, variants: Sequence[_T | Matcher[_T]]) -> None:
        """
        Initialize the matcher.

        Args:
            variants:
                List of possible values to match against.
        """
        self._matcher: Matcher[Sequence[_T]] = GenericMatcher(
            "arrayContains",
            extra_fields={"variants": variants},
        )

    def to_integration_json(self) -> dict[str, Any]:  # noqa: D102
        return self._matcher.to_integration_json()

    def to_matching_rule(self) -> dict[str, Any]:  # noqa: D102
        return self._matcher.to_matching_rule()


class EachKeyMatcher(Matcher[Mapping[_T, Matchable]]):
    """
    Each key matcher.

    A matcher that applies a matcher to each key in a mapping.
    """

    def __init__(
        self,
        value: Mapping[_T, Matchable],
        rules: list[Matcher[_T]] | None = None,
    ) -> None:
        """
        Initialize the matcher.

        Args:
            value:
                Example value to match against.

            rules:
                List of matchers to apply to each key in the mapping.
        """
        self._matcher: Matcher[Mapping[_T, Matchable]] = GenericMatcher(
            "eachKey",
            value=value,
            extra_fields={"rules": rules},
        )

    def to_integration_json(self) -> dict[str, Any]:  # noqa: D102
        return self._matcher.to_integration_json()

    def to_matching_rule(self) -> dict[str, Any]:  # noqa: D102
        return self._matcher.to_matching_rule()


class EachValueMatcher(Matcher[Mapping[Matchable, _T]]):
    """
    Each value matcher.

    A matcher that applies a matcher to each value in a mapping.
    """

    def __init__(
        self,
        value: Mapping[Matchable, _T],
        rules: list[Matcher[_T]] | None = None,
    ) -> None:
        """
        Initialize the matcher.

        Args:
            value:
                Example value to match against.

            rules:
                List of matchers to apply to each value in the mapping.
        """
        self._matcher: Matcher[Mapping[Matchable, _T]] = GenericMatcher(
            "eachValue",
            value=value,
            extra_fields={"rules": rules},
        )

    def to_integration_json(self) -> dict[str, Any]:  # noqa: D102
        return self._matcher.to_integration_json()

    def to_matching_rule(self) -> dict[str, Any]:  # noqa: D102
        return self._matcher.to_matching_rule()


class MatchingRuleJSONEncoder(JSONEncoder):
    """
    JSON encoder class for matching rules.

    This class is used to encode matching rules to JSON.
    """

    def default(self, o: Any) -> Any:  # noqa: ANN401
        """
        Encode the object to JSON.
        """
        if isinstance(o, Matcher):
            return o.to_matching_rule()
        return super().default(o)


class IntegrationJSONEncoder(JSONEncoder):
    """
    JSON encoder class for integration JSON objects.

    This class is used to encode integration JSON objects to JSON.
    """

    def default(self, o: Any) -> Any:  # noqa: ANN401
        """
        Encode the object to JSON.
        """
        if isinstance(o, Matcher):
            return o.to_integration_json()
        if isinstance(o, Generator):
            return o.to_integration_json()
        return super().default(o)
