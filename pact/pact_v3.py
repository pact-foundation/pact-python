import os
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
        self.pact_dir = pact_dir or os.getcwd() + 'pacts'
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
        print("--> ENTER")
        self.mock_server = self.pact.start_mock_server()
        return self.mock_server

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("--> EXIT")

    def __process_body(self, body, count = 0):
        print("--> ", type(body), count)
        if isinstance(body, dict):
            return { key: self.__process_body(value, count = count + 1) for key, value in body.items() }
        elif isinstance(body, list):
            return [ self.__process_body(value, count = count + 1) for value in body ]
        elif isinstance(body, V3Matcher):
            return self.__process_body(body.generate(), count = count + 1)
        else:
            return body
