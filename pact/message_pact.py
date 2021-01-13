"""API for creating a contract and configuring the mock service."""
from __future__ import unicode_literals

import json
import os
from subprocess import Popen
from .constants import MESSAGE_PATH

class MessagePact():
    """
    Represents a contract between a consumer and provider.

    Provides Python context handlers to configure the Pact mock service to
    perform tests on a Python consumer. For example:

    >>> from pact import Consumer, Provider
    >>> pact = Consumer('MyMessageConsumer').has_pact_with(Provider('provider'))
    >>> (pact
    ... .given('Given')
    ... .expects_to_receive('Expects to Recieve')
    ... .with_content({'name': 'John', 'document_name': 'sample_document.doc'})
    ... .with_metadata({'contentType': 'application/json', 'source': 'legacy_api'}))
    >>> with pact:
    ...   requests.get(pact.uri + '/echo?text=Hello!')

    The GET request is made to the mock service, which will verify that it
    was a GET to /echo with a query string with a key named `text` and its
    value is `Hello!`. If the request does not match an error is raised, if it
    does match the defined interaction, it will respond with the text `Hello!`.
    """

    HEADERS = {'X-Pact-Mock-Service': 'true'}

    MANDATORY_FIELDS = {'provider_state', 'description', 'metadata', 'content'}

    def __init__(self, consumer, provider, log_dir=None,
                 publish_to_broker=False, broker_base_url=None, broker_username=None,
                 broker_password=None, broker_token=None, pact_dir=None, version='3.0.0',
                 file_write_mode='merge'):
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
        self._message_process = None

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

    # def publish(self): # TODO: add pact file generation
    #     """Publish the generated pact files to the specified pact broker."""
    #     if self.broker_base_url is None \
    #             and "PACT_BROKER_BASE_URL" not in os.environ:
    #         raise RuntimeError("No pact broker URL specified. "
    #                            + "Did you expect the PACT_BROKER_BASE_URL "
    #                            + "environment variable to be set?")

    #     pact_files = fnmatch.filter(
    #         os.listdir(self.pact_dir),
    #         self._normalize_consumer_name(self.consumer.name) + '*.json'
    #     )
    #     command = [
    #         BROKER_CLIENT_PATH,
    #         'publish',
    #         '--consumer-app-version={}'.format(self.consumer.version)]

    #     if self.broker_base_url is not None:
    #         command.append('--broker-base-url={}'.format(self.broker_base_url))
    #     if self.broker_username is not None:
    #         command.append('--broker-username={}'.format(self.broker_username))
    #     if self.broker_password is not None:
    #         command.append('--broker-password={}'.format(self.broker_password))
    #     if self.broker_token is not None:
    #         command.append('--broker-token={}'.format(self.broker_token))

    #     command.extend(pact_files)

    #     if self.consumer.tag_with_git_branch:
    #         command.append('--tag-with-git-branch')

    #     if self.consumer.tags is not None:
    #         for tag in self.consumer.tags:
    #             command.extend(['-t', tag])

    #     publish_process = Popen(command)
    #     publish_process.wait()
    #     if publish_process.returncode != 0:
    #         url = self.broker_base_url or os.environ["PACT_BROKER_BASE_URL"]
    #         raise RuntimeError(
    #             "There was an error while publishing to the "
    #             + "pact broker at {}."
    #             .format(url))

    def write_to_pact_file(self):

        # for x in self._message_interactions:
        # temporarily assumed we only have a single message
        command = [
            MESSAGE_PATH,
            'update',
            json.dumps(self._messages[0]),
            '--pact-dir', self.pact_dir,
            '--pact-specification-version={}'.format(self.version),
            '--consumer', self.consumer.name + "_message",
            '--provider', self.provider.name + "_message"]

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

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit a Python context.

        Calls the mock service to verify the message occurred as
        expected, and has it write out the contracts to disk.
        """
        if (exc_type, exc_val, exc_tb) != (None, None, None):
            return

        self.write_to_pact_file()
