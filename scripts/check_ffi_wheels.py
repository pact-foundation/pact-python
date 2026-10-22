#!/usr/bin/env python3
"""Check the ABI tags and extension names of pact-python-ffi wheels.

Usage:
    python scripts/check_ffi_wheels.py WHEEL [WHEEL ...]

Each wheel must carry either the `abi3` or the `abi3.abi3t` tag, and its CFFI
extension must use the matching file name. A free-threaded interpreter ignores
an `abi3` extension, so a mismatch yields a wheel which installs but fails to
import. The set of wheels must include both tags.
"""

from __future__ import annotations

import logging
import sys
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)

EXTENSIONS = {
    "abi3": {"pact_ffi/ffi.abi3.so", "pact_ffi/ffi.pyd"},
    "abi3.abi3t": {"pact_ffi/ffi.abi3t.so", "pact_ffi/ffi.pyd"},
}


def check(wheel: Path) -> tuple[str | None, list[str]]:
    """
    Check a single wheel.

    Args:
        wheel:
            Path to the wheel.

    Returns:
        The ABI tag of the wheel, if recognised, and a list of errors.
    """
    # Wheel names are `{name}-{version}-{python}-{abi}-{platform}.whl`.
    abi = wheel.stem.split("-")[-2]
    if abi not in EXTENSIONS:
        return None, [f"{wheel.name}: unexpected ABI tag {abi!r}"]

    with zipfile.ZipFile(wheel) as zf:
        found = {
            name
            for name in zf.namelist()
            if name.startswith("pact_ffi/ffi.") and name.endswith((".so", ".pyd"))
        }
    if len(found) != 1 or not found <= EXTENSIONS[abi]:
        return abi, [f"{wheel.name}: {abi!r} wheel contains {sorted(found)}"]
    return abi, []


def main(argv: list[str]) -> int:
    """
    Check every wheel given on the command line.

    Args:
        argv:
            Paths to the wheels.

    Returns:
        The process exit code.
    """
    errors: list[str] = []
    abis: set[str] = set()
    for arg in argv:
        abi, wheel_errors = check(Path(arg))
        errors.extend(wheel_errors)
        if abi:
            abis.add(abi)
            logger.info("%s: %s", Path(arg).name, abi)

    errors.extend(f"no {abi!r} wheel was built" for abi in EXTENSIONS.keys() - abis)
    for error in errors:
        logger.error("error: %s", error)
    return 1 if errors else 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    sys.exit(main(sys.argv[1:]))
