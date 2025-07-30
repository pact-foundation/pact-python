"""
Error classes for Pact.
"""

from __future__ import annotations

import copy
import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class PactError(Exception, ABC):
    """
    Base class for exceptions raised by the Pact module.
    """


class InteractionVerificationError(PactError):
    """
    Exception raised due during the verification of an interaction.

    This error is raised when an error occurs during the manual verification of an
    interaction. This is typically raised when the consumer fails to handle the
    interaction correctly thereby generating its own exception. The cause of the
    error is stored in the `error` attribute.
    """

    def __init__(self, description: str, error: Exception) -> None:
        """
        Initialise a new InteractionVerificationError.

        Args:
            description:
                Description of the interaction that failed verification.

            error: Error that occurred during the verification of the
                interaction.
        """
        super().__init__(f"Error verifying interaction '{description}': {error}")
        self._description = description
        self._error = error

    @property
    def description(self) -> str:
        """
        Description of the interaction that failed verification.
        """
        return self._description

    @property
    def error(self) -> Exception:
        """
        Error that occurred during the verification of the interaction.
        """
        return self._error


class PactVerificationError(PactError):
    """
    Exception raised due to errors in the verification of a Pact.

    This is raised when performing manual verification of the Pact through the
    [`verify`][pact.v3.Pact.verify] method:

    ```python
    pact = Pact("consumer", "provider")
    # Define interactions...
    try:
        pact.verify(handler, kind="Async")
    except PactVerificationError as e:
        print(e.errors)
    ```

    All of the errors that occurred during the verification of all of the
    interactions are stored in the `errors` attribute.

    This is different from the [`MismatchesError`][pact.v3.MismatchesError]
    which is raised when there are mismatches detected by the mock server.
    """

    def __init__(self, errors: list[InteractionVerificationError]) -> None:
        """
        Initialise a new PactVerificationError.

        Args:
            errors:
                Errors that occurred during the verification of the Pact.
        """
        super().__init__(f"Error verifying Pact (count: {len(errors)})")
        self._errors = errors

    @property
    def errors(self) -> list[InteractionVerificationError]:
        """
        Errors that occurred during the verification of the Pact.
        """
        return self._errors


class Mismatch(ABC):
    """
    A mismatch between the Pact contract and the actual interaction.

    See
    https://github.com/pact-foundation/pact-reference/blob/f5ddf3d353149ae0fb539a1616eeb8544509fdfc/rust/pact_matching/src/lib.rs#L880
    for the underlying source of the data.
    """

    @property
    @abstractmethod
    def type(self) -> str:
        """
        Type of the mismatch.
        """

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Mismatch:  # noqa: C901, PLR0911
        """
        Create a new Mismatch from a dictionary.

        Args:
            data:
                Data for the mismatch.

        Returns:
            A new Mismatch object.
        """
        if "type" in data:
            mismatch_type = data.pop("type")
            # Pact mismatches
            if mismatch_type in ["MissingRequest", "missing-request"]:
                return MissingRequest(**data)
            if mismatch_type in ["RequestNotFound", "request-not-found"]:
                return RequestNotFound(**data)
            if mismatch_type in ["RequestMismatch", "request-mismatch"]:
                return RequestMismatch(**data)

            # Interaction mismatches
            if mismatch_type in ["MethodMismatch", "method-mismatch"]:
                return MethodMismatch(**data)
            if mismatch_type in ["PathMismatch", "path-mismatch"]:
                return PathMismatch(**data)
            if mismatch_type in ["StatusMismatch", "status-mismatch"]:
                return StatusMismatch(**data)
            if mismatch_type in ["QueryMismatch", "query-mismatch"]:
                return QueryMismatch(**data)
            if mismatch_type in ["HeaderMismatch", "header-mismatch"]:
                return HeaderMismatch(**data)
            if mismatch_type in ["BodyTypeMismatch", "body-type-mismatch"]:
                return BodyTypeMismatch(**data)
            if mismatch_type in ["BodyMismatch", "body-mismatch"]:
                return BodyMismatch(**data)
            if mismatch_type in ["MetadataMismatch", "metadata-mismatch"]:
                return MetadataMismatch(**data)
                logger.warning("RequestMismatch not implemented")

            logger.warning("Unknown mismatch type: %s (%r)", mismatch_type, data)
            return GenericMismatch(**data, type=mismatch_type)
        return GenericMismatch(**data)


class GenericMismatch(Mismatch):
    """
    Generic mismatch between the Pact contract and the actual interaction.

    This is used when the mismatch is not otherwise covered by a specific
    mismatch below.
    """

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Initialise a new GenericMismatch.

        Args:
            kwargs:
                Data for the mismatch.
        """
        self._data = kwargs

    @property
    def type(self) -> str:
        """
        Type of the mismatch.
        """
        return self._data.get("type", "UnknownMismatchType")

    def __repr__(self) -> str:
        """
        Information-rich string representation of the GenericMismatch.
        """
        return f"<GenericMismatch: {self.type!r}>"

    def __str__(self) -> str:
        """
        Informal string representation of the GenericMismatch.
        """
        return f"Generic mismatch ({self.type}): {self._data}"


class MissingRequest(Mismatch):
    """
    Mismatch due to a missing request.
    """

    def __init__(self, method: str, path: str, request: dict[str, Any]) -> None:
        """
        Initialise a new MissingRequest.

        Args:
            method:
                HTTP method of the missing request.

            path:
                Path of the missing request.

            request:
                Details of the missing request.
        """
        self._method = method
        self._path = path
        self._request = request

    @property
    def type(self) -> str:
        """
        Type of the mismatch.
        """
        return "MissingRequest"

    @property
    def method(self) -> str:
        """
        HTTP method of the missing request.
        """
        return self._method

    @property
    def path(self) -> str:
        """
        Path of the missing request.
        """
        return self._path

    @property
    def request(self) -> dict[str, Any]:
        """
        Details of the missing request.
        """
        return self._request

    def __repr__(self) -> str:
        """
        Information-rich string representation of the MissingRequest.
        """
        return "<MissingRequest: {}>".format(
            ", ".join([
                f"method={self.method!r}",
                f"path={self.path!r}",
                f"request={self.request!r}",
            ])
        )

    def __str__(self) -> str:
        """
        Informal string representation of the MissingRequest.
        """
        extra = copy.deepcopy(self.request)
        extra.pop("method")
        extra.pop("path")
        return f"Missing request: {self.method} {self.path}: {extra}"


class RequestNotFound(Mismatch):
    """
    Mismatch due to a request not being found.
    """

    def __init__(self, method: str, path: str, request: dict[str, Any]) -> None:
        """
        Initialise a new RequestNotFound.

        Args:
            method:
                HTTP method of the request not found.

            path:
                Path of the request not found.

            request:
                Details of the request not found.
        """
        self._method = method
        self._path = path
        self._request = request

    @property
    def type(self) -> str:
        """
        Type of the mismatch.
        """
        return "RequestNotFound"

    @property
    def method(self) -> str:
        """
        HTTP method of the request not found.
        """
        return self._method

    @property
    def path(self) -> str:
        """
        Path of the request not found.
        """
        return self._path

    @property
    def request(self) -> dict[str, Any]:
        """
        Details of the request not found.
        """
        return self._request

    def __repr__(self) -> str:
        """
        Information-rich string representation of the RequestNotFound.
        """
        return "<RequestNotFound: {}>".format(
            ", ".join([
                f"method={self.method!r}",
                f"path={self.path!r}",
                f"request={self.request!r}",
            ])
        )

    def __str__(self) -> str:
        """
        Informal string representation of the RequestNotFound.
        """
        extra = copy.deepcopy(self.request)
        extra.pop("method")
        extra.pop("path")
        return f"Request not found: {self.method} {self.path}: {extra}"


class RequestMismatch(Mismatch):
    """
    Mismatch due to an incorrect request.
    """

    def __init__(
        self, method: str, path: str, mismatches: list[dict[str, Any]]
    ) -> None:
        """
        Initialise a new RequestMismatch.

        Args:
            method:
                HTTP method of the request.

            path:
                Path of the request.

            mismatches:
                List of mismatches in the request.
        """
        self._method = method
        self._path = path
        self._mismatches = [Mismatch.from_dict(m) for m in mismatches]

    @property
    def type(self) -> str:
        """
        Type of the mismatch.
        """
        return "RequestMismatch"

    @property
    def method(self) -> str:
        """
        HTTP method of the request.
        """
        return self._method

    @property
    def path(self) -> str:
        """
        Path of the request.
        """
        return self._path

    @property
    def mismatches(self) -> list[Mismatch]:
        """
        List of mismatches in the request.
        """
        return self._mismatches

    def __repr__(self) -> str:
        """
        Information-rich string representation of the RequestMismatch.
        """
        return "<RequestMismatch: {}>".format(
            ", ".join([
                f"method={self.method!r}",
                f"path={self.path!r}",
                f"mismatches={self.mismatches!r}",
            ])
        )

    def __str__(self) -> str:
        """
        Informal string representation of the RequestMismatch.
        """
        return "\n".join([
            f"Request mismatch: {self.method} {self.path}",
            *(f"    ({i + 1}) {m}" for i, m in enumerate(self.mismatches)),
        ])


class MethodMismatch(Mismatch):
    """
    Mismatch due to an incorrect HTTP method.
    """

    def __init__(self, expected: str, actual: str) -> None:
        """
        Initialise a new MethodMismatch.

        Args:
            expected:
                Expected HTTP method.

            actual:
                Actual HTTP method.
        """
        self._expected = expected
        self._actual = actual

    @property
    def type(self) -> str:
        """
        Type of the mismatch.
        """
        return "MethodMismatch"

    @property
    def expected(self) -> str:
        """
        Expected HTTP method.
        """
        return self._expected

    @property
    def actual(self) -> str:
        """
        Actual HTTP method.
        """
        return self._actual

    def __repr__(self) -> str:
        """
        Information-rich string representation of the MethodMismatch.
        """
        return f"<MethodMismatch: expected={self.expected!r}, actual={self.actual!r}>"

    def __str__(self) -> str:
        """
        Informal string representation of the MethodMismatch.
        """
        return f"Method mismatch: expected {self.expected}, got {self.actual}"


class PathMismatch(Mismatch):
    """
    Mismatch due to an incorrect path.
    """

    def __init__(self, expected: str, actual: str, mismatch: str) -> None:
        """
        Initialise a new PathMismatch.

        Args:
            expected:
                Expected path.

            actual:
                Actual path.

            mismatch:
                Mismatch between the expected and actual paths.
        """
        self._expected = expected
        self._actual = actual
        self._mismatch = mismatch

    @property
    def type(self) -> str:
        """
        Type of the mismatch.
        """
        return "PathMismatch"

    @property
    def expected(self) -> str:
        """
        Expected path.
        """
        return self._expected

    @property
    def actual(self) -> str:
        """
        Actual path.
        """
        return self._actual

    @property
    def mismatch(self) -> str:
        """
        Mismatch between the expected and actual paths.
        """
        return self._mismatch

    def __repr__(self) -> str:
        """
        Information-rich string representation of the PathMismatch.
        """
        return "<PathMismatch: {}>".format(
            ", ".join([
                f"expected={self.expected!r}",
                f"actual={self.actual!r}",
                f"mismatch={self.mismatch!r}",
            ])
        )

    def __str__(self) -> str:
        """
        Informal string representation of the PathMismatch.
        """
        return (
            "Path mismatch: "
            f"expected {self.expected}, got {self.actual} "
            f"({self.mismatch})"
        )


class StatusMismatch(Mismatch):
    """
    Mismatch due to an incorrect HTTP status code.
    """

    def __init__(self, expected: int, actual: int, mismatch: str) -> None:
        """
        Initialise a new StatusMismatch.

        Args:
            expected:
                Expected HTTP status code.

            actual:
                Actual HTTP status code.

            mismatch:
                Description of the mismatch.
        """
        self._expected = expected
        self._actual = actual
        self._mismatch = mismatch

    @property
    def type(self) -> str:
        """
        Type of the mismatch.
        """
        return "StatusMismatch"

    @property
    def expected(self) -> int:
        """
        Expected HTTP status code.
        """
        return self._expected

    @property
    def actual(self) -> int:
        """
        Actual HTTP status code.
        """
        return self._actual

    @property
    def mismatch(self) -> str:
        """
        Description of the mismatch.
        """
        return self._mismatch

    def __repr__(self) -> str:
        """
        Information-rich string representation of the StatusMismatch.
        """
        return "<StatusMismatch: {}>".format(
            ", ".join([
                f"expected={self.expected!r}",
                f"actual={self.actual!r}",
                f"mismatch={self.mismatch!r}",
            ])
        )

    def __str__(self) -> str:
        """
        Informal string representation of the StatusMismatch.
        """
        return (
            "Status mismatch: "
            f"expected {self.expected}, got {self.actual} "
            f"({self.mismatch})"
        )


class QueryMismatch(Mismatch):
    """
    Mismatch due to an incorrect query parameter.
    """

    def __init__(
        self,
        parameter: str,
        expected: str,
        actual: str,
        mismatch: str,
    ) -> None:
        """
        Initialise a new QueryMismatch.

        Args:
            parameter:
                Query parameter name.

            expected:
                Expected value of the query parameter.

            actual:
                Actual value of the query parameter.

            mismatch:
                Description of the mismatch.
        """
        self._parameter = parameter
        self._expected = expected
        self._actual = actual
        self._mismatch = mismatch

    @property
    def type(self) -> str:
        """
        Type of the mismatch.
        """
        return "QueryMismatch"

    @property
    def parameter(self) -> str:
        """
        Query parameter name.
        """
        return self._parameter

    @property
    def expected(self) -> str:
        """
        Expected value of the query parameter.
        """
        return self._expected

    @property
    def actual(self) -> str:
        """
        Actual value of the query parameter.
        """
        return self._actual

    @property
    def mismatch(self) -> str:
        """
        Description of the mismatch.
        """
        return self._mismatch

    def __repr__(self) -> str:
        """
        Information-rich string representation of the QueryMismatch.
        """
        return "<QueryMismatch: {}>".format(
            ", ".join([
                f"parameter={self.parameter!r}",
                f"expected={self.expected!r}",
                f"actual={self.actual!r}",
                f"mismatch={self.mismatch!r}",
            ])
        )

    def __str__(self) -> str:
        """
        Informal string representation of the QueryMismatch.
        """
        return f"Query mismatch: {self.mismatch}"


class HeaderMismatch(Mismatch):
    """
    Mismatch due to an incorrect header.
    """

    def __init__(self, key: str, expected: str, actual: str, mismatch: str) -> None:
        """
        Initialise a new HeaderMismatch.

        Args:
            key:
                Header key.

            expected:
                Expected value of the header.

            actual:
                Actual value of the header.

            mismatch:
                Description of the mismatch.
        """
        self._key = key
        self._expected = expected
        self._actual = actual
        self._mismatch = mismatch

    @property
    def type(self) -> str:
        """
        Type of the mismatch.
        """
        return "HeaderMismatch"

    @property
    def key(self) -> str:
        """
        Header key.
        """
        return self._key

    @property
    def expected(self) -> str:
        """
        Expected value of the header.
        """
        return self._expected

    @property
    def actual(self) -> str:
        """
        Actual value of the header.
        """
        return self._actual

    @property
    def mismatch(self) -> str:
        """
        Description of the mismatch.
        """
        return self._mismatch

    def __repr__(self) -> str:
        """
        Information-rich string representation of the HeaderMismatch.
        """
        return "<HeaderMismatch: {}>".format(
            ", ".join([
                f"key={self.key!r}",
                f"expected={self.expected!r}",
                f"actual={self.actual!r}",
                f"mismatch={self.mismatch!r}",
            ])
        )

    def __str__(self) -> str:
        """
        Informal string representation of the HeaderMismatch.
        """
        return f"Header mismatch: {self.mismatch}"


class BodyTypeMismatch(Mismatch):
    """
    Mismatch due to an incorrect content type of the body.
    """

    def __init__(  # noqa: PLR0913
        self,
        expected: str,
        actual: str,
        mismatch: str,
        expected_body: bytes | None = None,
        expectedBody: bytes | None = None,  # noqa: N803
        actual_body: bytes | None = None,
        actualBody: bytes | None = None,  # noqa: N803
    ) -> None:
        """
        Initialise a new BodyTypeMismatch.

        Args:
            expected:
                Expected content type of the body.

            actual:
                Actual content type of the body.

            mismatch:
                Description of the mismatch.

            expected_body:
                Expected body content.

            actual_body:
                Actual body content.

            expectedBody:
                Alias for `expected_body`.

            actualBody:
                Alias for `actual_body`.
        """
        self._expected = expected
        self._actual = actual
        self._mismatch = mismatch
        self._expected_body = expected_body or expectedBody
        self._actual_body = actual_body or actualBody

    @property
    def type(self) -> str:
        """
        Type of the mismatch.
        """
        return "BodyTypeMismatch"

    @property
    def expected(self) -> str:
        """
        Expected content type of the body.
        """
        return self._expected

    @property
    def actual(self) -> str:
        """
        Actual content type of the body.
        """
        return self._actual

    @property
    def mismatch(self) -> str:
        """
        Description of the mismatch.
        """
        return self._mismatch

    @property
    def expected_body(self) -> bytes | None:
        """
        Expected body content.
        """
        return self._expected_body

    @property
    def actual_body(self) -> bytes | None:
        """
        Actual body content.
        """
        return self._actual_body

    def __repr__(self) -> str:
        """
        Information-rich string representation of the BodyTypeMismatch.
        """
        return "<BodyTypeMismatch: {}>".format(
            ", ".join([
                f"expected={self.expected!r}",
                f"actual={self.actual!r}",
                f"mismatch={self.mismatch!r}",
                f"expected_body={self.expected_body!r}",
                f"actual_body={self.actual_body!r}",
            ])
        )

    def __str__(self) -> str:
        """
        Informal string representation of the BodyTypeMismatch.
        """
        return f"Body type mismatch: {self.mismatch}"


class BodyMismatch(Mismatch):
    """
    Mismatch due to an incorrect body element.
    """

    def __init__(
        self,
        path: str,
        expected: str,
        actual: str,
        mismatch: str,
    ) -> None:
        """
        Initialise a new BodyMismatch.

        Args:
            path:
                Path expression to where the mismatch occurred.

            expected:
                Expected value.

            actual:
                Actual value.

            mismatch:
                Description of the mismatch.
        """
        self._path = path
        self._expected = expected
        self._actual = actual
        self._mismatch = mismatch

    @property
    def type(self) -> str:
        """
        Type of the mismatch.
        """
        return "BodyMismatch"

    @property
    def path(self) -> str:
        """
        Path expression to where the mismatch occurred.
        """
        return self._path

    @property
    def expected(self) -> str:
        """
        Expected value.
        """
        return self._expected

    @property
    def actual(self) -> str:
        """
        Actual value.
        """
        return self._actual

    @property
    def mismatch(self) -> str:
        """
        Description of the mismatch.
        """
        return self._mismatch

    def __repr__(self) -> str:
        """
        Information-rich string representation of the BodyMismatch.
        """
        return "<BodyMismatch: {}>".format(
            ", ".join([
                f"path={self.path!r}",
                f"expected={self.expected!r}",
                f"actual={self.actual!r}",
                f"mismatch={self.mismatch!r}",
            ])
        )

    def __str__(self) -> str:
        """
        Informal string representation of the BodyMismatch.
        """
        return f"Body mismatch: {self.mismatch}"


class MetadataMismatch(Mismatch):
    """
    Mismatch due to incorrect message metadata.
    """

    def __init__(self, key: str, expected: str, actual: str, mismatch: str) -> None:
        """
        Initialise a new MetadataMismatch.

        Args:
            key:
                Metadata key.

            expected:
                Expected value.

            actual:
                Actual value.

            mismatch:
                Description of the mismatch.
        """
        self._key = key
        self._expected = expected
        self._actual = actual
        self._mismatch = mismatch

    @property
    def type(self) -> str:
        """
        Type of the mismatch.
        """
        return "MetadataMismatch"

    @property
    def key(self) -> str:
        """
        Metadata key.
        """
        return self._key

    @property
    def expected(self) -> str:
        """
        Expected value.
        """
        return self._expected

    @property
    def actual(self) -> str:
        """
        Actual value.
        """
        return self._actual

    @property
    def mismatch(self) -> str:
        """
        Description of the mismatch.
        """
        return self._mismatch

    def __repr__(self) -> str:
        """
        Information-rich string representation of the MetadataMismatch.
        """
        return "<MetadataMismatch: {}>".format(
            ", ".join([
                f"key={self.key!r}",
                f"expected={self.expected!r}",
                f"actual={self.actual!r}",
                f"mismatch={self.mismatch!r}",
            ])
        )

    def __str__(self) -> str:
        """
        Informal string representation of the MetadataMismatch.
        """
        return (
            "Metadata mismatch: "
            f"{self.key}: expected {self.expected}, got {self.actual} "
            f"({self.mismatch})"
        )


class MismatchesError(PactError):
    """
    Exception raised when there are mismatches between the Pact and the server.
    """

    def __init__(self, *mismatches: Mismatch | dict[str, Any]) -> None:
        """
        Initialise a new MismatchesError.

        Args:
            mismatches:
                Mismatches between the Pact and the server.
        """
        super().__init__(f"Mismatched interaction (count: {len(mismatches)})")
        self._mismatches = [
            m if isinstance(m, Mismatch) else Mismatch.from_dict(m) for m in mismatches
        ]

    @property
    def mismatches(self) -> list[Mismatch]:
        """
        Mismatches between the Pact and the server.
        """
        return self._mismatches

    def __repr__(self) -> str:
        """
        Information-rich string representation of the MismatchesError.
        """
        return "<MismatchesError: {}>".format(
            [f"{m!r}" for m in self._mismatches],
        )

    def __str__(self) -> str:
        """
        Informal string representation of the MismatchesError.
        """
        return "\n".join([
            "Mismatches:",
            *(f"  ({i + 1}) {m}" for i, m in enumerate(self._mismatches)),
        ])
