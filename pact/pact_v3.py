"""V3 API for creating a contract and configuring the mock service."""
import os
import os.path
from pact.ffi.native_mock_server import MockServer, MockServerResult
from pact.matchers_v3 import V3Matcher
from pact.verifier_v3 import CustomHeader

class PactV3(object):
    """
    Represents a contract between a consumer and provider (supporting Pact V3 specification).

    Provides Python context handlers to configure the Pact mock service to
    perform tests on a Python consumer.
    """

    def __init__(self, consumer_name, provider_name, hostname=None, port=None, transport=None, pact_dir=None, log_level=None):
        """Create a Pact V3 instance."""
        self.consumer_name = consumer_name
        self.provider_name = provider_name
        self.log_level = log_level
        self.pact_dir = pact_dir or os.path.join(os.getcwd(), 'pacts')
        # init(log_level=log_level)
        self.pact = MockServer()
        self.pact_handle = None
        self.interactions = []
        self.hostname = hostname or '127.0.0.1'
        self.port = port or 0
        self.transport = transport or 'http'

    def new_http_interaction(self, description):
        """Create a new http interaction."""
        self.pact_handle = MockServer().new_pact(self.consumer_name, self.provider_name)
        self.interactions = [self.pact.new_interaction(self.pact_handle, description)]
        return self

    def given(self, provider_state, params={}):
        """Define the provider state for this pact."""
        self.pact.given(self.interactions[0], provider_state)
        # self.pact.given(self.interactions[0],provider_state, params)
        return self

    def upon_receiving(self, description):
        """Define the name of this contract."""
        self.pact.upon_receiving(self.interactions[0], description)
        # self.pact.upon_receiving(description)
        return self

    def with_request(self, method='GET', path='/', query=None, headers=None, body=None):
        """Define the request that the client is expected to perform."""
        self.pact.with_request(self.interactions[0], method, path)
        # index = 0
        if headers is not None:
            for header in headers:
                print(header['name'])
                print(header['value'])
                # TODO:- deal with multi-value headers and increment the header value appropriately
                self.pact.with_response_header(self.interactions[0], header['name'], 0, header['value'])
                # index += 1
                if header['name'] in ['Content-Type', 'content-type']:
                    content_type = header['value']

        if body is not None:
            self.pact.with_request_body(self.interactions[0], content_type, self.__process_body(body))
        # TODO Add query header
        # self.pact.with_request(method, path, query, headers, self.__process_body(body))
        return self

    def with_request_with_binary_file(self, method='POST', path='/', query=None, headers=None, file=None):
        """Define the request that the client is expected to perform."""
        self.pact.with_request(self.interactions[0], method, path)
        # index = 0
        if headers is not None:
            for header in headers:
                print(header['name'])
                print(header['value'])
                self.pact.with_request_header(self.interactions[0], header['name'], 0, header['value'])
                # index += 1
                if header['name'] in ['Content-Type', 'content-type']:
                    content_type = header['value']

        if file is not None:
            with open(file, 'rb') as f:
                file_content = f.read()  # Read whole file in the file_content string
            self.pact.with_binary_file(self.interactions[0], "req", content_type, self.__process_body(file_content))
        # TODO Add query header
        # self.pact.with_request(method, path, query, headers, self.__process_body(body))
        return self

    def will_respond_with(self, status=200, headers: [CustomHeader] = None, body=None):
        """Define the response the server is expected to create."""
        # self.pact.will_respond_with(status, headers, self.__process_body(body))

        self.pact.response_status(self.interactions[0], status)
        index = 0
        if headers is not None:
            for header in headers:
                print(header['name'])
                print(header['value'])
                print(index)
                # TODO:- deal with multi-value headers and increment the header value appropriately
                self.pact.with_response_header(self.interactions[0], header['name'], 0, header['value'])
                index += 1
                if header['name'] in ['Content-Type', 'content-type']:
                    content_type = header['value']

        if body is not None:
            # self.pact.with_response_body(self.interactions[0], content_type, self.__process_body(body))
            self.pact.with_response_body(self.interactions[0], content_type, self.__process_body(body))
        return self

    def __enter__(self):
        """
        Enter a Python context.

        Sets up the mock service to expect the client requests.
        """
        # self.setup()
        return

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit a Python context.

        Calls the mock service to verify that all interactions occurred as
        expected, and has it write out the contracts to disk.
        """
        if (exc_type, exc_val, exc_tb) != (None, None, None):
            return

        return

    def start_service(self) -> int:
        """
        Start the external Mock Service.

        :raises RuntimeError: if there is a problem starting the mock service.
        """
        self.mock_server_port = self.pact.start_mock_server(self.pact_handle, self.hostname, self.port, self.transport, None)
        return self.mock_server_port

    def verify(self) -> MockServerResult:
        """
        Have the mock service verify all interactions occurred.

        Calls the mock service to verify that all interactions occurred as
        expected, and has it write out the contracts to disk.

        :raises AssertionError: When not all interactions are found.
        """
        # self.interactions = []
        return self.pact.verify(self.mock_server_port, self.pact_handle, self.pact_dir)

    def __process_body(self, body):
        if isinstance(body, dict):
            return {key: self.__process_body(value) for key, value in body.items()}
        elif isinstance(body, list):
            return [self.__process_body(value) for value in body]
        elif isinstance(body, V3Matcher):
            return self.__process_body(body.generate())
        else:
            return body
