"""
Unit tests for the :mod:`pact.xml` XML body builder.
"""

from __future__ import annotations

import json

import pytest

from pact import match, xml
from pact.match.matcher import AbstractMatcher, IntegrationJSONEncoder
from pact.xml import XmlElement, body, element


class TestElement:
    """Tests for :func:`pact.xml.element`."""

    def test_returns_xml_element(self) -> None:
        result = element("id", 1)
        assert isinstance(result, XmlElement)

    def test_literal_text_content(self) -> None:
        result = body(element("id", 123))
        assert result == {
            "root": {
                "name": "id",
                "children": [{"content": 123}],
                "attributes": {},
            }
        }

    def test_literal_string_content(self) -> None:
        result = body(element("name", "Alice"))
        assert result == {
            "root": {
                "name": "name",
                "children": [{"content": "Alice"}],
                "attributes": {},
            }
        }

    def test_matcher_text_content_includes_content_and_matcher(self) -> None:
        m = match.int(123)
        result = body(element("id", m))
        children = result["root"]["children"]
        assert len(children) == 1
        assert children[0]["content"] == 123
        assert children[0]["matcher"] is m

    def test_matcher_text_content_is_abstract_matcher(self) -> None:
        result = body(element("id", match.int(123)))
        matcher = result["root"]["children"][0]["matcher"]
        assert isinstance(matcher, AbstractMatcher)

    def test_matcher_without_value_omits_content(self) -> None:
        # match.int() with no value uses a generator
        m = match.int()
        result = body(element("id", m))
        children = result["root"]["children"]
        assert "content" not in children[0]
        assert children[0]["matcher"] is m

    def test_container_element_with_children(self) -> None:
        result = body(
            element(
                "user",
                element("id", 123),
                element("name", "Alice"),
            )
        )
        root = result["root"]
        assert root["name"] == "user"
        assert root["children"][0]["name"] == "id"
        assert root["children"][1]["name"] == "name"
        assert root["attributes"] == {}

    def test_empty_element(self) -> None:
        result = body(element("empty"))
        assert result == {
            "root": {
                "name": "empty",
                "children": [],
                "attributes": {},
            }
        }

    def test_attrs_plain_values(self) -> None:
        result = body(element("user", attrs={"id": "1", "version": "2"}))
        assert result["root"]["attributes"] == {"id": "1", "version": "2"}

    def test_attrs_with_matcher(self) -> None:
        m = match.int(1)
        result = body(element("user", attrs={"id": m}))
        assert result["root"]["attributes"]["id"] is m

    def test_attrs_none_gives_empty_dict(self) -> None:
        result = body(element("tag"))
        assert result["root"]["attributes"] == {}

    def test_namespace_declaration_in_attrs(self) -> None:
        result = body(
            element("ns1:projects", attrs={"xmlns:ns1": "http://example.com/"})
        )
        assert result["root"]["attributes"]["xmlns:ns1"] == "http://example.com/"


class TestEach:
    """Tests for :meth:`XmlElement.each`."""

    def test_each_returns_self(self) -> None:
        elem = element("item", 1)
        result = elem.each(min=1)
        assert result is elem

    def test_each_wraps_element_in_type_matcher(self) -> None:
        elem = element("item", element("id", 1)).each(min=1)
        result = body(elem)
        root = result["root"]
        assert root["pact:matcher:type"] == "type"
        assert root["min"] == 1
        assert root["value"]["name"] == "item"

    def test_each_default_examples_equals_min(self) -> None:
        elem = element("item").each(min=3)
        result = body(elem)
        assert result["root"]["examples"] == 3

    def test_each_explicit_examples(self) -> None:
        elem = element("item").each(min=2, examples=5)
        result = body(elem)
        assert result["root"]["examples"] == 5
        assert result["root"]["min"] == 2

    def test_each_with_max(self) -> None:
        elem = element("item").each(min=1, max=10)
        result = body(elem)
        assert result["root"]["min"] == 1
        assert result["root"]["max"] == 10

    def test_each_without_max_omits_max_key(self) -> None:
        elem = element("item").each(min=1)
        result = body(elem)
        assert "max" not in result["root"]

    def test_each_raises_when_min_less_than_1(self) -> None:
        with pytest.raises(ValueError, match="min must be at least 1"):
            element("item").each(min=0)

    def test_each_raises_when_max_less_than_min(self) -> None:
        with pytest.raises(
            ValueError, match="max must be greater than or equal to min"
        ):
            element("item").each(min=3, max=2)

    def test_each_raises_when_examples_less_than_min(self) -> None:
        with pytest.raises(
            ValueError, match="examples must be greater than or equal to min"
        ):
            element("item").each(min=3, examples=2)

    def test_each_raises_when_examples_exceed_max(self) -> None:
        with pytest.raises(
            ValueError, match="examples must be less than or equal to max"
        ):
            element("item").each(min=1, max=3, examples=5)

    def test_each_as_child_wraps_in_type_matcher(self) -> None:
        result = body(
            element(
                "items",
                element("item", element("id", 1)).each(min=2),
            )
        )
        child = result["root"]["children"][0]
        assert child["pact:matcher:type"] == "type"
        assert child["min"] == 2
        assert child["value"]["name"] == "item"


class TestBody:
    """Tests for :func:`pact.xml.body`."""

    def test_wraps_in_root_key(self) -> None:
        result = body(element("foo"))
        assert "root" in result
        assert result["root"]["name"] == "foo"

    def test_returns_dict(self) -> None:
        result = body(element("foo"))
        assert isinstance(result, dict)


class TestIntegration:
    """Integration: body() output survives json.dumps with IntegrationJSONEncoder."""

    def test_json_serialises_matchers(self) -> None:
        result = body(
            element(
                "user",
                element("id", match.int(123)),
                element("name", match.str("Alice")),
            )
        )
        serialised = json.dumps(result, cls=IntegrationJSONEncoder)
        parsed = json.loads(serialised)

        id_child = parsed["root"]["children"][0]
        assert id_child["name"] == "id"
        assert id_child["children"][0]["content"] == 123
        assert id_child["children"][0]["matcher"]["pact:matcher:type"] == "integer"

        name_child = parsed["root"]["children"][1]
        assert name_child["children"][0]["matcher"]["pact:matcher:type"] == "type"

    def test_module_access_via_pact_xml(self) -> None:
        result = xml.body(xml.element("user", xml.element("id", match.int(1))))
        assert result["root"]["name"] == "user"

    def test_direct_import(self) -> None:
        result = body(element("user", element("id", 1)))
        assert result["root"]["name"] == "user"
