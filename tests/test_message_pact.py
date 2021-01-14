import os
from subprocess import Popen

from mock import patch, call, Mock
from unittest import TestCase

from pact.message_consumer import MessageConsumer, Provider
from pact.message_pact import MessagePact
from pact.constants import MESSAGE_PATH
from pact import pact as pact

class MessagePactTestCase(TestCase):
    def setUp(self):
        self.consumer = MessageConsumer('TestConsumer')
        self.provider = Provider('TestProvider')

    def test_init_defaults(self):
        target = MessagePact(self.consumer, self.provider)
        self.assertIs(target.broker_base_url, None)
        self.assertIs(target.broker_username, None)
        self.assertIs(target.broker_password, None)
        self.assertIs(target.consumer, self.consumer)
        self.assertEqual(target.log_dir, os.getcwd())
        self.assertEqual(target.pact_dir, os.getcwd())
        self.assertIs(target.provider, self.provider)
        self.assertIs(target.publish_to_broker, False)
        self.assertEqual(target.version, '3.0.0')
        self.assertEqual(len(target._messages), 0)

    def test_init_custom_mock_service(self):
        target = MessagePact(
            self.consumer, self.provider, log_dir='/logs', pact_dir='/pacts',
            version='3.0.0', file_write_mode='merge')

        self.assertIs(target.consumer, self.consumer)
        self.assertEqual(target.log_dir, '/logs')
        self.assertEqual(target.pact_dir, '/pacts')
        self.assertIs(target.provider, self.provider)
        self.assertEqual(target.version, '3.0.0')
        self.assertEqual(target.file_write_mode, 'merge')
        self.assertEqual(len(target._messages), 0)

    def test_init_publish_to_broker(self):
        target = MessagePact(
            self.consumer, self.provider, publish_to_broker=True,
            broker_base_url='http://localhost', broker_username='username',
            broker_password='password', broker_token='token')

        self.assertEqual(target.broker_base_url, 'http://localhost')
        self.assertEqual(target.broker_username, 'username')
        self.assertEqual(target.broker_password, 'password')
        self.assertEqual(target.broker_token, 'token')
        self.assertIs(target.publish_to_broker, True)

    def test_definition_sparse(self):
        target = MessagePact(self.consumer, self.provider)
        (
            target
            .given('there is an alligator named John')
            .expects_to_receive('an alligator message')
            .with_content({'name': 'John', 'document_name': 'sample_document.doc'})
            .with_metadata({'contentType': 'application/json', 'source': 'legacy_api'})
        )

        self.assertEqual(len(target._messages), 1)

        self.assertEqual(
            target._messages[0]['providerStates'],
            [{'name':'there is an alligator named John'}])

        self.assertEqual(
            target._messages[0]['description'],
            'an alligator message')

        self.assertEqual(
            target._messages[0]['contents'],
            {'name': 'John', 'document_name': 'sample_document.doc'})

        self.assertEqual(
            target._messages[0]['metaData'],
            {'contentType': 'application/json', 'source': 'legacy_api'})

    def test_definition_without_given(self):
        target = MessagePact(self.consumer, self.provider)
        (
            target
            .expects_to_receive('an crocodile message')
            .with_content({'name': 'Mary'})
            .with_metadata({'source': 'legacy_api'})
        )

        self.assertEqual(len(target._messages), 1)

        self.assertIsNone(target._messages[0].get('providerStates'))

        self.assertEqual(
            target._messages[0]['description'],
            'an crocodile message')

        self.assertEqual(
            target._messages[0]['contents'],
            {'name': 'Mary'})

        self.assertEqual(
            target._messages[0]['metaData'],
            {'source': 'legacy_api'})


class PactGeneratePactFileTestCase(MessagePactTestCase):
    def setUp(self):
        super(PactGeneratePactFileTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_Popen = patch.object(pact, 'Popen', autospec=True).start()
        self.mock_Popen.return_value.returncode = 0


    def test_call_pact_message_to_generate_pact_file(self):
        # self.addCleanup(patch.stopall)
        # self.mock_Popen = patch.object(pact, 'Popen', autospec=True).start()
        # self.mock_Popen.return_value.returncode = 0
        # mock_Popen.return_value = 0
        # consumer = MessageConsumer('TestConsumer')
        # provider = Provider('TestProvider')

        target = MessagePact(
            self.consumer, self.provider, log_dir='/logs', pact_dir='/pacts',
            version='3.0.0', file_write_mode='merge')

        (target
            .given('There is an alligator named John')
            .expects_to_receive('an alligator message')
            .with_content({
                'name': 'John', 
                'document_name': 'sample_document.doc'
            }).with_metadata({
                'contentType': 'application/json',
                'source': 'legacy_api'}))

        target.write_to_pact_file()

        self.mock_Popen.assert_called_once_with([
            MESSAGE_PATH, 'update',
            '--consumer', 'TestConsumer_message',
            '--provider', 'TestProvider_message',
            '--consumer-app-version=3.0.0',
            '--pact-dir', '/pacts'
            ])
