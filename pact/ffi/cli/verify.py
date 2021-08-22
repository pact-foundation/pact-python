"""Methods to verify previously created pacts."""
import sys

import click

from pact.ffi.verifier import Verifier


def cli_options():
    def inner_func(function):
        verifier = Verifier()
        args = verifier.cli_args()

        for arg in args:
            arg_name = arg["name"].replace("-", "_")

            if arg["short"]:
                function = click.option(arg_name, f"-{arg['short']}", f"--{arg['long']}", help=arg["help"])(function)
            else:
                function = click.option(arg_name, f"--{arg['long']}", help=arg["help"])(function)
        return function

    return inner_func


@click.command()
@cli_options()
def main(**kwargs):
    print("Hello world!")
    print(kwargs)


if __name__ == "__main__":
    sys.exit(main())
