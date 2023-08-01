"""Mock Server Wrapper to pact reference dynamic libraries using FFI."""
from enum import Enum, unique
from typing import List, NamedTuple
from pact.__version__ import __version__
from pact.ffi.pact_ffi import PactFFI
from pact.ffi.utils import se
import json

@unique
class MockServerStatus(Enum):
    """Return codes from a verify request.

    As per: https://docs.rs/pact_ffi/0.3.4/pact_ffi/mock_server/index.html#mock_server_matched
    """

    SUCCESS = True  # Operation succeeded
    MOCK_SERVER_FAILED = False  # The mock server process failed, see output for errors
    # NULL_POINTER = 2  # A null pointer was received
    # PANIC = 3  # The method panicked
    # INVALID_ARGS = 4  # Invalid arguments were provided to the verification process


class MockServerResult(NamedTuple):
    """Wrap up the return code, and log output."""

    return_code: MockServerStatus
    logs: List[str]

class MockServer(PactFFI):
    """A Pact MockServer Wrapper.

    This interfaces with the Rust FFI crate pact_ffi, specifically the
    `mock_server` & `plugins` modules.

    .. mock_server:
        https://docs.rs/pact_ffi/0.3.4/pact_ffi/mock_server/index.html
    .. plugins:
        https://docs.rs/pact_ffi/0.3.4/pact_ffi/plugins/index.html
    """

    def __new__(cls):
        """Create a new instance of the MockServer."""
        return super(MockServer, cls).__new__(cls)

    def new_pact(self, consumer: str, provider: str):
        """
        Create a new Pact model and returns a handle to it.

        * `consumer_name` - The name of the consumer for the pact.
        * `provider_name` - The name of the provider for the pact.

        Returns a new `PactHandle`. The handle will need to be freed with the `pactffi_free_pact_handle`
        method to release its resources.
        """
        pact_handle = self.lib.pactffi_new_pact(se(consumer), se(provider))
        self.lib.pactffi_with_pact_metadata(pact_handle, b'pact-python', b'version', se(__version__))
        return pact_handle

    def with_specification(self, pact_handle, version=int):
        """
        Set the specification version for a given Pact model.

        Returns false if the interaction or Pact can't be
        modified (i.e. the mock server for it has already started) or the version is invalid.

        * `pact` - Handle to a Pact model
        * `version` - the spec version to use
        """
        return self.lib.pactffi_with_specification(pact_handle, version)

    def using_plugin(self, pact_handle, name=str, version=str):
        """
        Add a plugin to be used by the test.

        The plugin needs to be installed correctly for this function to work.

        * `plugin_name` is the name of the plugin to load.
        * `plugin_version` is the version of the plugin to load. It is optional, and can be NULL.

        Returns zero on success, and a positive integer value on failure.

        Note that plugins run as separate processes, so will need to be cleaned up afterwards by
        calling `pactffi_cleanup_plugins` otherwise you will have plugin processes left running.

        # Safety

        `plugin_name` must be a valid pointer to a NULL terminated string. `plugin_version` may be null,
        and if not NULL must also be a valid pointer to a NULL terminated string. Invalid
        pointers will result in undefined behaviour.

        # Errors

        * `1` - A general panic was caught.
        * `2` - Failed to load the plugin.
        * `3` - Pact Handle is not valid.

        When an error errors, LAST_ERROR will contain the error message.
        """
        return self.lib.pactffi_using_plugin(pact_handle, se(name), se(version))

    def new_interaction(self, pact_handle, description=str):
        """
        Create a new HTTP Interaction and returns a handle to it.

        * `description` - The interaction description. It needs to be unique for each interaction.

        Returns a new `InteractionHandle`.
        """
        return self.lib.pactffi_new_interaction(pact_handle, se(description))

    def new_message(self, pact_handle, description=str):
        """
        Create a new Pact Message model and returns a handle to it.

        * `consumer_name` - The name of the consumer for the pact.
        * `provider_name` - The name of the provider for the pact.

        Returns a new `MessagePactHandle`. The handle will need to be freed with the `pactffi_free_message_pact_handle`
        function to release its resources.
        """
        return self.lib.pactffi_new_message(pact_handle, se(description))

    def upon_receiving(self, interaction_handle, description=str):
        """
        Set the description for the Interaction.

        Returns false if the interaction or Pact can't be
        modified (i.e. the mock server for it has already started)

        * `description` - The interaction description. It needs to be unique for each interaction.
        """
        return self.lib.pactffi_upon_receiving(interaction_handle, se(description))

    def given(self, interaction_handle, description=str):
        """
        Add a provider state to the Interaction.

        Returns false if the interaction or Pact can't be
        modified (i.e. the mock server for it has already started)

        * `description` - The provider state description. It needs to be unique.
        """
        return self.lib.pactffi_given(interaction_handle, se(description))

    def with_request(self, interaction_handle, method=str, path=str):
        r"""
        Configure the request for the Interaction.

        Returns false if the interaction or Pact can't be
        modified (i.e. the mock server for it has already started)

        * `method` - The request method. Defaults to GET.
        * `path` - The request path. Defaults to `/`.

        To include matching rules for the path (only regex really makes sense to use), include the
        matching rule JSON format with the value as a single JSON document. I.e.

        ```c
        const char* value = "{\"value\":\"/path/to/100\", \"pact:matcher:type\":\"regex\", \"regex\":\"\\/path\\/to\\/\\\\d+\"}";
        pactffi_with_request(handle, "GET", value);
        ```
        See [IntegrationJson.md](https://github.com/pact-foundation/pact-reference/blob/master/rust/pact_ffi/IntegrationJson.md)
        """
        return self.lib.pactffi_with_request(interaction_handle, se(method), se(path))

    def with_header(self, interaction_handle, req_or_res="res" or "req", name=str, index=int, value=str):
        r"""
        Configure a header for the Interaction.

        Returns false if the interaction or Pact can't be
        modified (i.e. the mock server for it has already started)

         * `part` - The part of the interaction to add the header to (Request or Response).
         * `name` - the header name.
         * `value` - the header value.
         * `index` - the index of the value (starts at 0). You can use this to create a header with multiple values

         To setup a header with multiple values, you can either call this function multiple times
         with a different index value, i.e. to create `x-id=2, 3`

         ```c
         pactffi_with_header_v2(handle, InteractionPart::Request, "x-id", 0, "2");
         pactffi_with_header_v2(handle, InteractionPart::Request, "x-id", 1, "3");
         ```

         Or you can call it once with a JSON value that contains multiple values:

         ```c
         const char* value = "{\"value\": [\"2\",\"3\"]}";
         pactffi_with_header_v2(handle, InteractionPart::Request, "x-id", 0, value);
         ```

         To include matching rules for the header, include the matching rule JSON format with
         the value as a single JSON document. I.e.

         ```c
         const char* value = "{\"value\":\"2\", \"pact:matcher:type\":\"regex\", \"regex\":\"\\\\d+\"}";
         pactffi_with_header_v2(handle, InteractionPart::Request, "id", 0, value);
         ```
         See [IntegrationJson.md](https://github.com/pact-foundation/pact-reference/blob/master/rust/pact_ffi/IntegrationJson.md)

         # Safety
         The name and value parameters must be valid pointers to NULL terminated strings.
        """
        return self.lib.pactffi_with_header_v2(interaction_handle, 0 if req_or_res == 'req' else 1, se(name), index, se(value))

    def with_request_header(self, interaction_handle, name=str, index=int, value=str):
        """
        Configure a request header for the Interaction.

        See with_header for full detail
        """
        return self.with_header(interaction_handle, "req", name, index, value)

    def with_response_header(self, interaction_handle, name=str, index=int, value=str):
        """
        Configure a response header for the Interaction.

        See with_header for full detail
        """
        return self.with_header(interaction_handle, "res", name, index, value)

    def with_body(self, interaction_handle, req_or_res="res" or "req", content_type=str, body=str):
        r"""
        Add the body for the interaction.

        Returns false if the interaction or Pact can't be
         modified (i.e. the mock server for it has already started)

         * `part` - The part of the interaction to add the body to (Request or Response).
         * `content_type` - The content type of the body. Defaults to `text/plain`. Will be ignored if a content type
           header is already set.
         * `body` - The body contents. For JSON payloads, matching rules can be embedded in the body. See
         [IntegrationJson.md](https://github.com/pact-foundation/pact-reference/blob/master/rust/pact_ffi/IntegrationJson.md)

         For HTTP and async message interactions, this will overwrite the body. With asynchronous messages, the
         part parameter will be ignored. With synchronous messages, the request contents will be overwritten,
         while a new response will be appended to the message.

         # Safety

         The interaction contents and content type must either be NULL pointers, or point to valid
         UTF-8 encoded NULL-terminated strings. Otherwise, behaviour is undefined.

         # Error Handling

         If the contents is a NULL pointer, it will set the body contents as null. If the content
         type is a null pointer, or can't be parsed, it will set the content type as TEXT.
         Returns false if the interaction or Pact can't be modified (i.e. the mock server for it has
         already started) or an error has occurred.
        """
        if 'json' in content_type:
            encoded_body = se(json.dumps(body))
        else:
            encoded_body = se(body)
        return self.lib.pactffi_with_body(interaction_handle, 0 if req_or_res == 'req' else 1, se(content_type), encoded_body)

    def with_request_body(self, interaction_handle, content_type=str, body=str):
        """
        Add the request body for the interaction.

        See with_body for full detail

        """
        return self.with_body(interaction_handle, "req", content_type, body)

    def with_response_body(self, interaction_handle, content_type=str, body=str):
        """
        Add the response body for the interaction.

        See with_body for full detail

        """
        return self.with_body(interaction_handle, "res", content_type, body)

    def response_status(self, interaction_handle, code=int):
        """
        Configure the response for the Interaction.

        Returns false if the interaction or Pact can't be
        modified (i.e. the mock server for it has already started)

        `status` - the response status. Defaults to 200.
        """
        return self.lib.pactffi_response_status(interaction_handle, code)

    def message_expects_to_receive(self, message_handle, description=str):
        """
        Set the description for the Message.

        * `description` - The message description. It needs to be unique for each message.
        """
        self.lib.pactffi_message_expects_to_receive(message_handle, se(description))

    def message_given(self, message_handle, description=str):
        """
        Add a provider state to the Interaction.

        * `description` - The provider state description. It needs to be unique for each message
        """
        self.lib.pactffi_message_given(message_handle, se(description))

    def message_with_contents(self, message_handle, content_type=str, body=str):
        """
        Add the contents of the Message.

        Accepts JSON, binary and other payload types. Binary data will be base64 encoded when serialised.

        Note: For text bodies (plain text, JSON or XML), you can pass in a C string (NULL terminated)
        and the size of the body is not required (it will be ignored). For binary bodies, you need to
        specify the number of bytes in the body.

        * `content_type` - The content type of the body. Defaults to `text/plain`, supports JSON structures with matchers and binary data.
        * `body` - The body contents as bytes. For text payloads (JSON, XML, etc.), a C string can be used and matching rules can be embedded in the body.
        * `content_type` - Expected content type (e.g. application/json, application/octet-stream)
        * `size` - number of bytes in the message body to read. This is not required for text bodies (JSON, XML, etc.).
        """
        if 'json' in content_type:
            length = len(json.dumps(body))
            size = length + 1
            encoded_body = self.ffi.new("char[]", se(json.dumps(body)))
        else:
            length = len(body)
            size = length + 1
            encoded_body = self.ffi.new("char[]", se(body))
        return self.lib.pactffi_message_with_contents(message_handle, se(content_type), encoded_body, size)

    def start_mock_server(self, pact_handle, hostname=str, port=int, transport=str, transport_config=str or None):
        """
        Create a mock server for the provided Pact handle and transport.

        If the transport is not
        provided (it is a NULL pointer or an empty string), will default to an HTTP transport. The
        address is the interface bind to, and will default to the loopback adapter if not specified.
        Specifying a value of zero for the port will result in the operating system allocating the port.

        Parameters:
        * `pact` - Handle to a Pact model created with created with `pactffi_new_pact`.
        * `addr` - Address to bind to (i.e. `127.0.0.1` or `[::1]`).
                    Must be a valid UTF-8 NULL-terminated string, or NULL or empty,
                    in which case the loopback adapter is used.
        * `port` - Port number to bind to. A value of zero will result in the operating system allocating an available port.
        * `transport` - The transport to use (i.e. http, https, grpc).
                        Must be a valid UTF-8 NULL-terminated string, or NULL or empty,
                        in which case http will be used.
        * `transport_config` - (OPTIONAL) Configuration for the transport as a valid JSON string. Set to NULL or empty if not required.

        The port of the mock server is returned.

        # Safety
        NULL pointers or empty strings can be passed in for the address, transport and transport_config,
        in which case a default value will be used. Passing in an invalid pointer will result in undefined behaviour.

        # Errors

        Errors are returned as negative values.

        | Error | Description |
        |-------|-------------|
        | -1 | An invalid handle was received. Handles should be created with `pactffi_new_pact` |
        | -2 | transport_config is not valid JSON |
        | -3 | The mock server could not be started |
        | -4 | The method panicked |
        | -5 | The address is not valid |

        int32_t pactffi_create_mock_server_for_transport(PactHandle pact,
                                                 const char *addr,
                                                 uint16_t port,
                                                 const char *transport,
                                                 const char *transport_config);

        """
        mock_server_port = self.lib.pactffi_create_mock_server_for_transport(pact_handle, se(hostname), port, se(
            transport), se('{}') if transport_config is None else se(transport_config))
        assert mock_server_port not in ['-1', '-2', '-3', '-4', '-5']
        print(f"Mock server started: {mock_server_port}")
        return mock_server_port

    def message_reify(self, message_handle):
        """
        Reify the given message.

        Reification is the process of stripping away any matchers, and returning the original contents.
        NOTE: the returned string needs to be deallocated with the `free_string` function
        """
        reified = self.lib.pactffi_message_reify(message_handle)
        return self.ffi.string(reified).decode('utf-8')

    def new_sync_message_interaction(self, pact_handle, description: str):
        """
        Create a new synchronous message interaction (request/response) and return a handle to it.

        * `description` - The interaction description. It needs to be unique for each interaction.

        Returns a new `InteractionHandle`.
        """
        return self.lib.pactffi_new_sync_message_interaction(pact_handle, se(description))

    def interaction_contents(self, message_handle, req_or_res="res" or "req", content_type=str, body=str or json):
        """
        Set the interaction part using a plugin.

        The contents is a JSON string that will be passed on to
        the plugin to configure the interaction part. Refer to the plugin documentation on the format
        of the JSON contents.

        Returns zero on success, and a positive integer value on failure.

        * `interaction` - Handle to the interaction to configure.
        * `part` - The part of the interaction to configure (request or response). It is ignored for messages.
        * `content_type` - NULL terminated C string of the content type of the part.
        * `contents` - NULL terminated C string of the JSON contents that gets passed to the plugin.

        # Safety

        `content_type` and `contents` must be a valid pointers to NULL terminated strings. Invalid
        pointers will result in undefined behaviour.

        # Errors

        * `1` - A general panic was caught.
        * `2` - The mock server has already been started.
        * `3` - The interaction handle is invalid.
        * `4` - The content type is not valid.
        * `5` - The contents JSON is not valid JSON.
        * `6` - The plugin returned an error.

        When an error errors, LAST_ERROR will contain the error message.
        """
        if 'json' in content_type:
            encoded_body = self.ffi.new("char[]", se(json.dumps(body)))
        else:
            encoded_body = self.ffi.new("char[]", se(body))
        return self.lib.pactffi_interaction_contents(message_handle, 0 if req_or_res == 'req' else 1, se(content_type), encoded_body)

    def with_message_request_contents(self, message_handle, content_type=str, body=str or json):
        """
        Set the request interaction part using a plugin.

        see interaction_contents for details
        """
        self.interaction_contents(message_handle, "req", content_type, body)

    def with_message_response_contents(self, message_handle, content_type=str, body=str or json):
        """
        Set the response interaction part using a plugin.

        see interaction_contents for details
        """
        self.interaction_contents(message_handle, "req", content_type, body)

    def mock_server_matched(self, mock_server_port=int):
        """
        External interface to check if a mock server has matched all its requests.

        The port number is passed in, and if all requests have been matched, true is returned.

        False is returned if
          - there is no mock server on the given port
          - any request has not been successfully matched
          - the method panics.
        """
        result = self.lib.pactffi_mock_server_matched(mock_server_port)
        print(f"Pact - Got matching client requests: {result}")
        return result

    def write_pact_file(self, mock_server_port=int, directory=str, overwrite=bool):
        """
        External interface to trigger a mock server to write out its pact file.

        This function should be called if all the consumer tests have passed.
        The directory to write the file to is passed as the second parameter.
        If a NULL pointer is passed, the current working directory is used.

        If overwrite is true, the file will be overwritten with the contents of the current pact.
        Otherwise, it will be merged with any existing pact file.

        Returns 0 if the pact file was successfully written. Returns a positive code if the file can
        not be written, or there is no mock server running on that port or the function panics.

        # Errors

        Errors are returned as positive values.

        | Error | Description |
        |-------|-------------|
        | 1 | A general panic was caught |
        | 2 | The pact file was not able to be written |
        | 3 | A mock server with the provided port was not found |
        """
        print(f"Writing pact file to {directory}")
        result = self.lib.pactffi_write_pact_file(mock_server_port, se(directory), overwrite)
        print(f"Pact file writing results: {result}")
        return result

    def write_message_pact_file(self, message_pact=int, directory=str, overwrite=bool):
        """
        External interface to write out the message pact file.

        This function should be called if all the consumer tests have passed.
        The directory to write the file to is passed as the second parameter.
        If a NULL pointer is passed, the current working directory is used.

        If overwrite is true, the file will be overwritten with the contents of the current pact.
        Otherwise, it will be merged with any existing pact file.

        Returns 0 if the pact file was successfully written. Returns a positive code if the file can
        not be written, or there is no mock server running on that port or the function panics.

        # Errors

        Errors are returned as positive values.

        | Error | Description |
        |-------|-------------|
        | 1 | The pact file was not able to be written |
        | 2 | The message pact for the given handle was not found |
        """
        print(f"Writing pact message file to {directory}")
        result = self.lib.pactffi_write_message_pact_file(message_pact, se(directory), overwrite)
        print(f"Pact message file writing results: {result}")
        return result

    def verify(self, mock_server_port, pact_handle, PACT_FILE_DIR, message_pact=None):
        """
        External interface to check if a mock server has matched all its requests.

        The port number is passed in, and if all requests have been matched, true is returned.
        False is returned if there
        * is no mock server on the given port, or if any request has not been successfully matched, or
        * the method panics.
        """
        result = self.mock_server_matched(mock_server_port)
        if result is True:
            self.write_pact_file(mock_server_port, PACT_FILE_DIR, False)
            if message_pact is not None:
                self.write_message_pact_file(message_pact, PACT_FILE_DIR, False)
            logs = ["success"]
        else:
            print('pactffi_mock_server_matched did not match')
            mismatches = self.lib.pactffi_mock_server_mismatches(mock_server_port)
            if mismatches:
                logs = json.loads(self.ffi.string(mismatches))
                print(json.dumps(result, indent=4))

        # Cleanup
        self.lib.pactffi_cleanup_mock_server(mock_server_port)
        self.lib.pactffi_cleanup_plugins(pact_handle)
        return MockServerResult(result, logs)

def mock_server_mismatches(self, mock_server_port=int):
    """
    External interface to get all the mismatches from a mock server.

    The port number of the mock
    server is passed in, and a pointer to a C string with the mismatches in JSON format is
    returned.

    **NOTE:** The JSON string for the result is allocated on the heap, and will have to be freed
    once the code using the mock server is complete. The [`cleanup_mock_server`](fn.cleanup_mock_server.html) function is
    provided for this purpose.

    # Errors

    If there is no mock server with the provided port number, or the function panics, a NULL
    pointer will be returned. Don't try to dereference it, it will not end well for you.
    """
    mismatches = self.lib.pactffi_mock_server_mismatches(mock_server_port)
    if mismatches:
        result = json.loads(self.ffi.string(mismatches))
        print(json.dumps(result, indent=4))
        self.lib.pactffi_string_delete(result)
        return result
    else:
        return []
