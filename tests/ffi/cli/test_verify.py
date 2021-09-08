import os

import pytest

from pact.ffi.cli.verify import main
from pact.ffi.verifier import Verifier, VerifyStatus
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
    """Click should return the usage information"""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert result.output.startswith("Usage: pact-verifier [OPTIONS]")


def test_cli_no_args():
    """If no args are provided, but Click passes the default, we still want help"""
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert result.output.startswith("Usage: pact-verifier [OPTIONS]")


def test_cli_verify_success(httpserver):
    pact_file = "examples/pacts/pact-consumer-one-pact-provider-one.json"
    pact_file_path = os.path.join(os.getcwd(), pact_file)
    assert os.path.isfile(pact_file_path), "The working directory must be pact-python, rather than pact-python/tests"

    body = {"hello": "world"}
    endpoint = "/test-provider-one"
    httpserver.expect_request(endpoint).respond_with_json(body)

    args = [
        # f"--url=http://localhost:{httpserver.port}",
        f"--port={httpserver.port}",
        f"--provider-name=pact-provider-one",
        f"--provider-version=0.0.1",
        f"--provider-tags=tag",
        f"--file={pact_file_path}",
    ]
    print(args)
    runner = CliRunner()
    result = runner.invoke(main, args)
    logs = result.output
    assert VerifyStatus(result.exit_code) == VerifyStatus.SUCCESS


from urllib.request import urlopen


def test_hello(httpserver):
    runner = CliRunner()
    result = runner.invoke(main, [])

    body = "Hello, World!"
    endpoint = "/hello"
    httpserver.expect_request(endpoint).respond_with_data(body)
    with urlopen(httpserver.url_for(endpoint)) as response:
        result = response.read().decode()
    assert result == "Hello, World!"
