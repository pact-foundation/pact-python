"""
Create placeholder files for all other files in the codebase.

This script is run by mkdocs-gen-files when the documentation is built and
creates placeholder files for all other files in the codebase. This is done so
that the documentation site can link to all files in the codebase, even if they
aren't part of the documentation proper.

If the files are binary, they are copied as-is (e.g. for images), otherwise a
HTML redirect is created.

If the destination file already exists (either because it is a real file, or was
otherwise already generated), the script will ignore the current file and
continue silently.
"""

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import mkdocs_gen_files
from mkdocs_gen_files.editor import FilesEditor

if TYPE_CHECKING:
    import io

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


def is_binary(buffer: bytes) -> bool:
    """
    Determine whether the given buffer is binary or not.

    The check is done by attempting to decode the buffer as UTF-8. If this
    succeeds, the buffer is not binary. If it fails, the buffer is binary.

    The entire buffer will be checked, therefore if checking whether a file is
    binary, only the start of the file should be passed.

    Args:
        buffer:
            The buffer to check.

    Returns:
        True if the buffer is binary, False otherwise.
    """
    try:
        buffer.decode("utf-8")
    except UnicodeDecodeError:
        return True
    else:
        return False


for source_path in ALL_FILES:
    if not source_path.is_file():
        continue
    if source_path.parts[0] in ["docs"]:
        continue

    dest_path = Path(DOCS_DEST, source_path)

    if str(dest_path) in EDITOR.files:
        continue

    fi: "io.IOBase"
    with Path(source_path).open("rb") as fi:
        buf = fi.read(2048)

    if is_binary(buf):
        if source_path.stat().st_size < 16 * 2**20:
            # Copy the file only if it's less than 16MB.
            with (
                Path(source_path).open("rb") as fi,
                mkdocs_gen_files.open(
                    dest_path,
                    "wb",
                ) as fd,
            ):
                fd.write(fi.read())
        else:
            # File is too big, create a redirect.
            url = (
                "https://github.com"
                "/pact-foundation/pact-python"
                "/raw"
                "/develop"
                f"/{source_path}"
            )
            with mkdocs_gen_files.open(dest_path, "w", encoding="utf-8") as fd:
                fd.write(f'<meta http-equiv="refresh" content="0; url={url}">')
                fd.write(f"# Redirecting to {url}...")
                fd.write(f"[Click here if you are not redirected]({url})")

            mkdocs_gen_files.set_edit_path(
                dest_path,
                f"https://github.com/pact-foundation/pact-python/edit/develop/{source_path}",
            )

    else:
        with (
            Path(source_path).open("r", encoding="utf-8") as fi,
            mkdocs_gen_files.open(
                dest_path,
                "w",
                encoding="utf-8",
            ) as fd,
        ):
            fd.write(fi.read())
