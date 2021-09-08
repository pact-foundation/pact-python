#!/usr/bin/env python

import json
import sys
import typing
from dataclasses import field, make_dataclass, asdict
from pathlib import Path
from typing import List
from typing import Optional

import cloudpickle
import python_jsonschema_objects
import python_jsonschema_objects as pjs

from pact.ffi.verifier import Verifier


def get_json_schema():
    """Construct, from the FFI args, a dict in the structure required by python_jsonschema_objects."""

    cli_json_path = Path.cwd().joinpath("examples/ffi/pact_ffi_args.json")
    with open(cli_json_path) as json_file:
        data = json.load(json_file)

    properties = {}
    for option in data.get("options"):
        long = option["long"].replace("-", "_")  # Because python won't like arguments named with a -
        if option["multiple"]:

            properties[long] = {"type": "array", "items": {"type": "string"}}
        else:
            properties[long] = {"type": "string"}

    json_schema = {"title": "Verifier Args", "type": "object", "properties": properties, "additionalProperties": False}
    return json_schema


python_jsonschema_objects_example_looks_like_this = {
    "title": "Person",
    "type": "object",
    "properties": {
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "dogs": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["firstName", "lastName"],
}


def try_dataclass():
    cli_json_path = Path.cwd().joinpath("examples/ffi/pact_ffi_args.json")
    with open(cli_json_path) as json_file:
        data = json.load(json_file)

    list_options = [
        (attribute["long"].replace("-", "_"), List[str], field(default_factory=list))
        for attribute in data.get("options")
        if attribute["multiple"]
    ]
    str_options = [
        (attribute["long"].replace("-", "_"), typing.Optional[str], field(default=None))
        for attribute in data.get("options")
        if not attribute["multiple"]
    ]
    bool_options = [(attribute["long"].replace("-", "_"), bool, field(default=None)) for attribute in data.get("flags")]

    VerifierArgsDataClass = make_dataclass("VerifierArgsDataClass", str_options + list_options + bool_options)

    args = VerifierArgsDataClass(scheme="http", file=["file1", "file2", "file3"])

    print()
    print("Check some attributes:")
    print(f"{args.scheme=}")
    print(args.scheme)
    print(f"{args.file=}")

    print()
    print("as_dict")
    print(asdict(args))
    print("Try setting a non existent attribute:")
    try:
        args.fake = 123
    except python_jsonschema_objects.validators.ValidationError as e:
        print(e)

    print()
    print("Try calling the verifier:")
    print(f"Using dict args: {asdict(args)=}")
    verifier = Verifier()
    args_str = verifier.args_dict_to_str(asdict(args))
    print(f"Calling with {args_str=}")
    result = verifier.verify(args_str)
    print(result.logs)

    # Save the class
    print("Does it pickle?")
    with open("verifier_args.pkl", "wb") as dill_file:
        cloudpickle.dump(VerifierArgsDataClass, dill_file)


def try_generate_source():
    cli_json_path = Path.cwd().joinpath("examples/ffi/pact_ffi_args.json")
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
        f"@dataclass{nl}"
        f"class VerifierArgs:{nl}"
        f'    """Auto-generated class, containing the arguments available to the pact verifier."""{nl}'
        f"{nl}"
        f'{nl.join([f"    # {option[2]}{nl}    {option[0]}: {option[1]} = {option[3]}{nl}" for option in str_options + list_options + bool_options])}'
        ""
    )
    print(lines)

    with open("script/verifier_args.py", "w") as f:
        f.writelines(lines)


def try_source():
    from script.verifier_args import VerifierArgs

    args = VerifierArgs(broker_url="http://somewhere.com", scheme="https", file=["file1", "file2", "file3"])

    print("Try calling the verifier:")
    print(f"Using dict args: {asdict(args)=}")
    verifier = Verifier()
    args_str = verifier.args_dict_to_str(asdict(args))
    print(f"Calling with {args_str=}")
    result = verifier.verify(args_str)
    print(result.logs)


def try_python_jsonschema_objects():
    # Use the CLI FFI args to construct a class to hold the args
    json_schema = get_json_schema()
    builder = pjs.ObjectBuilder(json_schema)
    ns = builder.build_classes()
    VerifierArgs = ns.VerifierArgs

    args = VerifierArgs(broker_url="http://somewhere.com", scheme="https", file=["file1", "file2", "file3"])

    print()
    print("Check some attributes:")
    print(f"{args.scheme=}")
    print(args.scheme)
    print(f"{args.file=}")

    print()
    print("Attributes:")
    for attribute in args:
        print(f"{attribute} = {args.get(attribute)}")

    print()
    print("as_dict")
    print(args.as_dict())
    print("Try setting a non existent attribute:")
    try:
        args.fake = 123
    except python_jsonschema_objects.validators.ValidationError as e:
        print(e)

    print()
    print("Try calling the verifier:")
    print(f"Using dict args: {args.as_dict()=}")
    verifier = Verifier()
    args_str = verifier.args_dict_to_str(args.as_dict())
    print(f"Calling with {args_str=}")
    result = verifier.verify(args_str)
    print(result.logs)


def main(**kwargs):
    try_python_jsonschema_objects()
    try_dataclass()
    try_generate_source()
    try_source()


if __name__ == "__main__":
    sys.exit(main())
