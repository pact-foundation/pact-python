"""Methods to verify previously created pacts."""
import sys

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
    print(kwargs)


if __name__ == "__main__":
    sys.exit(main())
