"""API for creating a contract and configuring the mock service."""
from __future__ import unicode_literals

import json
import os
from subprocess import Popen

from .broker import Broker
from .constants import MESSAGE_PATH

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MessagePact(Broker):
    """
    Represents a contract between a consumer and provider using messages.

    Provides Python context handlers to configure the Pact mock service to
    perform tests on a Python consumer. For example:

    >>> from pact import Consumer, Provider
    >>> pact = MessageConsumer('MyMessageConsumer').has_pact_with(Provider('provider'))
    >>> (pact
    ... .given({"name": "Test provider"}])
    ... .expects_to_receive('Test description')
    ... .with_content({'name': 'John', 'document_name': 'sample_document.doc'})
    ... .with_metadata({'contentType': 'application/json'}))
    >>> with pact:
    ... log.info("In Python context")
    """

    MANDATORY_FIELDS = {'providerStates', 'description', 'contents', 'metaData'}

    def __init__(self, consumer, provider,
                 publish_to_broker=False, broker_base_url=None, broker_username=None,
                 broker_password=None, broker_token=None, pact_dir=None, version='3.0.0',
                 file_write_mode='merge'):
        """
        Create a Pact instance using messages.
        :param consumer: A consumer for this contract that uses messages.
        :type consumer: pact.Consumer
        :param provider: The provider for this contract.
        :type provider: pact.Provider
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
            `merge`.
        :type file_write_mode: str
        """
        super().__init__(
            broker_base_url,
            broker_username,
            broker_password,
            broker_token
        )

        self.consumer = consumer
        self.file_write_mode = file_write_mode
        self.pact_dir = pact_dir or os.getcwd()
        self.provider = provider
        self.publish_to_broker = publish_to_broker
        self.version = version
        self._process = None
        self._messages = []
        self._message_process = None

    def given(self, provider_states):
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

        state = [{"name": "{}".format(provider_states)}]
        self._messages[0]['providerStates'] = state
        return self

    def with_metadata(self, metadata):
        self._insert_message_if_complete()
        self._messages[0]['metaData'] = metadata
        return self

    def with_content(self, contents):
        self._insert_message_if_complete()
        self._messages[0]['contents'] = contents
        return self

    def expects_to_receive(self, description):
        self._insert_message_if_complete()
        self._messages[0]['description'] = description
        return self

    def send_message(self):
        return self._messages

    @staticmethod
    def _normalize_consumer_name(name):
        return name.lower().replace(' ', '_')

    def write_to_pact_file(self):
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

    def __enter__(self):
        """
        Enter a Python context.

        Sets up the mock service to expect the client requests.
        """
        log.info("__enter__ context")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit a Python context.

        Calls the mock service to verify the message occurred as
        expected, and has it write out the contracts to disk.
        """
        if (exc_type, exc_val, exc_tb) != (None, None, None):
            return

        self.write_to_pact_file()

        if (self.publish_to_broker):
            self.publish(self.consumer.name, self.consumer.version,
                        tag_with_git_branch=self.consumer.tag_with_git_branch,
                        consumer_tags=self.consumer.tags)
