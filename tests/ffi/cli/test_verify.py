from pact.ffi.cli.verify import main
from pact.ffi.verifier import Verifier, VerifyStatus


def test_cli_args():
    """Make sure we have at least some arguments and they all have the required
    long version and help."""
    args = Verifier().cli_args()

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
    args = Verifier().cli_args()
    assert len(args.options) == len(cli_options)
    assert all([arg.long in cli_options for arg in args.options])

    assert len(args.flags) == len(cli_flags)
    assert all([arg.long in cli_flags for arg in args.flags])


def test_cli_help(runner):
    """Click should return the usage information."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert result.output.startswith("Usage: pact-verifier-ffi [OPTIONS]")


def test_cli_no_args(runner):
    """If no args are provided, but Click passes the default, we still want help."""
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert result.output.startswith("Usage: pact-verifier-ffi [OPTIONS]")


def test_cli_verify_success(runner, httpserver, pact_consumer_one_pact_provider_one_path):
    """
    Use the FFI library to verify a simple pact, using a mock httpserver.
    In this case the response is as expected, so the verify succeeds.
    """
    body = {"answer": 42}  # 42 will be returned as an int, as expected
    endpoint = "/test-provider-one"
    httpserver.expect_request(endpoint).respond_with_json(body)

    args = [
        f"--port={httpserver.port}",
        f"--file={pact_consumer_one_pact_provider_one_path}",
    ]
    result = runner.invoke(main, args)

    assert VerifyStatus(result.exit_code) == VerifyStatus.SUCCESS


def test_cli_verify_failure(runner, httpserver, pact_consumer_one_pact_provider_one_path):
    """
    Use the FFI library to verify a simple pact, using a mock httpserver.
    In this case the response is NOT as expected (str not int), so the verify fails.
    """
    body = {"answer": "42"}  # 42 will be returned as a str, which will fail
    endpoint = "/test-provider-one"
    httpserver.expect_request(endpoint).respond_with_json(body)

    args = [
        f"--port={httpserver.port}",
        f"--file={pact_consumer_one_pact_provider_one_path}",
    ]
    result = runner.invoke(main, args)

    assert VerifyStatus(result.exit_code) == VerifyStatus.VERIFIER_FAILED
