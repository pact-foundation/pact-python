from pact.ffi.cli.verify import main
from pact.ffi.verifier import Verifier
from click.testing import CliRunner


def test_cli_args():
    """
    Basic test to make sure we have at least some arguments and they all have
    the required long version and help
    """
    verifier = Verifier()
    args = verifier.cli_args()

    assert len(args.options) > 0
    assert len(args.flags) > 0
    assert all([arg.help is not None for arg in args.options])
    assert all([arg.long is not None for arg in args.options])
    assert all([arg.help is not None for arg in args.flags])
    assert all([arg.long is not None for arg in args.flags])


def test_cli_args_cautious(cli_options, cli_flags):
    """
    If desired, we can keep track of the list of arguments supported by the FFI
    CLI, and then at least be alerted if there is a change (this test will fail).

    We don't really *need* to test against this, but it might be nice to know to
    avoid any surprises.
    """
    verifier = Verifier()
    args = verifier.cli_args()

    assert len(args.options) == len(cli_options)
    assert all([arg.long in cli_options for arg in args.options])

    assert len(args.flags) == len(cli_flags)
    assert all([arg.long in cli_flags for arg in args.flags])


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
