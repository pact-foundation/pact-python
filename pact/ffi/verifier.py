"""Wrapper to pact reference dynamic libraries using FFI."""
from enum import Enum, unique
from typing import NamedTuple, List

from pact.ffi.pact_ffi import PactFFI
import json


@unique
class VerifyStatus(Enum):
    SUCCESS = 0  # Operation succeeded
    VERIFIER_FAILED = 1  # The verification process failed, see output for errors
    NULL_POINTER = 2  # A null pointer was received
    PANIC = 3  # The method panicked
    INVALID_ARGS = 4  # Invalid arguments were provided to the verification process


class VerifyResult(NamedTuple):
    return_code: VerifyStatus
    logs: List[str]


class Argument:
    """Hold the attributes of a single argument which can be used by the Verifier"""

    long: str  # For example: "token"
    short: str = None  # For example "t"
    help: str  # Help description, for example: "Bearer token to use when fetching pacts from URLS"
    default_value: str = None  # The value which will be passed if none are provided, such as "http" for schema
    possible_values: List[str] = None  # If only specific values can be used, such as ["http", "https"] for schema
    multiple: bool  # If the argument can be provided multiple times, for example with file
    env: str = None  # ENV which will be used in the absence of a provided argument, for example PACT_BROKER_TOKEN

    def __init__(
        self,
        long: str,
        help: str,
        multiple: bool,
        short: str = None,
        default_value: str = None,
        possible_values: List[str] = None,
        env: str = None,
    ):
        self.long = long
        self.short = short
        self.help = help
        self.default_value = default_value
        self.possible_values = possible_values
        self.multiple = multiple
        self.env = env


class Arguments:
    """Hold the various options and flags which can be used by the Verifier"""

    options: List[Argument] = []
    flags: List[Argument] = []

    def __init__(self, options: List[Argument], flags: List[Argument]):
        self.options = [Argument(**option) for option in options]
        self.flags = [Argument(**flags) for flags in flags]


class Verifier(PactFFI):
    """A Pact Verifier Wrapper.

    This interfaces with the Rust FFI crate pact_ffi, specifically the
    `verifier`_ module.

    .. _verifier:
        https://docs.rs/pact_ffi/0.0.2/pact_ffi/verifier/index.html
    """

    def __new__(cls):
        return super(Verifier, cls).__new__(cls)

    def verify(self, args=None) -> VerifyResult:
        """Call verify method."""

        # The FFI library specifically defines "usage" of no args, so we will
        # replicate that here. In reality we will always want args.
        if args:
            c_args = self.ffi.new("char[]", bytes(args, "utf-8"))
        else:
            c_args = self.ffi.NULL

        result = self.lib.pactffi_verify(c_args)
        logs = self.get_logs()
        return VerifyResult(result, logs)

    def cli_args(self) -> Arguments:
        result = self.lib.pactffi_verifier_cli_args()
        arguments = Arguments(**json.loads(self.ffi.string(result).decode("utf-8")))
        self.lib.pactffi_free_string(result)
        return arguments

    @staticmethod
    def args_dict_to_str(cli_args_dict):
        cli_args = ""
        for key, value in cli_args_dict.items():
            # Don't pass through the debug flag for Click
            if key == "debug_click":
                continue
            key_arg = key.replace("_", "-")
            if value and isinstance(value, bool):
                cli_args = f"{cli_args}\n--{key_arg}"
            elif value and isinstance(value, str):
                cli_args = f"{cli_args}\n--{key_arg}={value}"
            elif value and isinstance(value, tuple) or isinstance(value, list):
                for multiple_opt in value:
                    cli_args = f"{cli_args}\n--{key_arg}={multiple_opt}"
        cli_args = cli_args.strip()
        return cli_args
