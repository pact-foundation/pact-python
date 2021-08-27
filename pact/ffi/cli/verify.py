"""Methods to verify previously created pacts."""
import sys
from typing import List

import click

from pact.ffi.verifier import Verifier, Arguments


def cli_options():
    def inner_func(function):
        verifier = Verifier()
        args: Arguments = verifier.cli_args()

        for opt in args.options:
            type_choice = click.Choice(opt.possible_values) if opt.possible_values else None

            if opt.short:
                function = click.option(
                    f"-{opt.short}",
                    f"--{opt.long}",
                    help=opt.help,
                    type=type_choice,
                    default=opt.default_value,
                    multiple=opt.multiple,
                )(function)
            else:
                function = click.option(
                    f"--{opt.long}", help=opt.help, type=type_choice, default=opt.default_value, multiple=opt.multiple
                )(function)

        for flag in args.flags:
            function = click.option(f"--{flag.long}", help=flag.help, is_flag=True)(function)

        return function

    return inner_func


@click.command()
@cli_options()
def main(**kwargs):
    print("Hello world!")

    print("kwargs received:")
    print(kwargs)

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
    print("")
    print("CLI args to send via FFI:")
    print(cli_args.strip())

    print("")
    verifier = Verifier()
    result = verifier.verify(cli_args)
    print("Result from FFI call to verify:")
    print(f"{result.return_code=}")
    print(f"{result.logs=}")


if __name__ == "__main__":
    sys.exit(main())
