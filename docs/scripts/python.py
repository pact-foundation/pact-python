"""
Script used by mkdocs-gen-files to generate documentation for Pact Python.

The script is run by mkdocs-gen-files when the documentation is built in order
to generate documentation from Python docstrings.
"""

import subprocess
from pathlib import Path
from typing import Union

import mkdocs_gen_files


def process_python(src: str, dest: Union[str, None] = None) -> None:
    """
    Process the Python files in the given directory.

    The source directory is relative to the root of the repository, and only
    Python files which are version controlled are processed. The generated
    documentation may optionally written to a different directory.
    """
    dest = dest or src

    # List of all files version controlled files in the SRC_ROOT
    files = sorted(
        map(
            Path,
            subprocess.check_output(["git", "ls-files", src])  # noqa: S603, S607
            .decode("utf-8")
            .splitlines(),
        ),
    )
    files = sorted(filter(lambda p: p.suffix == ".py", files))

    for source_path in files:
        module_path = source_path.relative_to(src).with_suffix("")
        doc_path = source_path.relative_to(src).with_suffix(".md")
        full_doc_path = Path(dest, doc_path)

        parts = [src, *module_path.parts]

        # Skip __main__ modules
        if parts[-1] == "__main__":
            continue

        # The __init__ modules are implicit in the directory structure.
        if parts[-1] == "__init__":
            parts = parts[:-1]
            full_doc_path = full_doc_path.parent / "README.md"

        if full_doc_path.exists():
            with mkdocs_gen_files.open(full_doc_path, "a", encoding="utf-8") as fd:
                python_identifier = ".".join(parts)
                print("# " + parts[-1], file=fd)
                print("::: " + python_identifier, file=fd)
        else:
            with mkdocs_gen_files.open(full_doc_path, "w", encoding="utf-8") as fd:
                python_identifier = ".".join(parts)
                print("# " + parts[-1], file=fd)
                print("::: " + python_identifier, file=fd)

        mkdocs_gen_files.set_edit_path(
            full_doc_path,
            f"https://github.com/pact-foundation/pact-python/edit/master/pact/{module_path}.py",
        )


process_python("pact")
process_python("examples")
