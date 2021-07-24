"""API for creating a contract and configuring the mock service."""
from __future__ import unicode_literals

import os
import platform
from subprocess import Popen

import psutil
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry

from .broker import Broker
from .constants import MOCK_SERVICE_PATH
from .matchers import from_term


class Pact(Broker):
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

    MANDATORY_FIELDS = {'response', 'description', 'request'}

    def __init__(
        self,
        consumer,
        provider,
        host_name='localhost',
        port=1234,
        log_dir=None,
        ssl=False,
        sslcert=None,
        sslkey=None,
        cors=False,
        publish_to_broker=False,
        broker_base_url=None,
        broker_username=None,
        broker_password=None,
        broker_token=None,
        pact_dir=None,
        specification_version='2.0.0',
        file_write_mode='overwrite',
    ):
        """
        Create a Pact instance.

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
        :param publish_to_broker: Flag to control automatic publishing of
            pacts to a pact broker. Defaults to False.
        :type publish_to_broker: bool
        :param broker_base_url: URL of the pact broker that pacts will be
            published to. Can also be supplied through the PACT_BROKER_BASE_URL
            environment variable. Defaults to None.
        :type broker_base_url: str
        :param broker_username: Username to use when connecting to the pact
            broker if authentication is required. Can also be supplied through
            the PACT_BROKER_USERNAME environment variable. Defaults to None.
        :type broker_username: str
        :param broker_password: Password to use when connecting to the pact
            broker if authentication is required. Strongly recommend supplying
            this value through the PACT_BROKER_PASSWORD environment variable
            instead. Defaults to None.
        :type broker_password: str
        :param broker_token: Authentication token to use when connecting to
            the pact broker. Strongly recommend supplying this value through
            the PACT_BROKER_TOKEN environment variable instead.
            Defaults to None.
        :type broker_token: str
        :param pact_dir: Directory where the resulting pact files will be
            written. Defaults to the current directory.
        :type pact_dir: str
        :param specification_version: The Pact Specification version to use, defaults to
            '2.0.0'.
        :type version: str of the consumer version.
        :param file_write_mode: `overwrite` or `merge`. Use `merge` when
            running multiple mock service instances in parallel for the same
            consumer/provider pair. Ensure the pact file is deleted before
            running tests when using this option so that interactions deleted
            from the code are not maintained in the file. Defaults to
            `overwrite`.
        :type file_write_mode: str
        """
        super().__init__(
            broker_base_url, broker_username, broker_password, broker_token
        )

        scheme = 'https' if ssl else 'http'
        self.uri = '{scheme}://{host_name}:{port}'.format(
            host_name=host_name, port=port, scheme=scheme)
        self.consumer = consumer
        self.cors = cors
        self.file_write_mode = file_write_mode
        self.host_name = host_name
        self.log_dir = log_dir or os.getcwd()
        self.pact_dir = pact_dir or os.getcwd()
        self.port = port
        self.provider = provider
        self.publish_to_broker = publish_to_broker
        self.ssl = ssl
        self.sslcert = sslcert
        self.sslkey = sslkey
        self.specification_version = specification_version
        self._interactions = []
        self._process = None

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
        self._insert_interaction_if_complete()
        self._interactions[0]['provider_state'] = provider_state
        return self

    def setup(self):
        """Configure the Mock Service to ready it for a test."""
        try:
            interactions_uri = f"{self.uri}/interactions"
            resp = requests.delete(
                interactions_uri, headers=self.HEADERS, verify=False
            )

            assert resp.status_code == 200, resp.text
            resp = requests.put(
                interactions_uri,
                headers=self.HEADERS,
                verify=False,
                json={"interactions": self._interactions},
            )

            assert resp.status_code == 200, resp.text
        except AssertionError:
            raise

    def start_service(self):
        """
        Start the external Mock Service.

        :raises RuntimeError: if there is a problem starting the mock service.
        """
        command = [
            MOCK_SERVICE_PATH,
            "service",
            f"--host={self.host_name}",
            f"--port={format(self.port)}",
            "--log", f"{self.log_dir}/pact-mock-service.log",
            "--pact-dir", self.pact_dir,
            "--pact-file-write-mode", self.file_write_mode,
            f"--pact-specification-version={self.specification_version}",
            "--consumer", self.consumer.name,
            "--provider", self.provider.name,
        ]

        if self.ssl:
            command.append('--ssl')
        if self.sslcert:
            command.extend(['--sslcert', self.sslcert])
        if self.sslkey:
            command.extend(['--sslkey', self.sslkey])

        self._process = Popen(command)
        self._wait_for_server_start()

    def stop_service(self):
        """Stop the external Mock Service."""
        is_windows = 'windows' in platform.platform().lower()
        if is_windows:
            # Send the signal to ruby.exe, not the *.bat process
            p = psutil.Process(self._process.pid)
            for child in p.children(recursive=True):
                child.terminate()
            p.wait()
            if psutil.pid_exists(self._process.pid):
                raise RuntimeError(
                    'There was an error when stopping the Pact mock service.')

        else:
            self._process.terminate()

            self._process.communicate()
            if self._process.returncode != 0:
                raise RuntimeError(
                    'There was an error when stopping the Pact mock service.'
                )
        if self.publish_to_broker:
            self.publish(
                self.consumer.name,
                self.consumer.version,
                tag_with_git_branch=self.consumer.tag_with_git_branch,
                consumer_tags=self.consumer.tags,
                pact_dir=self.pact_dir
            )

    def upon_receiving(self, scenario):
        """
        Define the name of this contract.

        :param scenario: A unique name for this contract.
        :type scenario: basestring
        :rtype: Pact
        """
        self._insert_interaction_if_complete()
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
            self.uri + "/interactions/verification", headers=self.HEADERS, verify=False
        )
        assert resp.status_code == 200, resp.text
        resp = requests.post(self.uri + "/pact", headers=self.HEADERS, verify=False)
        assert resp.status_code == 200, resp.text

    def with_request(self, method, path, body=None, headers=None, query=None):
        """
        Define the request that the client is expected to perform.

        :param method: The HTTP method.
        :type method: str
        :param path: The path portion of the URI the client will access.
        :type path: str, Matcher
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
        self._insert_interaction_if_complete()
        self._interactions[0]['request'] = Request(
            method, path, body=body, headers=headers, query=query
        ).json()
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
        self._insert_interaction_if_complete()
        self._interactions[0]['response'] = Response(
            status, headers=headers, body=body
        ).json()
        return self

    def _insert_interaction_if_complete(self):
        """
        Insert a new interaction if current interaction is complete.

        An interaction is complete if it has all the mandatory fields.
        If there are no interactions, a new interaction will be added.

        :rtype: None
        """
        if not self._interactions:
            self._interactions.append({})
        elif all(field in self._interactions[0] for field in self.MANDATORY_FIELDS):
            self._interactions.insert(0, {})

    def _wait_for_server_start(self):
        """
        Wait for the mock service to be ready for requests.

        :rtype: None
        :raises RuntimeError: If there is a problem starting the mock service.
        """
        s = requests.Session()
        retries = Retry(total=9, backoff_factor=0.1)
        http_mount = 'https://' if self.ssl else 'http://'
        s.mount(http_mount, HTTPAdapter(max_retries=retries))

        resp = s.get(self.uri, headers=self.HEADERS, verify=False)
        if resp.status_code != 200:
            self._process.terminate()
            self._process.communicate()
            raise RuntimeError(
                'There was a problem starting the mock service: %s', resp.text
            )

    def __enter__(self):
        """
        Enter a Python context.

        Sets up the mock service to expect the client requests.
        """
        self.setup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit a Python context.

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
        :type path: str, Matcher
        :param body: The contents of the body of the expected request.
        :type body: str, dict, list
        :param headers: The headers of the expected request.
        :type headers: dict
        :param query: The URI query of the expected request.
        :type query: str or dict
        """
        self.method = method
        self.path = from_term(path)
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
