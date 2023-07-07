
# from pact.ffi.verifier import Verifier, VerifyStatus

# def test_version():
#     result = Verifier().version()
#     assert result == "0.4.5"


# def test_verify_no_args():
#     result = Verifier().verify(args=None)
#     assert VerifyStatus(result.return_code) == VerifyStatus.NULL_POINTER


# def test_verify_help():
#     result = Verifier().verify(args="--help")
#     assert VerifyStatus(result.return_code) == VerifyStatus.INVALID_ARGS
#     assert "kind: HelpDisplayed" in "\n".join(result.logs)


# def test_verify_version():
#     result = Verifier().verify(args="--version")
#     assert VerifyStatus(result.return_code) == VerifyStatus.INVALID_ARGS
#     assert "kind: VersionDisplayed" in "\n".join(result.logs)


# def test_verify_invalid_args():
#     """Verify we get an expected return code and log content to invalid args.

#     Example output, with TRACE (default) logs:
#     [TRACE][mio::poll] registering event source with poller: token=Token(0), interests=READABLE | WRITABLE
#     [ERROR][pact_ffi::verifier::verifier] error verifying Pact: "error: Found argument 'Your argument
#     is invalid' which wasn't expected, or isn't valid in this context\n\nUSAGE:\n    pact_verifier_cli
#     [FLAGS] [OPTIONS] --broker-url <broker-url>... --dir <dir>... --file <file>... --provider-name <provider-name>
#     --url <url>...\n\nFor more information try --help" Error { message: "error: Found argument 'Your argument is
#     invalid' which wasn't expected, or isn't valid in this context\n\nUSAGE:\n    pact_verifier_cli [FLAGS] [OPTIONS]
#     --broker-url <broker-url>... --dir <dir>... --file <file>... --provider-name <provider-name> --url <url>...\n\n
#     For more information try --help", kind: UnknownArgument, info: Some(["Your argument is invalid"]) }
#     """
#     result = Verifier().verify(args="Your argument is invalid")
#     assert VerifyStatus(result.return_code) == VerifyStatus.INVALID_ARGS
#     assert "kind: UnknownArgument" in "\n".join(result.logs)
#     assert len(result.logs) == 1  # 1 for only the ERROR log, otherwise will be 2


# def test_verify_success(httpserver, pact_consumer_one_pact_provider_one_path):
#     """
#     Use the FFI library to verify a simple pact, using a mock httpserver.
#     In this case the response is as expected, so the verify succeeds.
#     """
#     body = {"answer": 42}  # 42 will be returned as an int, as expected
#     endpoint = "/test-provider-one"
#     httpserver.expect_request(endpoint).respond_with_json(body)

#     args_list = [
#         f"--port={httpserver.port}",
#         f"--file={pact_consumer_one_pact_provider_one_path}",
#     ]
#     args = "\n".join(args_list)
#     result = Verifier().verify(args=args)
#     assert VerifyStatus(result.return_code) == VerifyStatus.SUCCESS


# def test_verify_failure(httpserver, pact_consumer_one_pact_provider_one_path):
#     """
#     Use the FFI library to verify a simple pact, using a mock httpserver.
#     In this case the response is NOT as expected (str not int), so the verify fails.
#     """
#     body = {"answer": "42"}  # 42 will be returned as a str, which will fail
#     endpoint = "/test-provider-one"
#     httpserver.expect_request(endpoint).respond_with_json(body)

#     args_list = [
#         f"--port={httpserver.port}",
#         f"--file={pact_consumer_one_pact_provider_one_path}",
#     ]
#     args = "\n".join(args_list)
#     result = Verifier().verify(args=args)
#     assert VerifyStatus(result.return_code) == VerifyStatus.VERIFIER_FAILED


# """
# Original verifier tests. Moving as they are implemented via FFI instead.

# TODO:
#     def test_verifier_with_provider_and_files(self, mock_path_exists, mock_wrapper):
#     def test_verifier_with_provider_and_files_passes_consumer_selctors(self, mock_path_exists, mock_wrapper):
#     def test_validate_on_publish_results(self):
#     def test_publish_on_success(self, mock_path_exists, mock_wrapper):
#     def test_raises_error_on_missing_pact_files(self, mock_path_exists):
#     def test_expand_directories_called_for_pacts(self, mock_path_exists, mock_expand_dir, mock_wrapper):
#     def test_passes_enable_pending_flag_value(self, mock_wrapper):
#     def test_passes_include_wip_pacts_since_value(self, mock_path_exists, mock_wrapper):
#     def test_verifier_with_broker(self, mock_wrapper):
#     def test_verifier_and_pubish_with_broker(self, mock_wrapper):
#     def test_verifier_with_broker_passes_consumer_selctors(self, mock_wrapper):
#     def test_publish_on_success(self, mock_path_exists, mock_wrapper):
#     def test_passes_enable_pending_flag_value(self, mock_wrapper):
#     def test_passes_include_wip_pacts_since_value(self, mock_path_exists, mock_wrapper):

# Done:
#     def test_version(self):

# Issues:
# Skipped test_verifier.py and cli/test_ffi_verifier.py, there is an issue with the loggers whereby
# test_ffi_verifier.py uses pactffi_log_to_buffer and pactffi_verifier_logs with a verifier handle
# the others, either write to a pactffi_log_to_file, or call pactffi_log_to_buffer but call pactffi_fetch_log_buffer
# This function can take a log specifier but its not clear how to set that.
# if the tests are run individually they are fine...
# """
