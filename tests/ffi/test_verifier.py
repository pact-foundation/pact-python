from pact.ffi.verifier import Verifier, VerifyStatus


def test_version():
    verifier = Verifier()
    # TODO: While messing with a local libpact_ffi build
    # assert verifier.version() == "0.0.1"
    assert verifier.version() == "0.0.2"


def test_verify_no_args():
    result = Verifier().verify(args=None)
    assert VerifyStatus(result.return_code) == VerifyStatus.NULL_POINTER


def test_verify_help():
    result = Verifier().verify(args="--help")
    assert VerifyStatus(result.return_code) == VerifyStatus.INVALID_ARGS
    assert "kind: HelpDisplayed" in "\n".join(result.logs)


def test_verify_version():
    result = Verifier().verify(args="--version")
    assert VerifyStatus(result.return_code) == VerifyStatus.INVALID_ARGS
    assert "kind: VersionDisplayed" in "\n".join(result.logs)


def test_verify_invalid_args():
    """Verify we get an expected return code and log content to invalid args.

    Example output, with TRACE (default) logs:
    [TRACE][mio::poll] registering event source with poller: token=Token(0), interests=READABLE | WRITABLE
    [ERROR][pact_ffi::verifier::verifier] error verifying Pact: "error: Found argument 'Your argument is invalid' which wasn't expected, or isn't valid in this context\n\nUSAGE:\n    pact_verifier_cli [FLAGS] [OPTIONS] --broker-url <broker-url>... --dir <dir>... --file <file>... --provider-name <provider-name> --url <url>...\n\nFor more information try --help" Error { message: "error: Found argument 'Your argument is invalid' which wasn't expected, or isn't valid in this context\n\nUSAGE:\n    pact_verifier_cli [FLAGS] [OPTIONS] --broker-url <broker-url>... --dir <dir>... --file <file>... --provider-name <provider-name> --url <url>...\n\nFor more information try --help", kind: UnknownArgument, info: Some(["Your argument is invalid"]) }
    """
    verifier = Verifier()
    result = verifier.verify(args="Your argument is invalid")
    assert VerifyStatus(result.return_code) == VerifyStatus.INVALID_ARGS
    assert "kind: UnknownArgument" in "\n".join(result.logs)
    assert len(result.logs) == 1  # 1 for only the ERROR log, otherwise will be 2


"""
Original verifier tests. Moving as they are implemented via FFI instead.

TODO:
    def test_verifier_with_provider_and_files(self, mock_path_exists, mock_wrapper):
    def test_verifier_with_provider_and_files_passes_consumer_selctors(self, mock_path_exists, mock_wrapper):
    def test_validate_on_publish_results(self):
    def test_publish_on_success(self, mock_path_exists, mock_wrapper):
    def test_raises_error_on_missing_pact_files(self, mock_path_exists):
    def test_expand_directories_called_for_pacts(self, mock_path_exists, mock_expand_dir, mock_wrapper):
    def test_passes_enable_pending_flag_value(self, mock_wrapper):
    def test_passes_include_wip_pacts_since_value(self, mock_path_exists, mock_wrapper):
    def test_verifier_with_broker(self, mock_wrapper):
    def test_verifier_and_pubish_with_broker(self, mock_wrapper):
    def test_verifier_with_broker_passes_consumer_selctors(self, mock_wrapper):
    def test_publish_on_success(self, mock_path_exists, mock_wrapper):
    def test_passes_enable_pending_flag_value(self, mock_wrapper):
    def test_passes_include_wip_pacts_since_value(self, mock_path_exists, mock_wrapper):
    
Done:
    def test_version(self):
    
Issues:
   
"""


def test_cli_args():
    verifier = Verifier()
    # TODO: While messing with a local libpact_ffi build
    # assert verifier.version() == "0.0.1"
    args = verifier.cli_args()
    x = 1
