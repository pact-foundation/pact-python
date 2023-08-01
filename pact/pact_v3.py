"""V3 API for creating a contract and configuring the mock service."""
import os
import os.path
from pact.ffi.native_mock_server import MockServer
from pact.matchers import Matcher
from pact.matchers_v3 import V3Matcher

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
        self.pact_handle = MockServer().new_pact(consumer_name, provider_name)
        self.interactions = []
        self.hostname = hostname or 'localhost'
        self.port = port or 0
        self.transport = transport or 'http'

    def new_http_interaction(self, description):
        """Create a new http interaction."""
        self.interactions.append(self.pact.new_interaction(self.pact_handle, description))
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
        if headers is not None:
            for idx, header in enumerate(headers):
                self.pact.with_request_header(self.interactions[0], header['name'], idx, header['value'])

        if body is not None:
            content_type = 'application/json'  # TODO:- dont hardcode
            self.pact.with_request_body(self.interactions[0], content_type, self.__process_body(body))
        # TODO Add query header
        # self.pact.with_request(method, path, query, headers, self.__process_body(body))
        return self

    # def with_request_with_binary_file(self, content_type, file, method='POST', path='/', query=None, headers=None):
    #     """Define the request that the client is expected to perform with a binary body."""
    #     self.pact.add_request_binary_file(content_type, file, method, path, query, headers)
    #     return self

    def will_respond_with(self, status=200, headers=None, body=None):
        """Define the response the server is expected to create."""
        # self.pact.will_respond_with(status, headers, self.__process_body(body))

        self.pact.response_status(self.interactions[0], status)
        if headers is not None:
            for idx, header in enumerate(headers):
                self.pact.with_request_header(self.interactions[0], header['name'], idx, header['value'])
        if body is not None:
            content_type = 'application/json'  # TODO:- dont hardcode
            self.pact.with_response_body(self.interactions[0], content_type, self.__process_body(body))
        return self

    def __enter__(self):
        """
        Enter a Python context.

        Sets up the mock service to expect the client requests.
        """
        self.mock_server = self.pact.start_mock_server(self.pact_handle, self.hostname, self.port, self.transport, None)
        return self.mock_server

    def __exit__(self):
        # def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit a Python context.

        Calls the mock service to verify that all interactions occurred as
        expected, and has it write out the contracts to disk.
        """
        return self.pact.verify(self.mock_server, self.pact_handle, self.pact_dir)
        # test_results = self.mock_server.get_test_result()
        # print("--> EXIT", exc_type, test_results)
        # if exc_type is not None or test_results is not None:
        #     error = "Test failed for the following reasons:"
        #     if exc_type is not None:
        #         error += "\n\n\tTest code failed with an error: " + getattr(exc_val, 'message', repr(exc_val))
        #     if test_results is not None:
        #         error += "\n\n\tMock server failed with the following: "
        #         i = 1
        #         for result in test_results:
        #             error += "\n\t  {}) {} {}".format(i, result["method"], result["path"])

        #             if 'mismatches' in result:
        #                 j = 1
        #                 for mismatch in result['mismatches']:
        #                     error += "\n\t    {}) {} {}".format(j, mismatch["type"], mismatch["mismatch"])

        #             if result['type'] == "request-not-found":
        #                 error += "\n    The following request was not expected: {}".format(result["request"])

        #             if result['type'] == "missing-request":
        #                 error += "\n    The following request was expected but not received: {}" \
        #                     .format(result["request"])

        #             i += 1

        #     raise RuntimeError(error)
        # else:
        #     self.mock_server.write_pact_file(self.pact_dir, False)
        #     self.mock_server.shutdown()

    def __process_body(self, body):
        if isinstance(body, dict):
            return {key: self.__process_body(value) for key, value in body.items()}
        elif isinstance(body, list):
            return [self.__process_body(value) for value in body]
        elif isinstance(body, V3Matcher):
            return self.__process_body(body.generate())
        elif isinstance(body, Matcher):
            return self.__process_body(body.generate())
        else:
            return body
