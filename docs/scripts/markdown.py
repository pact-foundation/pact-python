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

import subprocess
import sys
from pathlib import Path

import mkdocs_gen_files
from mkdocs_gen_files.editor import FilesEditor

EDITOR = FilesEditor.current()

# These paths are relative to the project root, *not* the current file.
SRC_ROOT = "."
DOCS_DEST = "."

# List of all files version controlled files in the SRC_ROOT
ALL_FILES = sorted(
    map(
        Path,
        subprocess.check_output(["git", "ls-files", SRC_ROOT])  # noqa: S603, S607
        .decode("utf-8")
        .splitlines(),
    ),
)


for source_path in filter(lambda p: p.suffix == ".md", ALL_FILES):
    if source_path.parts[0] == "docs":
        continue
    dest_path = Path(DOCS_DEST, source_path)

    if str(dest_path) in EDITOR.files:
        print(  # noqa: T201
            f"Unable to copy {source_path} to {dest_path} because the file already"
            " exists at the destination.",
            file=sys.stderr,
        )
        msg = f"File {dest_path} already exists."
        raise RuntimeError(msg)

    with Path(source_path).open("r", encoding="utf-8") as fi, mkdocs_gen_files.open(
        dest_path,
        "w",
        encoding="utf-8",
    ) as fd:
        fd.write(fi.read())

    mkdocs_gen_files.set_edit_path(
        dest_path,
        f"https://github.com/pact-foundation/pact-python/edit/develop/{source_path}",
    )
