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
    long: str
    short: str = None
    help: str
    default_value: str = None
    possible_values: List[str] = None
    multiple: bool

    def __init__(
        self,
        long: str,
        help: str,
        multiple: bool,
        short: str = None,
        default_value: str = None,
        possible_values: List[str] = None,
    ):
        self.long = long
        self.short = short
        self.help = help
        self.default_value = default_value
        self.possible_values = possible_values
        self.multiple = multiple


class Arguments:
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
        https://docs.rs/pact_ffi/0.0.1/pact_ffi/verifier/index.html
    """

    def verify(self, args=None) -> VerifyResult:
        """Call verify method."""

        if args:
            c_args = self.ffi.new("char[]", bytes(args, "utf-8"))
        else:
            c_args = self.ffi.NULL

        # This fails if called a second time after the library has been loaded
        # ..but still seems to work
        # result = lib.pactffi_log_to_buffer()
        # assert LogToBufferStatus(result) == LogToBufferStatus.SUCCESS
        # Additionally, when reading from the buffer it seems to come back empty
        # when running normally. Storing to a temporary file, at least for now.
        # with tempfile.TemporaryDirectory() as td:
        #     output = os.path.join(td, 'output')
        #     output_c = ffi.new('char[]', bytes(output, 'utf-8'))
        #     result = lib.pactffi_log_to_file(output_c)
        #     x = 1
        #     result = lib.pactffi_verify(c_args)
        #
        #     lines = open(output).readlines()

        result = self.lib.pactffi_verify(c_args)
        logs = self._get_logs()
        return VerifyResult(result, logs)

    def cli_args(self) -> str:
        result = self.lib.pactffi_verifier_cli_args()
        return Arguments(**json.loads(self.ffi.string(result).decode("utf-8")))
