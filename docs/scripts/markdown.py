"""
Script to merge Markdown documentation from the main codebase into the docs.

This script is run by mkdocs-gen-files when the documentation is built and
imports Markdown documentation from the main codebase so that it can be included
in the documentation site. For example, a Markdown file located at
`some/path/foo.md` will be treated as if it was located at
`docs/some/path/foo.md` without the need for symlinks or copying the file.

If the destination file already exists (either because it is a real file, or was
otherwise already generated), the script will raise a RuntimeError.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

import mkdocs_gen_files
from mkdocs_gen_files.editor import FilesEditor
from pathspec import PathSpec

if TYPE_CHECKING:
    from collections.abc import Sequence

EDITOR = FilesEditor.current()
_T = TypeVar("_T")


def is_subsequence(a: Sequence[_T], b: Sequence[_T]) -> int | None:
    """
    Checks if a is a sublist of b.

    This will return the index of the first element of a in b if a is a sublist
    of b, or None otherwise.
    """
    if len(a) > len(b):
        return None
    for i in range(len(b) - len(a) + 1):
        if all(a[j] == b[i + j] for j in range(len(a))):
            return i
    return None


def process_markdown(
    src: str,
    ignore: list[str] | None = None,
    mapping: list[tuple[str, str]] | None = None,
) -> None:
    """
    Process out-of-docs Markdown files.

    The source directory is relative to the root of the repository, and only
    Markdown files which are version controlled are processed. Once processed,
    they will be available to MkDocs as if they were located in the `docs`
    directory.

    Args:
        src:
            The source directory to process.

        ignore:
            A list of patterns to ignore. This uses the same syntax as `.gitignore`.

        mapping:
            List of tuples containing the source and destination paths to map.
            Note that the list is processed in order, with later mappings
            applied after earlier mappings.
    """
    ignore_spec = PathSpec.from_lines("gitwildmatch", ignore or [])
    mapping_parts: list[tuple[Sequence[str], Sequence[str]]] = [
        (Path(a).parts, Path(b).parts) for a, b in mapping or []
    ]
    files = sorted(
        Path(p)
        for p in subprocess.check_output(  # noqa: S603
            ["git", "ls-files", src],  # noqa: S607
        )
        .decode("utf-8")
        .splitlines()
        if p.endswith(".md") and not ignore_spec.match_file(p)
    )

    for file in files:
        file_parts: list[str] = list(file.parts)
        for from_parts, to_parts in mapping_parts:
            idx = is_subsequence(from_parts, file_parts)
            if idx is not None:
                file_parts = [
                    *file_parts[:idx],
                    *to_parts,
                    *file_parts[idx + len(from_parts) :],
                ]
        destination = Path(*file_parts)

        if str(destination) in EDITOR.files:
            print(  # noqa: T201
                f"Unable to copy {file} to {destination} because the file already"
                " exists at the destination.",
                file=sys.stderr,
            )
            msg = f"File {destination} already exists."
            raise RuntimeError(msg)

        with (
            Path(file).open("r", encoding="utf-8") as fi,
            mkdocs_gen_files.open(
                destination,
                "w",
                encoding="utf-8",
            ) as fd,
        ):
            fd.write(fi.read())

        mkdocs_gen_files.set_edit_path(
            destination,
            f"https://github.com/pact-foundation/pact-python/edit/main/{file}",
        )


if __name__ == "<run_path>":
    process_markdown(
        ".",
        ignore=[
            "docs",
        ],
    )
