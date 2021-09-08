"""Methods to verify previously created pacts."""
import sys
from typing import Callable

import click

from pact.ffi.verifier import Verifier, Arguments


def cli_options():
    """
    Dynamically construct the Click CLI options available to interface with the
    current version of the FFI library.
    This attempts to ensure there cannot be a mismatch between the two.
    """

    def inner_func(function: Callable) -> Callable:
        verifier = Verifier()
        args: Arguments = verifier.cli_args()

        # Handle the options requiring values
        for opt in args.options:
            type_choice = click.Choice(opt.possible_values) if opt.possible_values else None

            # Let the user know if an ENV can be used here instead
            _help = f"{opt.help}{f'. Alternatively: ${opt.env}' if opt.env else ''}"

            if opt.short:
                function = click.option(
                    f"-{opt.short}",
                    f"--{opt.long}",
                    help=_help,
                    type=type_choice,
                    default=opt.default_value,
                    multiple=opt.multiple,
                    envvar=opt.env,
                )(function)
            else:
                function = click.option(
                    f"--{opt.long}",
                    help=_help,
                    type=type_choice,
                    default=opt.default_value,
                    multiple=opt.multiple,
                    envvar=opt.env,
                )(function)

        # Handle the boolean flags
        for flag in args.flags:
            # Let the user know if an ENV can be used here instead
            # Note: future proofing, there do not seem to be any as of Pact FFI Library 0.0.2
            _help = f"{flag.help}{f'. Alternatively: ${flag.env}' if flag.env else ''}"

            function = click.option(f"--{flag.long}", help=_help, envvar=opt.env, is_flag=True)(function)

        function = click.option(
            f"--debug-click",
            help="Display arguments passed to the FFI library",
            is_flag=True,
        )(function)

        return function

    return inner_func


@click.command()
@cli_options()
def main(**kwargs):
    cli_args = ""
    for key, value in kwargs.items():
        key_arg = key.replace("_", "-")
        if value and isinstance(value, bool):
            cli_args = f"{cli_args}\n--{key_arg}"
        elif value and isinstance(value, str):
            cli_args = f"{cli_args}\n--{key_arg}={value}"
        elif value and isinstance(value, tuple):
            for multiple_opt in value:
                cli_args = f"{cli_args}\n--{key_arg}={multiple_opt}"
    cli_args = cli_args.strip()

    if kwargs.get("debug_click"):
        print("kwargs received:")
        print(kwargs)
        print("CLI args to send via FFI:")
        print(cli_args)
        print("")

    verifier = Verifier()
    result = verifier.verify(cli_args)
    print("Result from FFI call to verify:")
    print(f"{result.return_code=}")
    print(f"{result.logs=}")


if __name__ == "__main__":
    sys.exit(main())
