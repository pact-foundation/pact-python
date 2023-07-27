"""Wrapper to pact reference dynamic libraries using FFI."""
import json
import os
from pact.ffi.verifier import VerifyResult
from pact.pact_exception import PactException
from cffi import FFI
from pact.ffi.register_ffi import RegisterFfi
from pact.verify_wrapper import expand_directories, is_url


class FFIVerify(object):
    """A Pact Verifier Wrapper."""

    def version(self):
        """Publish version info."""
        ffi = FFI()
        lib = RegisterFfi().get_ffi_lib(ffi)
        result = lib.pactffi_version()
        return ffi.string(result).decode("utf-8")

    def verify( # noqa: max-complexity: 15
        self,
        *pacts,
        provider_base_url,
        provider,
        enable_pending=False,
        include_wip_pacts_since=None,
        **kwargs
    ):
        """Call verify method."""
        self._validate_input(pacts, **kwargs)

        # verbose = kwargs.get("verbose", False)
        provider_app_version = kwargs.get("provider_app_version")
        provider_version_branch = kwargs.get("provider_version_branch")
        publish_verification_results = kwargs.get("publish_verification_results", False)
        broker_username = kwargs.get("broker_username", None)
        broker_password = kwargs.get("broker_password", None)
        broker_token = kwargs.get("broker_token", None)
        broker_url = kwargs.get("broker_url", None)
        provider_states_setup_url = kwargs.get("provider_states_setup_url")
        state_change_as_query = kwargs.get("state_change_as_query", True)
        state_change_teardown = kwargs.get("state_change_teardown", False)
        log_dir = kwargs.get("log_dir")
        # TODO - log_level is applied globally
        # doesnt seem to be a way to set a new log level
        # during a test run
        log_level = kwargs.get("log_level", "INFO")
        provider_tags = kwargs.get("provider_tags", [])
        consumer_version_selectors = kwargs.get("consumer_selectors", [])
        consumer_version_tags = kwargs.get("consumer_tags", [])
        request_timeout = kwargs.get("request_timeout", 10)
        # Additional parameters
        filter_description = kwargs.get("filter_description", None)
        filter_state = kwargs.get("filter_state", None)
        filter_no_state = kwargs.get("filter_no_state", False)
        build_url = kwargs.get("build_url", None)
        disable_ssl_verification = kwargs.get("disable_ssl_verification", False)
        # Set it to greater than zero to enable an error when no pacts
        #  * are found to verify, and set it to zero to disable this.
        no_pacts_is_error = kwargs.get("no_pacts_is_error", False)
        # plugin_name = kwargs.get("plugin_name", None)
        # plugin_version = kwargs.get("plugin_version", None)
        provider_transport = kwargs.get("provider_transport", None)
        if provider_base_url is not None:
            provider_scheme = provider_base_url.split(":")[0]
            provider_hostname = provider_base_url.split(":")[1].replace("//", "")
            if provider_hostname is None:
                provider_hostname = "localhost"
            try:
                provider_path = provider_hostname.split("/")[1]
            except IndexError:
                provider_path = "/"
            try:
                provider_port = int(provider_base_url.split(":")[2])
            except IndexError:
                provider_port = 8000

        def safe_encode(s):
            return b"NULL" if s is None or "" else s.encode("ascii")

        def null_encode():
            return b"NULL"

        ffi = FFI()
        lib = RegisterFfi().get_ffi_lib(ffi)
        # lib.pactffi_log_to_stdout(5)
        # lib.pactffi_log_to_buffer(1)

        LOG_LEVEL_MAPPING = {
            "NONE": 0,
            "ERROR": 1,
            "WARN": 2,
            "INFO": 3,
            "DEBUG": 4,
            "TRACE": 5,
        }
        if log_dir is not None:
            lib.pactffi_log_to_file(safe_encode(os.path.join(log_dir, "pact.log")), 5)
        else:
            lib.pactffi_log_to_buffer(LOG_LEVEL_MAPPING[log_level])
            # lib.pactffi_log_to_stderr(LOG_LEVEL_MAPPING[log_level])

        verifier = lib.pactffi_verifier_new_for_application(b"pact-python", b"1.0.0")

        lib.pactffi_verifier_set_provider_info(
            verifier,
            safe_encode(provider),
            safe_encode(provider_scheme),
            safe_encode(provider_hostname),
            provider_port,
            safe_encode(provider_path),
        )
        if provider_scheme not in ("http", "https") and provider_transport is not None:
            lib.pactffi_verifier_add_provider_transport(
                verifier,
                safe_encode(provider_transport),
                provider_port,
                safe_encode(provider_path),
                safe_encode(provider_scheme),
            )

        lib.pactffi_verifier_set_verification_options(verifier, False, 5000)

        if provider_states_setup_url is not None:
            lib.pactffi_verifier_set_provider_state(verifier, safe_encode(provider_states_setup_url), state_change_teardown, state_change_as_query)

        local_file = False
        all_pact_urls = False
        if pacts:
            all_pact_urls = expand_directories(list(pacts))
            for pact_url in all_pact_urls:
                if not is_url(pact_url):
                    local_file = True

        if all_pact_urls and local_file:
            for pact in all_pact_urls:
                lib.pactffi_verifier_add_file_source(verifier, pact.encode("ascii"))
        elif all_pact_urls and local_file is False:
            for pact in all_pact_urls:
                lib.pactffi_verifier_url_source(
                    verifier,
                    pact.encode("ascii"),
                    safe_encode(broker_username),
                    safe_encode(broker_password),
                    safe_encode(broker_token),
                )
        elif not all_pact_urls and (
            consumer_version_selectors is []
            and consumer_version_tags is []
            and enable_pending is False
            and include_wip_pacts_since is None
        ):
            lib.pactffi_verifier_broker_source(
                verifier,
                safe_encode(broker_url),
                safe_encode(broker_username),
                safe_encode(broker_password),
                safe_encode(broker_token),
            )
        elif not all_pact_urls:
            lib.pactffi_verifier_broker_source_with_selectors(
                verifier,
                safe_encode(broker_url),
                safe_encode(broker_username),
                safe_encode(broker_password),
                safe_encode(broker_token),
                1 if enable_pending else 0,
                safe_encode(include_wip_pacts_since)
                if include_wip_pacts_since
                else safe_encode(""),
                ffi.new("char[]", json.dumps(provider_tags).encode("ascii"))
                if provider_tags
                else ffi.cast("void *", 0),  # TODO
                provider_tags.len() if provider_tags else 0,
                safe_encode(provider_version_branch)
                if provider_version_branch
                else null_encode(),
                ffi.new(
                    "char[]", json.dumps(consumer_version_selectors).encode("ascii")
                )
                if consumer_version_selectors
                else ffi.cast("void *", 0),  # TODO
                consumer_version_selectors.len() if consumer_version_selectors else 0,
                ffi.new("char[]", json.dumps(consumer_version_tags).encode("ascii"))
                if consumer_version_tags
                else ffi.cast("void *", 0),  # TODO
                consumer_version_tags.len() if consumer_version_tags else 0,
            )

        if not all_pact_urls and publish_verification_results is True:
            lib.pactffi_verifier_set_publish_options(
                verifier,
                safe_encode(provider_app_version),
                safe_encode(build_url),
                ffi.new("char[]", json.dumps(provider_tags).encode("ascii"))
                if provider_tags
                else ffi.cast("void *", 0),  # TODO
                provider_tags.len() if provider_tags else 0,
                safe_encode(provider_version_branch)
                if provider_version_branch
                else null_encode(),
            )

        if no_pacts_is_error is True:
            lib.pactffi_verifier_set_no_pacts_is_error(verifier, 1)

        if filter_state is not None or filter_description is not None:
            lib.pactffi_verifier_set_filter_info(
                verifier,
                safe_encode(filter_description),
                safe_encode(filter_state),
                1 if filter_no_state else 0,
            )

        lib.pactffi_verifier_set_verification_options(
            verifier, 1 if disable_ssl_verification else 0, request_timeout
        )
        result = lib.pactffi_verifier_execute(verifier)
        get_logs = lib.pactffi_verifier_logs(verifier)
        lib.pactffi_verifier_shutdown(verifier)

        logs = ffi.string(get_logs).decode("utf-8").rstrip().split("\n")
        lib.pactffi_string_delete(get_logs)
        # print(logs)
        return VerifyResult(result, logs)

    def _validate_input(self, pacts, **kwargs):
        if len(pacts) == 0 and not self._broker_present(**kwargs):
            raise PactException("Pact urls or Pact broker required")

    def _broker_present(self, **kwargs):
        if kwargs.get("broker_url") is None:
            return False
        return True
