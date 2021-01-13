"""API for creating a contract and configuring the mock service."""
from __future__ import unicode_literals

import fnmatch
import os
import platform
from subprocess import Popen

import psutil
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry

from .constants import BROKER_CLIENT_PATH
from .constants import MOCK_SERVICE_PATH
from .matchers import from_term


class MessagePact():
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

    HEADERS = {'X-Pact-Mock-Service': 'true'} ##

    MANDATORY_FIELDS = {'provider_state', 'description', 'metadata', 'content'}

    def __init__(self, consumer, provider, log_dir=None,
                    publish_to_broker=False, broker_base_url=None,
                    broker_username=None, broker_password=None, broker_token=None,
                    pact_dir=None, version='3.0.0', file_write_mode='overwrite'):
        """
        Create a Pact instance.

        :param consumer: The consumer for this contract.
        :type consumer: pact.Consumer
        :param provider: The provider for this contract.
        :type provider: pact.Provider
        :param log_dir: The directory where logs should be written. Defaults to
            the current directory.
        :type log_dir: str
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
        :param version: The Pact Specification version to use, defaults to
            '3.0.0'.
        :type version: str
        :param file_write_mode: `overwrite` or `merge`. Use `merge` when
            running multiple mock service instances in parallel for the same
            consumer/provider pair. Ensure the pact file is deleted before
            running tests when using this option so that interactions deleted
            from the code are not maintained in the file. Defaults to
            `overwrite`.
        :type file_write_mode: str
        """

        self.broker_base_url = broker_base_url
        self.broker_username = broker_username
        self.broker_password = broker_password
        self.broker_token = broker_token
        self.consumer = consumer
        self.file_write_mode = file_write_mode
        self.log_dir = log_dir or os.getcwd()
        self.pact_dir = pact_dir or os.getcwd()
        self.provider = provider
        self.publish_to_broker = publish_to_broker
        self.version = version
        self._process = None
        self._messages = []

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
        self._insert_message_if_complete()
        self._messages[0]['provider_state'] = provider_state
        return self

    def with_metadata(self, metadata):
        self._insert_message_if_complete()
        self._messages[0]['metadata'] = metadata
        return self

    def with_content(self, content):
        self._insert_message_if_complete()
        self._messages[0]['content'] = content
        return self



    def expects_to_receive(self, description):
        self._insert_message_if_complete()
        self._messages[0]['description'] = description
        return self 


    @staticmethod
    def _normalize_consumer_name(name):
        return name.lower().replace(' ', '_')

    def publish(self): # TODO: common
        """Publish the generated pact files to the specified pact broker."""
        if self.broker_base_url is None \
                and "PACT_BROKER_BASE_URL" not in os.environ:
            raise RuntimeError("No pact broker URL specified. "
                               + "Did you expect the PACT_BROKER_BASE_URL "
                               + "environment variable to be set?")

        pact_files = fnmatch.filter(
            os.listdir(self.pact_dir),
            self._normalize_consumer_name(self.consumer.name) + '*.json'
        )
        command = [
            BROKER_CLIENT_PATH,
            'publish',
            '--consumer-app-version={}'.format(self.consumer.version)]

        if self.broker_base_url is not None:
            command.append('--broker-base-url={}'.format(self.broker_base_url))
        if self.broker_username is not None:
            command.append('--broker-username={}'.format(self.broker_username))
        if self.broker_password is not None:
            command.append('--broker-password={}'.format(self.broker_password))
        if self.broker_token is not None:
            command.append('--broker-token={}'.format(self.broker_token))

        command.extend(pact_files)

        if self.consumer.tag_with_git_branch:
            command.append('--tag-with-git-branch')

        if self.consumer.tags is not None:
            for tag in self.consumer.tags:
                command.extend(['-t', tag])

        publish_process = Popen(command)
        publish_process.wait()
        if publish_process.returncode != 0:
            url = self.broker_base_url or os.environ["PACT_BROKER_BASE_URL"]
            raise RuntimeError(
                "There was an error while publishing to the "
                + "pact broker at {}."
                .format(url))

    # def setup(self):
    #     pass
        # """Configure the Mock Service to ready it for a test."""
        # try:
        #     resp = requests.delete(
        #         self.uri + '/interactions', headers=self.HEADERS, verify=False)

        #     assert resp.status_code == 200, resp.text
        #     resp = requests.put(
        #         self.uri + '/interactions',
        #         headers=self.HEADERS,
        #         verify=False,
        #         json={"interactions": self._interactions})

        #     assert resp.status_code == 200, resp.text
        # except AssertionError:
        #     raise

    def start_service(self):
        """
        Start the external Mock Service.

        :raises RuntimeError: if there is a problem starting the mock service.
        """
        command = [
            MOCK_SERVICE_PATH,
            'service',
            '--host={}'.format(self.host_name),
            '--port={}'.format(self.port),
            '--log', '{}/pact-mock-service.log'.format(self.log_dir),
            '--pact-dir', self.pact_dir,
            '--pact-file-write-mode', self.file_write_mode,
            '--pact-specification-version={}'.format(self.version),
            '--consumer', self.consumer.name,
            '--provider', self.provider.name]

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
                    'There was an error when stopping the Pact mock service.')
        if (self.publish_to_broker):
            self.publish()

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

    def verify(self): # TODO: common
        """
        Have the mock service verify all interactions occurred.

        Calls the mock service to verify that all interactions occurred as
        expected, and has it write out the contracts to disk.

        :raises AssertionError: When not all interactions are found.
        """
        pass
        # self._interactions = []
        # resp = requests.get(
        #     self.uri + '/interactions/verification',
        #     headers=self.HEADERS, verify=False)
        # assert resp.status_code == 200, resp.text
        # resp = requests.post(
        #     self.uri + '/pact', headers=self.HEADERS, verify=False)
        # assert resp.status_code == 200, resp.text


    def write_to_pact_file(self):

        for x in self._message_interactions:
            command = [
                MESSAGE_PATH,
                'update',
                json.dumps(x._messages[0]),
                '--pact-dir', self.pact_dir,
                '--pact-specification-version={}'.format(self.version),
                '--consumer', self.consumer.name + "_message",
                '--provider', self.provider.name + "_message"]

            print("********* command: {}".format(command))

            self._message_process = Popen(command)

    def _insert_message_if_complete(self):
        """
        Insert a new message if current message is complete.
        An interaction is complete if it has all the mandatory fields.
        If there are no message, a new message will be added.
        :rtype: None
        """
        if not self._messages:
            self._messages.append({})
        elif all(field in self._messages[0]
                 for field in self.MANDATORY_FIELDS):
            self._messages.insert(0, {})


    # def __enter__(self):
    #     """
    #     Enter a Python context.

    #     Sets up the mock service to expect the client requests.
    #     """
    #     self.setup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit a Python context.

        Calls the mock service to verify that all interactions occurred as
        expected, and has it write out the contracts to disk.
        """
        if (exc_type, exc_val, exc_tb) != (None, None, None):
            return

        self.write_to_pact_file()


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
