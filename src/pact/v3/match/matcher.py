"""
Matching functionality for Pact.

Matchers are used in Pact to allow for more flexible matching of data. While the
consumer defines the expected request and response, there are circumstances
where the provider may return dynamically generated data. In these cases, the
consumer should use a matcher to define the expected data.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import chain
from json import JSONEncoder
from typing import TYPE_CHECKING, Any, Generic

from pact.v3.generate.generator import Generator
from pact.v3.types import UNSET, Matchable, MatchableT, MatcherType, Unset

if TYPE_CHECKING:
    from collections.abc import Mapping


class Matcher(ABC, Generic[MatchableT]):
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


class GenericMatcher(Matcher[MatchableT]):
    """
    Generic matcher.

    A generic matcher, with the ability to define arbitrary additional fields
    for inclusion in the integration JSON object and matching rule.
    """

    def __init__(  # noqa: PLR0913
        self,
        type: MatcherType,  # noqa: A002
        /,
        value: MatchableT | Unset = UNSET,
        generator: Generator[MatchableT] | None = None,
        extra_fields: Mapping[str, Any] | None = None,
        integration_fields: Mapping[str, Any] | None = None,
        matching_rule_fields: Mapping[str, Any] | None = None,
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

            integration_fields:
                Additional configuration elements to pass to the matcher when
                converting it to an integration JSON object.

            matching_rule_fields:
                Additional configuration elements to pass to the matcher when
                converting it to a matching rule.

            **kwargs:
                Alternative way to define extra fields. See the `extra_fields`
                argument for more information.
        """
        self.type = type
        """
        The type of the matcher.
        """

        self.value: MatchableT | Unset = value
        """
        Default value used by Pact when executing tests.
        """

        self.generator: Generator[MatchableT] | None = generator
        """
        Generator used to generate a value when the value is not provided.
        """

        self._integration_fields = integration_fields or {}
        self._matching_rule_fields = matching_rule_fields or {}
        self._extra_fields = dict(chain((extra_fields or {}).items(), kwargs.items()))

    def has_value(self) -> bool:
        """
        Check if the matcher has a value.
        """
        return not isinstance(self.value, Unset)

    def to_integration_json(self) -> dict[str, Matchable]:
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
            **self._integration_fields,
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
            **self._matching_rule_fields,
        }


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
