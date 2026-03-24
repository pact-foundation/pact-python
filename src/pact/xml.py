"""
XML body builder for Pact contract testing.

This module provides builder functions for constructing XML request and response
bodies with embedded [Pact matchers][match]. It abstracts the FFI's
internal XML description format, so test authors only need to describe the XML
structure and attach matchers where desired.

```python
from pact import match, xml

response = xml.body(
    xml.element(
        "user",
        xml.element("id", match.int(123)),
        xml.element("name", match.str("Alice")),
    )
)
pact.with_body(response, content_type="application/xml")
```

The returned dict is passed to
[`with_body()`][interaction._base.Interaction.with_body] with
`content_type="application/xml"`. The Pact FFI detects the JSON-formatted body
and extracts matching rules automatically.

Individual functions can also be imported directly:

```python
from pact.xml import body, element

response = body(element("user", element("id", match.int(123))))
```
"""

from __future__ import annotations

from typing import Any, TypeAlias, Union

from pact.match.matcher import AbstractMatcher

XmlContent: TypeAlias = Union[
    "XmlElement", "AbstractMatcher[Any]", str, int, float, bool
]
"""
Valid types for element children.

These can be child elements, matchers (text with rules), or literal primitive
values (text without rules).
"""


class XmlElement:
    """
    Represents an XML element for use in Pact body descriptions.

    Do not instantiate directly, use [`element()`][element] instead.
    """

    def __init__(
        self,
        tag: str,
        *children: XmlContent,
        attrs: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialise an XML element.

        Args:
            tag:
                Element tag name, optionally including a namespace prefix
                (e.g. `"ns1:project"`).

            *children:
                Child elements or text content. Each positional argument is one
                of:

                - [`XmlElement`][XmlElement]: a nested child element.
                - [`AbstractMatcher`][match.matcher.AbstractMatcher]: text
                  content with a matching rule. The matcher's example value is
                  used as the generated text.
                - `str`, `int`, `float`, or `bool`: literal text content with
                  no matching rule.

            attrs:
                Element attributes as a mapping of attribute name to value.
                Values may be plain primitives or
                [`AbstractMatcher`][match.matcher.AbstractMatcher]
                instances. Use this parameter for namespace declarations (e.g.
                `{"xmlns:ns1": "http://..."}`) and any attribute whose name is
                not a valid Python identifier.
        """
        self._tag = tag
        self._children = children
        self._attrs: dict[str, Any] = dict(attrs) if attrs is not None else {}
        self._repeated = False
        self._min: int | None = None
        self._max: int | None = None
        self._examples: int = 1

    def each(
        self,
        *,
        min: int = 1,  # noqa: A002
        max: int | None = None,  # noqa: A002
        examples: int | None = None,
    ) -> XmlElement:
        """
        Mark this element as a type-matched repeating element.

        Causes a `type` matching rule to be registered for this element in the
        generated pact file, meaning the provider must return at least `min`
        instances of this element structure. Use `max` to also enforce an upper
        bound.

        This method is typically used when the element appears as a child
        inside another element's children list, but it can also be applied to
        the root element passed to [`body()`][body].

        Args:
            min:
                Minimum number of matching elements required in the provider
                response. Defaults to `1`.

            max:
                Maximum number of matching elements (optional).

            examples:
                Number of example copies of this element generated in the pact
                body. Defaults to `min`.

        Returns:
            `self`, to allow chaining directly after the constructor call.

        Example:
            ```python
            xml.element(
                "item",
                xml.element("id", match.int(1)),
            ).each(min=1, examples=3)
            ```
        """
        if min < 1:
            msg = f"min must be at least 1, got {min!r}."
            raise ValueError(msg)

        if max is not None and max < min:
            msg = (
                "max must be greater than or equal to min; "
                f"got min={min!r}, max={max!r}."
            )
            raise ValueError(msg)

        effective_examples = examples if examples is not None else min

        if effective_examples < min:
            msg = (
                "examples must be greater than or equal to min; "
                f"got min={min!r}, examples={effective_examples!r}."
            )
            raise ValueError(msg)

        if max is not None and effective_examples > max:
            msg = (
                "examples must be less than or equal to max when max is set; "
                f"got max={max!r}, examples={effective_examples!r}."
            )
            raise ValueError(msg)

        self._repeated = True
        self._min = min
        self._max = max
        self._examples = effective_examples
        return self

    def to_serializable_dict(self) -> dict[str, Any]:
        """
        Convert this element to a serialisable dict.

        The returned dict is suitable for
        [`IntegrationJSONEncoder`][match.matcher.IntegrationJSONEncoder].
        [`AbstractMatcher`][match.matcher.AbstractMatcher] objects within
        it are left as Python objects so that `IntegrationJSONEncoder`
        serialises them to their integration-JSON form when
        [`with_body()`][interaction._base.Interaction.with_body]
        calls `json.dumps`.

        If [`.each()`][XmlElement.each] was called on this element,
        the returned dict is wrapped in the FFI type-matcher envelope
        (`{"pact:matcher:type": "type", "value": ..., "examples": N}`).

        Returns:
            A dict representing this element in the FFI XML description format.
        """
        elem_dict = self._to_element_dict()
        if self._repeated:
            wrapper: dict[str, Any] = {
                "pact:matcher:type": "type",
                "value": elem_dict,
                "examples": self._examples,
            }
            if self._min is not None:
                wrapper["min"] = self._min
            if self._max is not None:
                wrapper["max"] = self._max
            return wrapper
        return elem_dict

    def _to_element_dict(self) -> dict[str, Any]:
        """Return the raw element dict without any repetition wrapper."""
        children_list: list[dict[str, Any]] = []
        for child in self._children:
            if isinstance(child, XmlElement):
                children_list.append(child.to_serializable_dict())
            elif isinstance(child, AbstractMatcher):
                entry: dict[str, Any] = {"matcher": child}
                if child.has_value():
                    entry["content"] = child.value  # type: ignore[attr-defined]
                children_list.append(entry)
            else:
                # Literal primitive, plain text content, no matching rule.
                children_list.append({"content": child})

        return {
            "name": self._tag,
            "children": children_list,
            "attributes": self._attrs,
        }


def element(
    tag: str,
    *children: XmlContent,
    attrs: dict[str, Any] | None = None,
) -> XmlElement:
    """
    Create an XML element for use in a Pact body description.

    Args:
        tag:
            Element tag name, optionally including a namespace prefix
            (e.g. `"ns1:project"`).

        *children:
            Child elements or text content. Each positional argument is one
            of:

            - [`XmlElement`][XmlElement]: a nested child element.
            - [`AbstractMatcher`][match.matcher.AbstractMatcher]: text
              content with a matching rule. The example value is taken from the
              matcher.
            - `str`, `int`, `float`, or `bool`: literal text content with no
              matching rule.

        attrs:
            Element attributes as a mapping of attribute name to value. Values
            may be [`AbstractMatcher`][match.matcher.AbstractMatcher]
            instances or plain primitives. Required for namespace declarations
            (e.g. `{"xmlns:ns1": "http://..."}`) and attribute names that are
            not valid Python identifiers.

    Returns:
        An [`XmlElement`][XmlElement] instance.

    Example:
        ```python
        from pact import match, xml

        xml.element(
            "user",
            xml.element("id", match.int(123)),
            xml.element("name", match.str("Alice")),
            attrs={"xmlns:ns1": "http://some.namespace/"},
        )
        ```
    """
    return XmlElement(tag, *children, attrs=attrs)


def body(root: XmlElement) -> dict[str, Any]:
    """
    Wrap a root [`XmlElement`][XmlElement] as an XML body description.

    The returned dict is suitable for passing to
    [`with_body()`][interaction._base.Interaction.with_body]
    with `content_type="application/xml"`. The Pact FFI detects the
    JSON-formatted body, generates the example XML, and extracts matching rules
    into the contract file.

    Args:
        root:
            The root element of the XML body.

    Returns:
        A dict in the FFI XML description format, ready for
        `with_body(result, content_type="application/xml")`.

    Example:
        ```python
        from pact import match, xml

        response = xml.body(
            xml.element(
                "user",
                xml.element("id", match.int(123)),
                xml.element("name", match.str("Alice")),
            )
        )
        pact.with_body(response, content_type="application/xml")
        ```
    """
    return {"root": root.to_serializable_dict()}
