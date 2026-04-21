#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "tree-sitter>=0.23",
#   "tree-sitter-python>=0.23",
# ]
# ///
"""
Generate docs/ai-tools/dsl.python.md from pact-python source.

Parses the pact-python source using tree-sitter (C library via Python bindings)
and emits a DSL reference document in the same style as the other pact-*
language reference files consumed by the pactflow AI skill.

Usage (from repo root):
    uv run scripts/generate_dsl_doc.py
    uv run scripts/generate_dsl_doc.py --output path/to/output.md
    uv run scripts/generate_dsl_doc.py --check   # exit 1 if file would change
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "pact"
DEFAULT_OUT = ROOT / "docs" / "ai-tools" / "dsl.python.md"

_LANGUAGE = Language(tspython.language())
_BUILTIN_PREFIX = re.compile(r"\bbuiltins\.")


# ---------------------------------------------------------------------------
# Tree-sitter helpers
# ---------------------------------------------------------------------------


def _make_parser() -> Parser:
    return Parser(_LANGUAGE)


def _parse(rel_path: str) -> tuple[bytes, Node]:
    source = (SRC / rel_path).read_bytes()
    return source, _make_parser().parse(source).root_node


def _parse_file(path: Path) -> tuple[bytes, Node]:
    source = path.read_bytes()
    return source, _make_parser().parse(source).root_node


def _text(source: bytes, node: Node) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8")


def _norm(text: str) -> str:
    """Collapse internal whitespace to a single space."""
    return re.sub(r"\s+", " ", text).strip()


def _iter_items(source: bytes, body: Node) -> Iterator[tuple[Node, list[str]]]:
    """Yield (func_node, decorator_names) for every function in a body node."""
    for child in body.children:
        decorators: list[str] = []
        func_node: Node | None = None
        if child.type == "decorated_definition":
            for c in child.children:
                if c.type == "decorator":
                    raw = _text(source, c).lstrip("@")
                    decorators.append(re.split(r"[.(]", raw)[0].strip())
            func_node = child.child_by_field_name("definition")
        elif child.type == "function_definition":
            func_node = child
        if func_node and func_node.type == "function_definition":
            yield func_node, decorators


def _find_class(source: bytes, root: Node, class_name: str) -> Node | None:
    """Return the top-level class_definition node with the given name."""
    for child in root.children:
        candidate: Node | None = None
        if child.type == "decorated_definition":
            candidate = child.child_by_field_name("definition")
        elif child.type == "class_definition":
            candidate = child
        if candidate and candidate.type == "class_definition":
            name_node = candidate.child_by_field_name("name")
            if name_node and _text(source, name_node) == class_name:
                return candidate
    return None


def _module_funcs(source: bytes, root: Node) -> dict[str, tuple[Node, list[str]]]:
    """Return {name: (func_node, decorators)} for top-level functions."""
    result: dict[str, tuple[Node, list[str]]] = {}
    for func_node, decorators in _iter_items(source, root):
        name_node = func_node.child_by_field_name("name")
        if name_node:
            name = _text(source, name_node)
            if name not in result:
                result[name] = (func_node, decorators)
    return result


def _should_skip(source: bytes, func_node: Node, decorators: list[str]) -> bool:
    name_node = func_node.child_by_field_name("name")
    name = _text(source, name_node) if name_node else ""
    if name.startswith("_") and name != "__init__":
        return True
    return any(d in ("overload", "deprecated") for d in decorators)


def _is_trivial_alias(source: bytes, func_node: Node) -> bool:
    """True if body is `return lowercase_func(...)` (after optional docstring)."""
    body = func_node.child_by_field_name("body")
    if not body:
        return False
    stmts = []
    for child in body.children:
        if child.type in ("newline", "indent", "dedent", "comment", "pass_statement"):
            continue
        if (
            child.type == "expression_statement"
            and child.children
            and child.children[0].type == "string"
        ):
            continue  # skip docstring
        stmts.append(child)
    if len(stmts) != 1 or stmts[0].type != "return_statement":
        return False
    call_candidates = [
        c for c in stmts[0].children if c.type not in ("return", "newline")
    ]
    if not call_candidates or call_candidates[0].type != "call":
        return False
    func_part = call_candidates[0].child_by_field_name("function")
    if not func_part or func_part.type != "identifier":
        return False
    callee = _text(source, func_part)
    return bool(callee) and callee[0].islower()


def _format_params(source: bytes, params_node: Node | None) -> list[str]:
    """Return parameter strings, excluding `self` and `cls`."""
    if not params_node:
        return []
    parts: list[str] = []
    for child in params_node.children:
        if child.type in ("(", ")", ",", "comment"):
            continue
        if child.type == "identifier" and _text(source, child) in ("self", "cls"):
            continue
        if child.type in (
            "typed_parameter",
            "typed_default_parameter",
            "default_parameter",
        ):
            first_id = next((c for c in child.children if c.type == "identifier"), None)
            if first_id and _text(source, first_id) in ("self", "cls"):
                continue
        raw = _norm(_text(source, child))
        raw = _BUILTIN_PREFIX.sub("", raw)
        parts.append(raw)
    return parts


def _fmt_sig(
    source: bytes,
    func_node: Node,
    indent: int = 0,
    name_prefix: str = "",
) -> str:
    name_node = func_node.child_by_field_name("name")
    name = _text(source, name_node) if name_node else "?"
    full_name = f"{name_prefix}.{name}" if name_prefix else name
    params = _format_params(source, func_node.child_by_field_name("parameters"))
    ret_node = func_node.child_by_field_name("return_type")
    if ret_node:
        ret_text = _norm(_text(source, ret_node))
        # Strip outer parens from multi-line return annotations e.g. `-> (\n  A | B\n)`
        if ret_text.startswith("(") and ret_text.endswith(")"):
            ret_text = ret_text[1:-1].strip()
        ret = f" -> {ret_text}"
    else:
        ret = ""
    pad = " " * indent
    return f"{pad}def {full_name}({', '.join(params)}){ret}"


def _get_docstring_summary(source: bytes, func_node: Node) -> str:
    """First non-empty line of the function docstring, or ''."""
    body = func_node.child_by_field_name("body")
    if not body:
        return ""
    for child in body.children:
        if child.type != "expression_statement":
            continue
        for expr in child.children:
            if expr.type != "string":
                continue
            raw = _text(source, expr)
            for delim in ('"""', "'''", '"', "'"):
                if (
                    raw.startswith(delim)
                    and raw.endswith(delim)
                    and len(raw) > 2 * len(delim)
                ):
                    content = raw[len(delim) : -len(delim)]
                    for raw_line in content.strip().splitlines():
                        stripped = raw_line.strip().rstrip(".")
                        if stripped:
                            return stripped
                    break
        break
    return ""


# ---------------------------------------------------------------------------
# Output cleanup
# ---------------------------------------------------------------------------

_TYPE_CLEANUPS: list[tuple[str, str]] = [
    ("_UUID_FORMAT_NAMES", "Literal['simple', 'lowercase', 'uppercase', 'urn']"),
    ("_NumberT", "int | float | Decimal"),
    ("dt.date", "date"),
    ("dt.time", "time"),
    ("dt.datetime", "datetime"),
    ("pact_ffi.PactSpecification", "PactSpecification"),
    ("pact_ffi.PactHandle", "PactHandle"),
]


def _clean(text: str) -> str:
    text = _BUILTIN_PREFIX.sub("", text)
    for old, new in _TYPE_CLEANUPS:
        text = text.replace(old, new)
    return text


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------


def _class_block(
    source: bytes,
    root: Node,
    class_name: str,
    *,
    skip_init: bool = False,
    skip_aliases: bool = False,
) -> str:
    cls_node = _find_class(source, root, class_name)
    lines: list[str] = [f"class {class_name}:"]
    if not cls_node:
        return "\n".join(lines)
    body = cls_node.child_by_field_name("body")
    if not body:
        return "\n".join(lines)
    seen: set[str] = set()
    for func_node, decorators in _iter_items(source, body):
        name_node = func_node.child_by_field_name("name")
        name = _text(source, name_node) if name_node else ""
        if name in seen or _should_skip(source, func_node, decorators):
            continue
        if skip_init and name == "__init__":
            continue
        if skip_aliases and _is_trivial_alias(source, func_node):
            continue
        seen.add(name)
        if "property" in decorators:
            ret_node = func_node.child_by_field_name("return_type")
            if ret_node:
                ret_text = _norm(_text(source, ret_node))
                if ret_text.startswith("(") and ret_text.endswith(")"):
                    ret_text = ret_text[1:-1].strip()
                ret = f" -> {ret_text}"
            else:
                ret = ""
            lines.append("    @property")
            lines.append(f"    def {name}(){ret}")
        else:
            lines.append(_fmt_sig(source, func_node, indent=4))
    return "\n".join(lines)


def _func_block(
    source: bytes,
    root: Node,
    ordered_names: list[str],
    alias_map: dict[str, str] | None = None,
    module_prefix: str = "",
) -> str:
    pfx = f"{module_prefix}." if module_prefix else ""
    by_name = _module_funcs(source, root)
    lines: list[str] = []
    for name in ordered_names:
        if alias_map and name in alias_map:
            lines.append(f"def {pfx}{name}(...)  # alias for {pfx}{alias_map[name]}")
            continue
        entry = by_name.get(name)
        if entry:
            func_node, _ = entry
            lines.append(_fmt_sig(source, func_node, name_prefix=module_prefix))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Document sections
# ---------------------------------------------------------------------------


def _section_pact() -> str:
    source, root = _parse("pact.py")
    pact = _class_block(source, root, "Pact")
    server = _class_block(source, root, "PactServer", skip_init=True, skip_aliases=True)
    return f"""\
File: src/pact/pact.py
```python
# from pact import Pact
{pact}

# Obtained via pact.serve() — never instantiated directly
{server}
```"""


def _section_interaction() -> str:
    base_src, base_root = _parse("interaction/_base.py")
    http_src, http_root = _parse("interaction/_http_interaction.py")
    base_block = _class_block(base_src, base_root, "Interaction", skip_init=True)
    http_block = _class_block(
        http_src, http_root, "HttpInteraction", skip_init=True, skip_aliases=True
    )
    base_header = (
        "File: src/pact/interaction/_base.py"
        "  (shared methods — available on all interaction types)"
    )
    return f"""\
{base_header}
```python
{base_block}
```

File: src/pact/interaction/_http_interaction.py  (HTTP-specific methods)
```python
{http_block}
```"""


def _section_match() -> str:
    source, root = _parse("match/__init__.py")
    public = [
        "int",
        "integer",
        "float",
        "decimal",
        "number",
        "str",
        "string",
        "regex",
        "uuid",
        "bool",
        "boolean",
        "date",
        "time",
        "datetime",
        "timestamp",
        "none",
        "null",
        "type",
        "like",
        "each_like",
        "includes",
        "array_containing",
        "each_key_matches",
        "each_value_matches",
        "content_type",
    ]
    alias_map = {
        "integer": "int",
        "decimal": "float",
        "string": "str",
        "boolean": "bool",
        "timestamp": "datetime",
        "null": "none",
        "like": "type",
    }
    block = _func_block(
        source, root, ordered_names=public, alias_map=alias_map, module_prefix="match"
    )
    return f"""\
File: src/pact/match/__init__.py
```python
# Always import as: from pact import match
# Never: from pact.match import int  (shadows built-ins)

{block}
```"""


def _section_generate() -> str:
    source, root = _parse("generate/__init__.py")
    public = [
        "bool",
        "boolean",
        "int",
        "integer",
        "float",
        "decimal",
        "str",
        "string",
        "regex",
        "uuid",
        "date",
        "time",
        "datetime",
        "timestamp",
        "hex",
        "hexadecimal",
        "provider_state",
        "mock_server_url",
    ]
    alias_map = {
        "boolean": "bool",
        "integer": "int",
        "decimal": "float",
        "string": "str",
        "timestamp": "datetime",
        "hexadecimal": "hex",
    }
    block = _func_block(
        source,
        root,
        ordered_names=public,
        alias_map=alias_map,
        module_prefix="generate",
    )
    return f"""\
File: src/pact/generate/__init__.py
```python
# Always import as: from pact import generate
{block}
```"""


def _section_verifier() -> str:
    source, root = _parse("verifier.py")
    block = _class_block(source, root, "Verifier", skip_aliases=True)
    return f"""\
File: src/pact/verifier.py
```python
# from pact import Verifier
{block}
```"""


# ---------------------------------------------------------------------------
# Generated examples — pulled from actual source files
# ---------------------------------------------------------------------------

_MATCH_SPEC: dict[str, str] = {
    "regex": "V2",
    "like": "V2",
    "type": "V2",
    "each_like": "V2",
    "int": "V3",
    "integer": "V3",
    "float": "V3",
    "decimal": "V3",
    "number": "V3",
    "str": "V3",
    "string": "V3",
    "uuid": "V3",
    "bool": "V3",
    "boolean": "V3",
    "date": "V3",
    "time": "V3",
    "datetime": "V3",
    "timestamp": "V3",
    "none": "V3",
    "null": "V3",
    "includes": "V3",
    "array_containing": "V3",
    "each_key_matches": "V4",
    "each_value_matches": "V4",
    "content_type": "V4",
}

_MATCH_EXAMPLES: dict[str, str] = {
    "int": "match.int(42)",
    "float": "match.float(9.99)",
    "number": "match.number(42)",
    "str": "match.str('Alice')",
    "regex": r'match.regex("abc", regex=r"[a-z]+")',
    "uuid": 'match.uuid("550e…")',
    "bool": "match.bool(True)",
    "date": 'match.date("2024-07-20")',
    "time": 'match.time("14:30:00")',
    "datetime": 'match.datetime("2024-07-20T14:30:00+00:00")',
    "none": "match.none()",
    "null": "match.null()",
    "type": "match.type(val)",
    "like": "match.like(val)",
    "each_like": "match.each_like(template)",
    "includes": 'match.includes("needle")',
    "array_containing": "match.array_containing([a, b])",
    "each_key_matches": "match.each_key_matches(d, rules=r)",
    "each_value_matches": "match.each_value_matches(d, rules=r)",
    "content_type": 'match.content_type("image/jpeg")',
}

_EXAMPLE_CONSUMER = (
    ROOT / "examples" / "http" / "requests_and_fastapi" / "test_consumer.py"
)
_EXAMPLE_PROVIDER = (
    ROOT / "examples" / "http" / "requests_and_fastapi" / "test_provider.py"
)


def _extract_func_source(path: Path, func_names: list[str]) -> list[str]:
    """Return source text for the named top-level functions, in order."""
    source, root = _parse_file(path)
    target = set(func_names)
    found: dict[str, str] = {}
    for child in root.children:
        outer = child
        func_node: Node | None = None
        if child.type == "decorated_definition":
            func_node = child.child_by_field_name("definition")
        elif child.type == "function_definition":
            func_node = child
        if func_node and func_node.type == "function_definition":
            name_node = func_node.child_by_field_name("name")
            if name_node:
                name = _text(source, name_node)
                if name in target and name not in found:
                    found[name] = _text(source, outer)
    return [found[n] for n in func_names if n in found]


def _section_matcher_table() -> str:
    source, root = _parse("match/__init__.py")
    by_name = _module_funcs(source, root)
    primaries = [
        "int",
        "float",
        "number",
        "str",
        "regex",
        "uuid",
        "bool",
        "date",
        "time",
        "datetime",
        "none",
        "type",
        "like",
        "each_like",
        "includes",
        "array_containing",
        "each_key_matches",
        "each_value_matches",
        "content_type",
    ]
    rows = ["| Matcher | Min Spec | Description |", "|---|---|---|"]
    for name in primaries:
        example = _MATCH_EXAMPLES.get(name, f"match.{name}(...)")
        spec = _MATCH_SPEC.get(name, "V3")
        entry = by_name.get(name)
        desc = _get_docstring_summary(source, entry[0]) if entry else ""
        rows.append(f"| `{example}` | {spec} | {desc} |")
    notes = (
        "\n**Date/time format note**: `match.date/time/datetime` accept"
        ' Python `strftime` format strings (e.g., `"%Y-%m-%d"`) and'
        " convert them to Java `SimpleDateFormat` internally."
        " Pass `disable_conversion=True` to supply a Java format string directly."
        "\n\n**Import pattern** — always use the module, never import functions"
        " directly:\n```python\nfrom pact import match, generate   # correct"
        "\nfrom pact.match import int         # wrong — shadows built-in int\n```"
    )
    return "## Matcher Quick Reference\n\n" + "\n".join(rows) + "\n" + notes


def _section_examples() -> str:
    consumer_funcs = _extract_func_source(
        _EXAMPLE_CONSUMER, ["test_get_user", "test_create_user"]
    )
    provider_funcs = _extract_func_source(
        _EXAMPLE_PROVIDER, ["test_provider", "mock_user_exists"]
    )
    consumer_block = "\n\n".join(consumer_funcs)
    provider_block = "\n\n".join(provider_funcs)
    src_consumer = "examples/http/requests_and_fastapi/test_consumer.py"
    src_provider = "examples/http/requests_and_fastapi/test_provider.py"
    key_rules = (
        "**Key rules**:\n"
        "- Call `with_request` before `will_respond_with`. Headers/body added"
        " _before_ `will_respond_with` target the request; _after_ it, the response.\n"
        "- `pact.serve()` is a context manager; access the mock server URL"
        " via `srv.url` (a `yarl.URL`).\n"
        "- Always provide example values in matchers (`match.int(1)` not"
        " `match.int()`) to keep tests deterministic."
    )
    state_note = (
        "**State handler signatures**: when `teardown=True`, each function"
        " receives `(action: str, params: dict)` where action is"
        ' `"setup"` or `"teardown"`. When `teardown=False` (default),'
        " functions receive only `(params: dict)`."
    )
    return f"""\
---

## Consumer Tests (Python)

> Source: [`{src_consumer}`]({src_consumer})

```python
{consumer_block}
```

{key_rules}

---

## Provider Verification (Python)

> Source: [`{src_provider}`]({src_provider})

```python
{provider_block}
```

{state_note}

---

{_section_matcher_table()}"""


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def build_doc() -> str:
    """Assemble and return the full DSL reference document."""
    sections = [
        "While you already know this, here is a reminder of the key"
        " pact-python classes, methods, and functions you will need to use"
        " to create a Pact test in Python"
        " (having omitted deprecated and unadvised methods):\n",
        "> **Auto-generated** from pact-python source by `scripts/generate_dsl_doc.py`."
        " Do not edit this file directly — run the workflow or the script instead.\n",
        _section_pact(),
        _section_interaction(),
        _section_match(),
        _section_generate(),
        _section_verifier(),
        _section_examples(),
    ]
    return _clean("\n\n".join(s.rstrip() for s in sections) + "\n")


def main() -> int:
    """CLI entry point — parse args, generate, write or check."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output path")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the file would change (use in CI)",
    )
    args = parser.parse_args()
    out_path = Path(args.output)
    content = build_doc()
    if args.check:
        if out_path.exists() and out_path.read_text(encoding="utf-8") == content:
            print(f"✓ {out_path} is up to date")  # noqa: T201
            return 0
        print(  # noqa: T201
            f"✗ {out_path} is out of date — run: uv run scripts/generate_dsl_doc.py"
        )
        return 1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"Written: {out_path}")  # noqa: T201
    return 0


if __name__ == "__main__":
    sys.exit(main())
