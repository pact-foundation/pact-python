"""Methods to verify previously created pacts."""
import re
import sys
from typing import Callable

import click
from click.core import ParameterSource

from pact.ffi.verifier import Verifier, Arguments


def cli_options():
    """
    Dynamically construct the Click CLI options available to interface with the
    current version of the FFI library.
    This attempts to ensure there cannot be a mismatch between the two, and
    means there doesn't need to be a duplication of logic.
    """

    def inner_func(function: Callable) -> Callable:
        verifier = Verifier()
        args: Arguments = verifier.cli_args()

        # Handle the options requiring values
        for opt in args.options:
            type_choice = click.Choice(opt.possible_values) if opt.possible_values else None

            # Let the user know if an ENV can be used here instead
            _help = f"{opt.help}{f'. Alternatively: ${click.style(opt.env, bold=True)}' if opt.env else ''}"

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
            _help = f"{flag.help}{f'. Alternatively: ${click.style(flag.env, bold=True)}' if flag.env else ''}"

            function = click.option(f"--{flag.long}", help=_help, envvar=flag.env, is_flag=True)(function)

        function = click.option(
            f"--debug-click",
            help="Display arguments passed to the Pact Rust FFI library, for debugging pact-verifier wrapper",
            is_flag=True,
        )(function)

        return function

    return inner_func


@click.command(name="pact-verifier", context_settings=dict(max_content_width=120))
@cli_options()
def main(**kwargs):
    """
    Verify one or more contracts against a provider service.

    Minimal example: pact-verifier --hostname localhost --port 8080 -d ./pacts
    """
    # Since we may only have default args, which are SOME args and we don't know
    # which are required, make sure we have at least one CLI argument
    ctx = click.get_current_context()
    if not [key for key, value in kwargs.items() if ctx.get_parameter_source(key) != ParameterSource.DEFAULT]:
        click.echo(ctx.get_help())
        sys.exit(0)

    verifier = Verifier()

    cli_args = verifier.args_dict_to_str(kwargs)

    if kwargs.get("debug_click"):
        click.echo("kwargs received:")
        click.echo(kwargs)
        click.echo("")

        # To try and avoid confusion and help with debugging, notify the user when ENVs are being used
        arguments_from_envs = [
            key for key, value in kwargs.items() if ctx.get_parameter_source(key) == ParameterSource.ENVIRONMENT
        ]
        if arguments_from_envs:
            click.echo(f"The following arguments are using values provided by ENVs: {arguments_from_envs}")
        click.echo("")

        click.echo("CLI args to send via FFI:")
        click.echo(cli_args)
        click.echo("")

    result = verifier.verify(cli_args)

    if kwargs.get("debug_click"):
        click.echo("Result from FFI call to verify:")
        click.echo(f"{result.return_code=}")
        click.echo(f"{result.logs=}")

    # If the FFI method returned some log output
    if result.logs:
        for log in result.logs:
            m = re.search('.*error verifying Pact: "error: (.*)", kind: .*', log)
            if m:
                for line in m.group(1).split("\\n"):
                    click.echo(line)
            else:
                click.echo(log)

    sys.exit(result.return_code)


if __name__ == "__main__":
    sys.exit(main())
