"""
Rewrite links to docs.

This hook is used to rewrite links within the documentation. Due to the way
Markdown files are collected across the repository (specifically, within `docs/`
and outside of `docs/`), links that cross this boundary don't already work
correctly.

This hook is used to rewrite links dynamically.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import mkdocs.plugins

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page


@mkdocs.plugins.event_priority(-50)
def on_page_markdown(
    markdown: str,
    page: Page,  # noqa: ARG001
    config: MkDocsConfig,  # noqa: ARG001
    files: Files,  # noqa: ARG001
) -> str | None:
    """
    Rewrite links to docs.

    Performs a simple regex substitution on the Markdown content. Specifically,
    any link to a file within `docs/{path}` is rewritten to just `/{path}`, and
    any links containing `../docs/..` are rewritten to just `../..`.

    This is clearly fragile, but until a better solution is needed, this should
    be sufficient.
    """
    # Find all links that start with `docs/` and rewrite them.
    markdown = re.sub(
        r"\]\((?P<link>docs/[^)]+)\)",
        lambda match: f"]({match.group('link')[5:]})",
        markdown,
        count=0,
        flags=re.MULTILINE,
    )

    # Find links that have an embedded `/docs/` and rewrite them.
    return re.sub(
        r"\]\((?P<link>[^)]+/docs/[^)]+)\)",
        lambda match: f"]({match.group('link').replace('/docs/', '/')})",
        markdown,
        count=0,
        flags=re.MULTILINE,
    )
