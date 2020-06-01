import os
import os.path
from pact_python_v3 import init, PactNative
from pact.matchers_v3 import V3Matcher

class PactV3(object):
    """
    Represents a contract between a consumer and provider (supporting Pact V3 specification).

    Provides Python context handlers to configure the Pact mock service to
    perform tests on a Python consumer.
    """

    def __init__(self, consumer_name, provider_name, pact_dir=None, log_level=None):
        self.consumer_name = consumer_name
        self.provider_name = provider_name
        self.log_level = log_level
        self.pact_dir = pact_dir or os.path.join(os.getcwd(), 'pacts')
        init(log_level = log_level)
        self.pact = PactNative(consumer_name, provider_name)
        
    def given(self, provider_state, params={}):
        self.pact.given(provider_state, params)
        return self

    def upon_receiving(self, description):
        self.pact.upon_receiving(description)
        return self

    def with_request(self, method='GET', path='/', query = None, headers = None, body = None):
        self.pact.with_request(method, path, query, headers, self.__process_body(body))
        return self

    def will_respond_with(self, status=200, headers = None, body = None):
        self.pact.will_respond_with(status, headers, self.__process_body(body))
        return self

    def __enter__(self):
        self.mock_server = self.pact.start_mock_server()
        return self.mock_server

    def __exit__(self, exc_type, exc_val, exc_tb):
        test_result = self.mock_server.get_test_result()
        print("--> EXIT", exc_type, test_result)
        if exc_type is not None or test_result is not None:
            error = "Test failed for the following reasons:"
            if exc_type is not None:
                error += "\n\n\tTest code failed with an error: " + getattr(exc_val, 'message', repr(exc_val))
            if test_result is not None:
                error += "\n\n\tMock server failed with the following mismatches: "
                i = 1
                for mismatches in test_result:
                    error += "\n\t  {}) {} {}".format(i, mismatches["method"], mismatches["path"])
                    for mismatch in mismatches["mismatches"]:
                        error += "\n\t      {} - {}".format(mismatch["type"], mismatch["mismatch"])
                    i += 1
            raise RuntimeError(error)
        else:
            self.mock_server.write_pact_file(self.pact_dir)
            self.mock_server.shutdown()

    def __process_body(self, body):
        if isinstance(body, dict):
            return { key: self.__process_body(value) for key, value in body.items() }
        elif isinstance(body, list):
            return [ self.__process_body(value) for value in body ]
        elif isinstance(body, V3Matcher):
            return self.__process_body(body.generate())
        else:
            return body
