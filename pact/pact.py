"""API for creating a contract and configuring the mock service."""
from __future__ import unicode_literals

import os
from subprocess import Popen

import requests

from .constants import MOCK_SERVICE_PATH
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
    ...   requests.get(pact.uri + '/echo?text=Hello!')

    The GET request is made to the mock service, which will verify that it
    was a GET to /echo with a query string with a key named `text` and its
    value is `Hello!`. If the request does not match an error is raised, if it
    does match the defined interaction, it will respond with the text `Hello!`.
    """

    HEADERS = {'X-Pact-Mock-Service': 'true'}

    def __init__(self, consumer, provider, host_name='localhost', port=1234,
                 log_dir=None, ssl=False, sslcert=None, sslkey=None,
                 cors=False, pact_dir=None, version='2.0.0'):
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
        :param log_dir: The directory where logs should be written. Defaults to
            the current directory.
        :type log_dir: str
        :param ssl: Flag to control the use of a self-signed SSL cert to run
            the server over HTTPS , defaults to False.
        :type ssl: bool
        :param sslcert: Path to a custom self-signed SSL cert file, 'ssl'
            option must be set to True to use this option. Defaults to None.
        :type sslcert: str
        :param sslkey: Path to a custom key and self-signed SSL cert key file,
            'ssl' option must be set to True to use this option.
            Defaults to None.
        :type sslkey: str
        :param cors: Allow CORS OPTION requests to be accepted,
            defaults to False.
        :type cors: bool
        :param pact_dir: Directory where the resulting pact files will be
            written. Defaults to the current directory.
        :type pact_dir: str
        :param version: The Pact Specification version to use, defaults to
            '2.0.0'.
        :type version: str
        """
        scheme = 'https' if ssl else 'http'
        self.uri = '{scheme}://{host_name}:{port}'.format(
            host_name=host_name, port=port, scheme=scheme)

        self.consumer = consumer
        self.cors = cors
        self.host_name = host_name
        self.log_dir = log_dir or os.getcwd()
        self.pact_dir = pact_dir or os.getcwd()
        self.port = port
        self.provider = provider
        self.ssl = ssl
        self.sslcert = sslcert
        self.sslkey = sslkey
        self.version = version
        self._interactions = []

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
        self._interactions.insert(0, {'provider_state': provider_state})
        return self

    def setup(self):
        """Configure the Mock Service to ready it for a test."""
        try:
            resp = requests.delete(
                self.uri + '/interactions', headers=self.HEADERS)

            assert resp.status_code == 200, resp.content
            resp = requests.put(
                self.uri + '/interactions',
                headers=self.HEADERS,
                json={"interactions": self._interactions})

            assert resp.status_code == 200, resp.content
        except AssertionError:
            raise

    def start_service(self):
        """Start the external Mock Service."""
        command = [
            MOCK_SERVICE_PATH,
            'start',
            '--host={}'.format(self.host_name),
            '--port={}'.format(self.port),
            '--log', '{}/pact-mock-service.log'.format(self.log_dir),
            '--pact-dir', self.pact_dir,
            '--pact-specification-version={}'.format(self.version),
            '--consumer', self.consumer.name,
            '--provider', self.provider.name]

        if self.ssl:
            command.append('--ssl')
        if self.sslcert:
            command.extend(['--sslcert', self.sslcert])
        if self.sslkey:
            command.extend(['--sslkey', self.sslkey])

        process = Popen(command)
        process.communicate()
        if process.returncode != 0:
            raise RuntimeError('The Pact mock service failed to start.')

    def stop_service(self):
        """Stop the external Mock Service."""
        command = [MOCK_SERVICE_PATH, 'stop', '--port={}'.format(self.port)]
        popen = Popen(command)
        popen.communicate()
        if popen.returncode != 0:
            raise RuntimeError(
                'There was an error when stopping the Pact mock service.')

    def upon_receiving(self, scenario):
        """
        Define the name of this contract.

        :param scenario: A unique name for this contract.
        :type scenario: basestring
        :rtype: Pact
        """
        self._interactions[0]['description'] = scenario
        return self

    def verify(self):
        """
        Have the mock service verify all interactions occurred.

        Calls the mock service to verify that all interactions occurred as
        expected, and has it write out the contracts to disk.

        :raises AssertionError: When not all interactions are found.
        """
        self._interactions = []
        resp = requests.get(
            self.uri + '/interactions/verification',
            headers=self.HEADERS)
        assert resp.status_code == 200, resp.content
        payload = {
            'consumer': {'name': self.consumer.name},
            'provider': {'name': self.provider.name},
            'pact_dir': self.pact_dir
        }
        resp = requests.post(
            self.uri + '/pact', headers=self.HEADERS, json=payload)
        assert resp.status_code == 200, resp.content

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
        self._interactions[0]['request'] = Request(
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
        self._interactions[0]['response'] = Response(status,
                                                     headers=headers,
                                                     body=body).json()
        return self

    def __enter__(self):
        """
        Handler for entering a Python context.

        Sets up the mock service to expect the client requests.
        """
        self.setup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Handler for exiting a Python context.

        Calls the mock service to verify that all interactions occurred as
        expected, and has it write out the contracts to disk.
        """
        if (exc_type, exc_val, exc_tb) != (None, None, None):
            return

        self.verify()


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

        if self.body is not None:
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
        if self.body is not None:
            response['body'] = self.body

        if self.headers:
            response['headers'] = self.headers

        return response
