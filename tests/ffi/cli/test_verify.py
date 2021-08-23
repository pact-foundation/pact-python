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

    assert len(args) > 0
    assert any(["help" in arg for arg in args])
    assert all(["long" in arg for arg in args])


def test_cli_args_cautious(cli_arguments):
    """
    If desired, we can keep track of the list of arguments supported by the FFI
    CLI, and then at least be alerted if there is a change (this test will fail).

    We don't really *need* to test against this, but it might be nice to know to
    avoid any surprises.
    """
    verifier = Verifier()
    args = verifier.cli_args()

    assert len(args) == len(cli_arguments)
    assert all([arg["name"] in cli_arguments for arg in args])


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
