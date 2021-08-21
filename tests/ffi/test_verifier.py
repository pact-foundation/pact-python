from pact.ffi.verifier import Verifier, VerifyStatus


def test_version():
    verifier = Verifier()
    assert verifier.version() == "0.0.1"


def test_verify_no_args():
    result = Verifier().verify(args=None)
    assert VerifyStatus(result.return_code) == VerifyStatus.NULL_POINTER


def test_verify_invalid_args():
    """Verify we get an expected return code and log content to invalid args.

    Example output, with TRACE (default) logs:
    [TRACE][mio::poll] registering event source with poller: token=Token(0), interests=READABLE | WRITABLE
    [ERROR][pact_ffi::verifier::verifier] error verifying Pact: "error: Found argument 'Your argument is invalid' which wasn't expected, or isn't valid in this context\n\nUSAGE:\n    pact_verifier_cli [FLAGS] [OPTIONS] --broker-url <broker-url>... --dir <dir>... --file <file>... --provider-name <provider-name> --url <url>...\n\nFor more information try --help" Error { message: "error: Found argument 'Your argument is invalid' which wasn't expected, or isn't valid in this context\n\nUSAGE:\n    pact_verifier_cli [FLAGS] [OPTIONS] --broker-url <broker-url>... --dir <dir>... --file <file>... --provider-name <provider-name> --url <url>...\n\nFor more information try --help", kind: UnknownArgument, info: Some(["Your argument is invalid"]) }
    """
    verifier = Verifier()
    result = verifier.verify(args="Your argument is invalid")
    assert VerifyStatus(result.return_code) == VerifyStatus.INVALID_ARGS
    assert 'UnknownArgument' in '\n'.join(result.logs)
    assert len(result.logs) == 1  # 1 for only the ERROR log, otherwise will be 2


def test_verify_invalid_args2():
    result = Verifier().verify(args="Your argument is still invalid")
    assert VerifyStatus(result.return_code) == VerifyStatus.INVALID_ARGS
    assert 'UnknownArgument' in '\n'.join(result.logs)
    assert len(result.logs) == 1
