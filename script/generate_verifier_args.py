#!/usr/bin/env python
"""
Generate Verifier args class

This script generates the python source for a class to be used for the Pact
verifier. It works by parsing the JSON produced by the Rust Pact FFI library
function "pactffi_verifier_cli_args".

Each argument available to the Rust Verifier is added as a line, along with the
description provided from Rust. This covers the single option argument, bool
arguments, and lists of options.
"""
import json
from pathlib import Path
from typing import List
from typing import Optional

from pact.ffi.verifier import Verifier


def generate_verifier_args_json(pact_ffi_args_json: str) -> None:
    """Call the Rust Pact FFI library to identify the args, and write to a file"""
    arguments = Verifier()._cli_args_raw()

    with open(pact_ffi_args_json, "w") as f:
        f.writelines(json.dumps(arguments, indent=2))


def generate_verifier_args_source(pact_ffi_args_json: str) -> None:
    """Take the generated JSON file, and construct a quick and dirty class"""
    cli_json_path = Path.cwd().joinpath(pact_ffi_args_json)
    with open(cli_json_path) as json_file:
        data = json.load(json_file)

    list_options = [
        (attribute["long"].replace("-", "_"), Optional[List[str]], attribute["help"], "field(default_factory=list)")
        for attribute in data.get("options")
        if attribute["multiple"]
    ]
    str_options = [
        (attribute["long"].replace("-", "_"), Optional[str], attribute["help"], None)
        for attribute in data.get("options")
        if not attribute["multiple"]
    ]
    bool_options = [
        (attribute["long"].replace("-", "_"), Optional[bool], attribute["help"], None)
        for attribute in data.get("flags")
    ]

    nl = "\n"
    lines = (
        f"import typing{nl}"
        f"from dataclasses import dataclass, field{nl}"
        f"{nl}"
        f"{nl}"
        f"@dataclass{nl}"
        f"class VerifierArgs:{nl}"
        f'    """Auto-generated class, containing the arguments available to the pact verifier."""{nl}'
        f"{nl}"
        f'{nl.join([f"    # {option[2]}{nl}    {option[0]}: {option[1]} = {option[3]}{nl}" for option in str_options + list_options + bool_options])}'
        ""
    )
    print(lines)

    with open("pact/ffi/verifier_args.py", "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    pact_ffi_args_json = "examples/ffi/pact_ffi_verifier_args.json"

    generate_verifier_args_json(pact_ffi_args_json)
    generate_verifier_args_source(pact_ffi_args_json)
