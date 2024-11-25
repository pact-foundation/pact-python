"""
Script used by mkdocs-gen-files to generate documentation from Python.

The script is run by mkdocs-gen-files when the documentation is built in order
to generate documentation from Python docstrings.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

import mkdocs_gen_files
from pathspec import PathSpec

if TYPE_CHECKING:
    from collections.abc import Sequence

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


def map_destination(
    path: Path,
    mapping: list[tuple[Sequence[str], Sequence[str]]],
) -> Path | None:
    """
    Takes a path to a Python files and maps it to a destination Markdown file.

    A few notes about some special files:

    - `__main__.py` files are ignored.
    - `__init__.py` files are mapped to the directory containing the file, with
      the name `README.md`.

    Args:
        path:
            The path to the Python file.

        mapping:
            List of tuples containing the source and destination paths to map.
            Note that the list is processed in order, with later mappings
            applied after earlier mappings.
    """
    segments = list(path.with_suffix(".md").parts)

    if segments[-1] == "__main__.md":
        return None

    if segments[-1] == "__init__.md":
        segments[-1] = "README.md"

    for from_parts, to_parts in mapping:
        idx = is_subsequence(from_parts, segments)
        if idx is not None:
            segments = [
                *segments[:idx],
                *to_parts,
                *segments[idx + len(from_parts) :],
            ]
    return Path(*segments)


def map_python_identifier(
    path: Path,
    mapping: list[tuple[str, str]],
) -> str | None:
    """
    Takes a path to a Python files and maps it to a destination Markdown file.

    A few notes about some special files:

    - `__main__.py` files are ignored.
    - `__init__.py` files are handled as usual within Python, i.e.,
      `some/path/__init__.py` is identified as `some.path`, and therefore is
      equivalent to `some/path.py`.

    Args:
        path:
            The path to the Python file.

        mapping:
            List of tuples containing the source and destination Python
            identifiers to map. Note that the list is processed in order, with
            later mappings applied after earlier mappings.
    """
    segments = list(path.with_suffix("").parts)

    if segments[-1] == "__main__":
        return None

    if segments[-1] == "__init__":
        segments = segments[:-1]

    python_identifier = ".".join(segments)
    for from_identifier, to_identifier in mapping:
        idx = is_subsequence(from_identifier.split("."), python_identifier.split("."))
        if idx is not None:
            python_identifier = (
                python_identifier[:idx]
                + to_identifier
                + python_identifier[idx + len(from_identifier) :]
            )
    return python_identifier


def process_python(
    src: str,
    ignore: list[str] | None = None,
    destination_mapping: list[tuple[str, str]] | None = None,
    python_mapping: list[tuple[str, str]] | None = None,
    *,
    ignore_private: bool = True,
) -> None:
    """
    Process the Python files in the given directory.

    The source directory is relative to the root of the repository, and only
    Python files which are version controlled are processed. Once processed,
    they will be available to MkDocs as if they were located in the `docs`
    directory.

    This makes use of `mkdocstrings` to generate documentation from the Python
    docstrings.

    Args:
        src:
            The source directory to process.

        ignore:
            A list of patterns to ignore. This uses the same syntax as
            `.gitignore`.

        destination_mapping:
            List of tuples containing the source and destination paths to map.
            Note that the list is processed in order, with later mappings
            applied after earlier mappings.

        python_mapping:
            List of tuples containing the source and destination Python
            identifiers to map. Note that the list is processed in order, with
            later mappings applied after earlier mappings. This is applied
            independently of the `destination_mapping` argument.

        ignore_private:
            Whether to ignore private modules (those starting with an underscore
            `_`, with the exception of special file names such as `__init__.py`
            and `__main__.py`).
    """
    ignore_spec = PathSpec.from_lines("gitwildmatch", ignore or [])
    files = sorted(
        Path(p)
        for p in subprocess.check_output(  # noqa: S603
            ["git", "ls-files", src],  # noqa: S607
        )
        .decode("utf-8")
        .splitlines()
        if p.endswith(".py") and not ignore_spec.match_file(p)
    )

    for file in files:
        if (
            ignore_private
            and file.name.startswith("_")
            and file.stem not in ["__init__", "__main__"]
        ):
            continue

        destination = map_destination(
            file,
            [(Path(a).parts, Path(b).parts) for a, b in destination_mapping or []],
        )
        python_identifier = map_python_identifier(file, python_mapping or [])

        if not destination or not python_identifier:
            continue

        with mkdocs_gen_files.open(
            destination,
            "a" if destination.exists() else "w",
            encoding="utf-8",
        ) as fd:
            print(
                "# " + python_identifier.split(".")[-1].replace("_", " ").title(),
                file=fd,
            )
            print("::: " + python_identifier, file=fd)

        mkdocs_gen_files.set_edit_path(
            destination,
            f"https://github.com/pact-foundation/pact-python/edit/main/{file}",
        )


if __name__ == "<run_path>":
    process_python(
        "src/pact",
        destination_mapping=[
            ("src/pact", "pact"),
        ],
        python_mapping=[("src.pact", "pact")],
    )
    process_python("examples")
