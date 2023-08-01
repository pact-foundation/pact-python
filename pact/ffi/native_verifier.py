"""Wrapper to pact reference dynamic libraries using FFI."""
import json
from pact.ffi.utils import ne, se
from typing import List
from pact.__version__ import __version__
from pact.ffi.pact_ffi import PactFFI

class VerifierHandle(int):
    """A typedef for the VerifierHandler opaque pointer."""

    handle = int

class NativeVerifier(PactFFI):
    """A Pact Verifier Wrapper.

    This interfaces with the Rust FFI crate pact_ffi, specifically the
    `verifier`_ module.

    .. _verifier:
        https://docs.rs/pact_ffi/0.0.2/pact_ffi/verifier/index.html
    """

    def __new__(cls):
        """Create a new instance of the Verifier."""
        return super(NativeVerifier, cls).__new__(cls)

    def execute(self, verifier_handle: VerifierHandle) -> int:
        """
        Run the verification.

        # Error Handling

        Errors will be reported with a non-zero return value.
        int pactffi_verifier_execute(struct VerifierHandle *handle);
        """
        return self.lib.pactffi_verifier_execute(verifier_handle)

    def new(self) -> VerifierHandle.handle:
        """
        Get a Handle to a newly created verifier.

        You should call `pactffi_verifier_shutdown` when
        done with the verifier to free all allocated resources.

         ### Safety

         This function is safe.

         # Error Handling

        Returns NULL on error.

        struct VerifierHandle *pactffi_verifier_new_for_application(const char *name, const char *version)
        """
        # struct VerifierHandle *pactffi_verifier_new(void);
        return self.lib.pactffi_verifier_new_for_application(se('pact-python'), se(__version__))

    def shutdown(self, verifier_handle: VerifierHandle):
        """
        Shutdown the verifier and release all resources.

        void pactffi_verifier_shutdown(struct VerifierHandle *handle);
        """
        self.lib.pactffi_verifier_shutdown(verifier_handle)

    def set_provider_info(self, verifier_handle: VerifierHandle, name=str, scheme=str, host=str, port=int, path=str):
        """
        Set the provider details for the Pact verifier.

        Set the provider details for the Pact verifier. Passing a NULL for any field will
        use the default value for that field.

        ### Safety

         All string fields must contain valid UTF-8. Invalid UTF-8
         will be replaced with U+FFFD REPLACEMENT CHARACTER.

        void pactffi_verifier_set_provider_info(struct VerifierHandle *handle,
                                                const char *name,
                                                const char *scheme,
                                                const char *host,
                                                unsigned short port,
                                                const char *path);
        """
        self.lib.pactffi_verifier_set_provider_info(verifier_handle, se(name), se(scheme), se(host), port, se(path))

    def add_provider_transport(self, verifier_handle: VerifierHandle, protocol=str, port=int, path=str, scheme=str):
        """
        Add a new transport for the given provider.

        Passing a NULL for any field will use the default value for that field.

        For non-plugin based message interactions, set protocol to "message" and set scheme
        to an empty string or "https" if secure HTTP is required. Communication to the calling
        application will be over HTTP to the default provider hostname.

        ##### Safety

        All string fields must contain valid UTF-8. Invalid UTF-8
        will be replaced with U+FFFD REPLACEMENT CHARACTER.

        ### Original Method

        void pactffi_verifier_add_provider_transport(struct VerifierHandle *handle,
                                                      const char *protocol,
                                                      unsigned short port,
                                                      const char *path,
                                                      const char *scheme);
        """
        self.lib.pactffi_verifier_add_provider_transport(verifier_handle, se(protocol), port, se(path), se(scheme))

    def set_filter_info(self, verifier_handle: VerifierHandle, filter_description=str, filter_state=str, filter_no_state=bool):
        """
        Set the filters for the Pact verifier.

        If `filter_description` is not empty, it needs to be as a regular expression.

        `filter_no_state` is a boolean value. Set it to greater than zero to turn the option on.

        ### Safety

        All string fields must contain valid UTF-8. Invalid UTF-8
        will be replaced with U+FFFD REPLACEMENT CHARACTER.


        void pactffi_verifier_set_filter_info(struct VerifierHandle *handle,
                                              const char *filter_description,
                                              const char *filter_state,
                                              unsigned char filter_no_state);

        """
        self.lib.pactffi_verifier_set_filter_info(verifier_handle, se(filter_description), se(filter_state), filter_no_state)

    def set_provider_state(self, verifier_handle: VerifierHandle, url=str, teardown=bool, body=bool):
        """
        Set the provider state URL for the Pact verifier.

        * `teardown` is a boolean value. If teardown state change requests should be made after an
        interaction is validated (default is false). Set it to greater than zero to turn the
        option on.

        * `body` is a boolean value. Sets if state change request data should be sent in the body
        (> 0, true) or as query parameters (== 0, false). Set it to greater than zero to turn the
        option on.

        ### Safety

        All string fields must contain valid UTF-8. Invalid UTF-8
        will be replaced with U+FFFD REPLACEMENT CHARACTER.


        void pactffi_verifier_set_provider_state(struct VerifierHandle *handle,
                                                const char *url,
                                                unsigned char teardown,
                                                unsigned char body);
        """
        self.lib.pactffi_verifier_set_provider_state(verifier_handle, se(url), teardown, body)

    def set_verification_options(self, verifier_handle: VerifierHandle, disable_ssl_verification: bool, request_timeout: int) -> int:
        """
        Set the options used by the verifier when calling the provider.

        `disable_ssl_verification` is a boolean value. Set it to greater than zero to turn the option on.

        ### Safety

        All string fields must contain valid UTF-8. Invalid UTF-8
        will be replaced with U+FFFD REPLACEMENT CHARACTER.

        /
        int pactffi_verifier_set_verification_options(struct VerifierHandle *handle,
                                                      unsigned char disable_ssl_verification,
                                                      unsigned long request_timeout);
        """
        return self.lib.pactffi_verifier_set_verification_options(verifier_handle, disable_ssl_verification, request_timeout)

    def set_coloured_output(self, verifier_handle: VerifierHandle, coloured_output: bool) -> int:
        """
        Enable or disable coloured output using ANSI escape codes in the verifier output.

        By default, coloured output is enabled.

        `coloured_output` is a boolean value. Set it to greater than zero to turn the option on.

        ### Safety

        This function is safe as long as the handle pointer points to a valid handle.


        int pactffi_verifier_set_coloured_output(struct VerifierHandle *handle,
                                                 unsigned char coloured_output);
        """
        return self.lib.pactffi_verifier_set_coloured_output(verifier_handle, coloured_output)

    def set_no_pacts_is_error(self, verifier_handle: VerifierHandle, is_error: bool) -> int:
        """
        Enable or disable if no pacts are found to verify results in an error.

        `is_error` is a boolean value. Set it to greater than zero to enable an error when no pacts
        are found to verify, and set it to zero to disable this.

        ### Safety

        This function is safe as long as the handle pointer points to a valid handle.

        int pactffi_verifier_set_no_pacts_is_error(struct VerifierHandle *handle, unsigned char is_error);
        """
        return self.lib.pactffi_verifier_set_no_pacts_is_error(verifier_handle, is_error)

    def set_publish_options(self, verifier_handle: VerifierHandle, provider_version=str, build_url=str, provider_tags=List[str], provider_branch=str) -> int:
        """
        Set the options used when publishing verification results to the Pact Broker.

        # Args

        - `handle` - The pact verifier handle to update
        - `provider_version` - Version of the provider to publish
        - `build_url` - URL to the build which ran the verification
        - `provider_tags` - Collection of tags for the provider
        - `provider_tags_len` - Number of provider tags supplied
        - `provider_branch` - Name of the branch used for verification

        ### Safety

        All string fields must contain valid UTF-8. Invalid UTF-8
        will be replaced with U+FFFD REPLACEMENT CHARACTER.

        /
        int pactffi_verifier_set_publish_options(struct VerifierHandle *handle,
                                                 const char *provider_version,
                                                 const char *build_url,
                                                 const char *const *provider_tags,
                                                 unsigned short provider_tags_len,
                                                 const char *provider_branch);
        """
        return self.lib.pactffi_verifier_set_publish_options(
            verifier_handle,
            se(provider_version),
            se(build_url),
            self.ffi.new("char[]", json.dumps(provider_tags).encode("ascii"))
            if provider_tags
            else self.ffi.cast("void *", 0),
            provider_tags.len() if provider_tags else 0,
            se(provider_branch)
            if provider_branch
            else ne(),

        )

    def set_consumer_filters(self, verifier_handle: VerifierHandle, consumer_filters=List[str]):
        """
        Set the consumer filters for the Pact verifier.

        ### Safety

        All string fields must contain valid UTF-8. Invalid UTF-8
        will be replaced with U+FFFD REPLACEMENT CHARACTER.

        void pactffi_verifier_set_consumer_filters(struct VerifierHandle *handle,
                                                   const char *const *consumer_filters,
                                                   unsigned short consumer_filters_len);
        """
        for consumer_filter in consumer_filters:
            c_item = self.ffi.new("char[]", se(consumer_filter))
        c_arr = self.ffi.new("char **", c_item)

        self.lib.pactffi_verifier_set_consumer_filters(verifier_handle,
                                                       c_arr,
                                                       len(consumer_filters)
                                                       )

    def add_custom_header(self, verifier_handle: VerifierHandle, header_name: str, header_value: str):
        """

        Add a custom header to be added to the requests made to the provider.

        ### Safety

        The header name and value must point to a valid NULL terminated string and must contain
        valid UTF-8.

        void pactffi_verifier_add_custom_header(struct VerifierHandle *handle,
                                                const char *header_name,
                                                const char *header_value);
        """
        self.lib.pactffi_verifier_add_custom_header(verifier_handle, se(header_name), se(header_value))

    def add_file_source(self, verifier_handle: VerifierHandle, file=str):
        """

        Add a Pact file as a source to verify.

        ### Safety

        All string fields must contain valid UTF-8. Invalid UTF-8
        will be replaced with U+FFFD REPLACEMENT CHARACTER.


        void pactffi_verifier_add_file_source(struct VerifierHandle *handle, const char *file);
        """
        self.lib.pactffi_verifier_add_file_source(verifier_handle, se(file))

    def add_directory_source(self, verifier_handle: VerifierHandle, directory: str):
        """
        Add a Pact directory as a source to verify.

        All pacts from the directory that match the provider name will be verified.

        ### Safety

        All string fields must contain valid UTF-8. Invalid UTF-8
        will be replaced with U+FFFD REPLACEMENT CHARACTER.

        void pactffi_verifier_add_directory_source(struct VerifierHandle *handle, const char *directory);

        """
        self.lib.pactffi_verifier_add_directory_source(verifier_handle, se(directory))

    def url_source(self, verifier_handle: VerifierHandle, url: str, username: str, password: str, token: str):
        """

        Add a URL as a source to verify. The Pact file will be fetched from the URL.

        If a username and password is given, then basic authentication will be used when fetching
        the pact file. If a token is provided, then bearer token authentication will be used.

        ### Safety

        All string fields must contain valid UTF-8. Invalid UTF-8
        will be replaced with U+FFFD REPLACEMENT CHARACTER.


        void pactffi_verifier_url_source(struct VerifierHandle *handle,
                                         const char *url,
                                         const char *username,
                                         const char *password,
                                         const char *token);
        """
        self.lib.pactffi_verifier_url_source(verifier_handle, se(url), se(username), se(password), se(token))

    def broker_source(self, verifier_handle: VerifierHandle, url: str, username: str, password: str, token: str):
        """
        Add a Pact broker as a source to verify.

        This will fetch all the pact files from the broker that match the provider name.

        If a username and password is given, then basic authentication will be used when fetching
        the pact file. If a token is provided, then bearer token authentication will be used.

        ### Safety

        All string fields must contain valid UTF-8. Invalid UTF-8
        will be replaced with U+FFFD REPLACEMENT CHARACTER.


        void pactffi_verifier_broker_source(struct VerifierHandle *handle,
                                             const char *url,
                                             const char *username,
                                             const char *password,
                                             const char *token);
        """
        self.lib.pactffi_verifier_broker_source(verifier_handle, se(url), se(username), se(password), b'NULL')

    def broker_source_with_selectors(self, verifier_handle: VerifierHandle,
                                     url: str,
                                     username: str,
                                     password: str,
                                     token: str,
                                     enable_pending: bool,
                                     include_wip_pacts_since: str,
                                     provider_tags: List[str],
                                     provider_branch: str,
                                     consumer_version_selectors: List[str],
                                     consumer_version_tags: List[str],
                                     ):
        """
        Add a Pact broker as a source to verify.

        This will fetch all the pact files from the broker that match the provider name and the consumer version selectors
        (See `https://docs.pact.io/pact_broker/advanced_topics/consumer_version_selectors/`).

        The consumer version selectors must be passed in in JSON format.

        `enable_pending` is a boolean value. Set it to greater than zero to turn the option on.

        If the `include_wip_pacts_since` option is provided, it needs to be a date formatted in
        ISO format (YYYY-MM-DD).

        If a username and password is given, then basic authentication will be used when fetching
        the pact file. If a token is provided, then bearer token authentication will be used.

        ### Safety

        All string fields must contain valid UTF-8. Invalid UTF-8
        will be replaced with U+FFFD REPLACEMENT CHARACTER.

        /
        void pactffi_verifier_broker_source_with_selectors(struct VerifierHandle *handle,
                                                           const char *url,
                                                           const char *username,
                                                           const char *password,
                                                           const char *token,
                                                           unsigned char enable_pending,
                                                           const char *include_wip_pacts_since,
                                                           const char *const *provider_tags,
                                                           unsigned short provider_tags_len,
                                                           const char *provider_branch,
                                                           const char *const *consumer_version_selectors,
                                                           unsigned short consumer_version_selectors_len,
                                                           const char *const *consumer_version_tags,
                                                           unsigned short consumer_version_tags_len);

        """
        self.lib.pactffi_verifier_broker_source_with_selectors(
            verifier_handle,
            se(url),
            se(username),
            se(password),
            se(token),
            enable_pending,
            # 1 if enable_pending else 0,
            se(include_wip_pacts_since)
            if include_wip_pacts_since
            else se(""),
            self.ffi.new("char[]", json.dumps(provider_tags).encode("ascii"))
            if provider_tags
            else self.ffi.cast("void *", 0),
            provider_tags.len() if provider_tags else 0,
            se(provider_branch)
            if provider_branch
            else ne(),
            self.ffi.new(
                "char[]", json.dumps(consumer_version_selectors).encode("ascii")
            )
            if consumer_version_selectors
            else self.ffi.cast("void *", 0),
            consumer_version_selectors.len() if consumer_version_selectors else 0,
            self.ffi.new("char[]", json.dumps(consumer_version_tags).encode("ascii"))
            if consumer_version_tags
            else self.ffi.cast("void *", 0),
            consumer_version_tags.len() if consumer_version_tags else 0,
        )

    def logs(self, verifier_handle: VerifierHandle) -> str:
        """
        Extract the logs for the verification run.

        This needs the memory buffer log sink to be setup before the verification is executed.
        The returned string will need to be freed with the `free_string` function call to avoid leaking memory.

        Will return a NULL pointer if the logs for the verification can not be retrieved.

        const char *pactffi_verifier_logs(const struct VerifierHandle *handle);
        """
        native_logs = self.lib.pactffi_verifier_logs(verifier_handle)
        logs = self.ffi.string(native_logs).decode("utf-8").rstrip().split("\n")
        self.lib.pactffi_string_delete(native_logs)
        return logs

    def logs_for_provider(self, provider_name: str):
        """
        Extract the logs for the verification run.

        This needs the memory buffer log sink to be setup before the verification is executed.
        The returned string will need to be freed with the `free_string` function call to avoid leaking memory.

        Will return a NULL pointer if the logs for the verification can not be retrieved.
        const char *pactffi_verifier_logs_for_provider(const char *provider_name);
        """
        native_logs = self.lib.pactffi_verifier_logs_for_provider(provider_name)
        logs = self.ffi.string(native_logs).decode("utf-8").rstrip().split("\n")
        self.lib.pactffi_string_delete(native_logs)
        return logs

    def output(self, verifier_handle: VerifierHandle, strip_ansi: bool) -> str:
        """
        Extract the standard output for the verification run.

        The returned string will need to be freed with the `free_string` function call to avoid leaking memory.

        * `strip_ansi` - This parameter controls ANSI escape codes. Setting it to a non-zero value
        will cause the ANSI control codes to be stripped from the output.

        Will return a NULL pointer if the handle is invalid.

        const char *pactffi_verifier_output(const struct VerifierHandle *handle, unsigned char strip_ansi);
        """
        native_logs = self.lib.pactffi_verifier_output(verifier_handle, strip_ansi)
        logs = self.ffi.string(native_logs).decode("utf-8").rstrip().split("\n")
        self.lib.pactffi_string_delete(native_logs)
        return logs

    def json(self, verifier_handle: VerifierHandle) -> str:
        """
        Extract the verification result as a JSON document.

        The returned string will need to be freed with the `free_string` function call to avoid leaking memory.

        Will return a NULL pointer if the handle is invalid.

        const char *pactffi_verifier_json(const struct VerifierHandle *handle);
        """
        native_logs = self.lib.pactffi_verifier_json(verifier_handle)
        logs = self.ffi.string(native_logs).decode("utf-8").rstrip().split("\n")
        self.lib.pactffi_string_delete(native_logs)
        return logs
