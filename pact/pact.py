"""API for creating a contract and configuring the mock service."""
import requests

from .matchers import from_term


class Pact(object):
    """
    Represents a contract between a consumer and provider.

    Provides Python context handlers to configure the Pact mock service to
    perform tests on a Python consumer. For example:

    >>> from pact import Consumer, Provider
    >>> pact = Consumer('consumer').has_pact_with(Provider('provider'))
    >>> (pact.given('the echo service is available')
    ...  .upon_receiving('a request is made to the echo service')
    ...  .with_request('get', '/echo', query={'text': 'Hello!'})
    ...  .will_respond_with(200, body='Hello!'))
    >>> with pact:
    ...   requests.get('http://localhost:1234/echo?text=Hello!')

    The GET request is made to the mock service, which will verify that it
    was a GET to /echo with a query string with a key named `text` and its
    value is `Hello!`. If the request does not match an error is raised, if it
    does match the defined interaction, it will respond with the text `Hello!`.
    """

    HEADERS = {'X-Pact-Mock-Service': 'true'}

    def __init__(self, consumer, provider, host_name='localhost', port=1234):
        """
        Constructor for Pact.

        :param consumer: The consumer for this contract.
        :type consumer: pact.Consumer
        :param provider: The provider for this contract.
        :type provider: pact.Provider
        :param host_name: The host name where the mock service is running.
        :type host_name: str
        :param port: The port number where the mock service is running.
        :type port: int
        """
        self.BASE_URI = 'http://{host_name}:{port}'.format(
            host_name=host_name, port=port)

        self.consumer = consumer
        self.provider = provider
        self._description = None
        self._provider_state = None
        self._request = None
        self._response = None
        self._scenario = None

    def given(self, provider_state):
        """
        Define the provider state for this pact.

        When the provider verifies this contract, they will use this field to
        setup pre-defined data that will satisfy the response expectations.

        :param provider_state: The short sentence that is unique to describe
            the provider state for this contract.
        :type provider_state: basestring
        :rtype: Pact
        """
        self._provider_state = provider_state
        return self

    def upon_receiving(self, scenario):
        """
        Define the name of this contract.

        :param scenario: A unique name for this contract.
        :type scenario: basestring
        :rtype: Pact
        """
        self._description = scenario
        return self

    def with_request(self, method, path, body=None, headers=None, query=None):
        """
        Define the request the request that the client is expected to perform.

        :param method: The HTTP method.
        :type method: str
        :param path: The path portion of the URI the client will access.
        :type path: str
        :param body: The request body, can be a string or an object that will
            serialize to JSON, like list or dict, defaults to None.
        :type body: list, dict or None
        :param headers: The headers the client is expected to include on with
            this request. Defaults to None.
        :type headers: dict or None
        :param query: The query options the client is expected to send. Can be
            a dict of keys and values, or a URL encoded string.
            Defaults to None.
        :type query: dict, basestring, or None
        :rtype: Pact
        """
        self._request = Request(
            method, path, body=body, headers=headers, query=query).json()

        return self

    def will_respond_with(self, status, headers=None, body=None):
        """
        Define the response the server is expected to create.

        :param status: The HTTP status code.
        :type status: int
        :param headers: All required headers. Defaults to None.
        :type headers: dict or None
        :param body: The response body, or a collection of Matcher objects to
            allow for pattern matching. Defaults to None.
        :type body: Matcher, dict, list, basestring, or None
        :rtype: Pact
        """
        self._response = Response(status, headers=headers, body=body).json()
        return self

    def __enter__(self):
        """
        Handler for entering a Python context.

        Sets up the mock service to expect the client requests.
        """
        payload = {
            'description': self._description,
            'provider_state': self._provider_state,
            'request': self._request,
            'response': self._response
        }

        resp = requests.delete(
            self.BASE_URI + '/interactions', headers=self.HEADERS)

        assert resp.status_code == 200, resp.content
        resp = requests.post(
            self.BASE_URI + '/interactions',
            headers=self.HEADERS, json=payload)

        assert resp.status_code == 200, resp.content

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Handler for exiting a Python context.

        Calls the mock service to verify that all interactions occurred as
        expected, and has it write out the contracts to disk.
        """
        if (exc_type, exc_val, exc_tb) != (None, None, None):
            return

        resp = requests.get(
            self.BASE_URI + '/interactions/verification', headers=self.HEADERS)
        assert resp.status_code == 200, resp.content
        payload = {
            'consumer': {'name': self.consumer.name},
            'provider': {'name': self.provider.name},
            'pact_dir': '/opt/contracts'
        }
        resp = requests.post(
            self.BASE_URI + '/pact', headers=self.HEADERS, json=payload)
        assert resp.status_code == 200, resp.content


class FromTerms(object):
    """Base class for objects built from a collection of Matchers."""

    def json(self):
        """Convert the object to a JSON version of the mock service."""
        raise NotImplementedError


class Request(FromTerms):
    """Represents an HTTP request and supports Matchers on its properties."""

    def __init__(self, method, path, body=None, headers=None, query=''):
        """
        Create a new instance of Request.

        :param method: The HTTP method that is expected.
        :type method: str
        :param path: The URI path that is expected on this request.
        :type path: str
        :param body: The contents of the body of the expected request.
        :type body: str, dict, list
        :param headers: The headers of the expected request.
        :type headers: dict
        :param query: The URI query of the expected request.
        :type query: str or dict
        """
        self.method = method
        self.path = path
        self.body = from_term(body)
        self.headers = from_term(headers)
        self.query = from_term(query)

    def json(self):
        """Convert the Request to a JSON version for the mock service."""
        request = {'method': self.method, 'path': self.path}

        if self.headers:
            request['headers'] = self.headers

        if self.body:
            request['body'] = self.body

        if self.query:
            request['query'] = self.query

        return request


class Response(FromTerms):
    """Represents an HTTP response and supports Matchers on its properties."""

    def __init__(self, status, headers=None, body=None):
        """
        Create a new Response.

        :param status: The expected HTTP status of the response.
        :type status: int
        :param headers: The expected headers of the response.
        :type headers: dict
        :param body: The expected body of the response.
        :type body: str, dict, or list
        """
        self.status = status
        self.body = from_term(body)
        self.headers = from_term(headers)

    def json(self):
        """Convert the Response to a JSON version for the mock service."""
        response = {'status': self.status}
        if self.body:
            response['body'] = self.body

        if self.headers:
            response['headers'] = self.headers

        return response
