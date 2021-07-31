"""API for creating a contract and configuring the mock service."""
from __future__ import unicode_literals

import json
import os
from subprocess import Popen

from .broker import Broker
from .constants import MESSAGE_PATH
from .matchers import from_term


class MessagePact(Broker):
    """
    Represents a contract between a consumer and provider using messages.

    Provides Python context handler to perform tests on a Python consumer. For example:

    >>> from pact import MessageConsumer, Provider
    >>> pact = MessageConsumer('MyMessageConsumer').has_pact_with(Provider('provider'))
    >>> (pact
    ... .given({"name": "Test provider"}])
    ... .expects_to_receive('Test description')
    ... .with_content({'name': 'John', 'document_name': 'sample_document.doc'})
    ... .with_metadata({'contentType': 'application/json'}))
    >>> with pact:
    ...   handler(event, context)
    """

    MANDATORY_FIELDS = {"providerStates", "description", "contents", "metaData"}

    def __init__(
        self,
        consumer,
        provider,
        publish_to_broker=False,
        broker_base_url=None,
        broker_username=None,
        broker_password=None,
        broker_token=None,
        pact_dir=None,
        version='3.0.0',
        file_write_mode="merge",
    ):
        """
        Create a Pact instance using messages.

        :param consumer: A consumer for this contract that uses messages.
        :type consumer: pact.MessageConsumer
        :param provider: The generic provider for this contract.
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
            broker_base_url, broker_username, broker_password, broker_token
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
        """
        Define metadata attached to the message.

        :param metadata: dictionary of metadata attached to the message.
        :type metadata: dict or None
        :rtype: Pact
        """
        self._insert_message_if_complete()
        self._messages[0]['metaData'] = metadata
        return self

    def with_content(self, contents):
        """
        Define message content (event) that will be use in the message.

        :param contents: dictionary of dictionary used in the message.
        :type metadata: dict
        :rtype: Pact
        """
        self._insert_message_if_complete()
        self._messages[0]['contents'] = from_term(contents)
        return self

    def expects_to_receive(self, description):
        """
        Define the name of this contract (Same as upon_receiving in http pact implementation).

        :param scenario: A unique name for this contract.
        :type scenario: basestring
        :rtype: Pact
        """
        self._insert_message_if_complete()
        self._messages[0]['description'] = description
        return self

    def write_to_pact_file(self):
        """
        Create a pact file based on provided attributes in DSL.

        Return 0 if success, 1 otherwise.

        :rtype: int
        """
        command = [
            MESSAGE_PATH,
            "update",
            json.dumps(self._messages[0]),
            "--pact-dir", self.pact_dir,
            f"--pact-specification-version={self.version}",
            "--consumer", f"{self.consumer.name}",
            "--provider", f"{self.provider.name}",
        ]

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
        elif all(field in self._messages[0] for field in self.MANDATORY_FIELDS):
            self._messages.insert(0, {})

    def __enter__(self):
        """Enter a Python context. This function is required for context manager to work."""
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit a Python context.

        Calls pact-message to write out the contracts to disk.
        """
        if (exc_type, exc_val, exc_tb) != (None, None, None):
            return

        self.write_to_pact_file()

        if self.publish_to_broker:
            self.publish(
                self.consumer.name,
                self.consumer.version,
                pact_dir=self.pact_dir,
                tag_with_git_branch=self.consumer.tag_with_git_branch,
                consumer_tags=self.consumer.tags,
            )
