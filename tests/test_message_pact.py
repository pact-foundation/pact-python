import os
import json

from mock import patch
from unittest import TestCase

from pact.message_consumer import MessageConsumer, Provider
from pact.message_pact import MessagePact
from pact.constants import MESSAGE_PATH
from pact import message_pact as message_pact
from pact import Term

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
        self.assertEqual(target.pact_dir, os.getcwd())
        self.assertIs(target.provider, self.provider)
        self.assertIs(target.publish_to_broker, False)
        self.assertEqual(target.version, '3.0.0')
        self.assertEqual(len(target._messages), 0)

    def test_init_custom_mock_service(self):
        target = MessagePact(
            self.consumer, self.provider, pact_dir='/pacts',
            version='3.0.0', file_write_mode='merge')

        self.assertIs(target.consumer, self.consumer)
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
            .with_metadata({'contentType': 'application/json',
                            'source': 'legacy_api',
                            'some-header': Term('\\d+-\\d+-\\d+T\\d+:\\d+:\\d+', '2022-02-15T20:16:01')})
        )

        self.assertEqual(len(target._messages), 1)

        self.assertEqual(
            target._messages[0]['providerStates'],
            [{'name': 'there is an alligator named John'}])

        self.assertEqual(
            target._messages[0]['description'],
            'an alligator message')

        self.assertEqual(
            target._messages[0]['contents'],
            {'name': 'John', 'document_name': 'sample_document.doc'})

        self.assertTrue({'contentType': 'application/json', 'source': 'legacy_api'}.items()
                        <= target._messages[0]['metaData'].items())

        self.assertTrue(target._messages[0]['metaData']['some-header'], 'Pact::Term')

    def test_definition_multiple_provider_states(self):
        target = MessagePact(self.consumer, self.provider)
        (
            target
            .given('there is an alligator named John',
                   params={'color': 'green', 'weight_kg': 130, 'length_m': 1.95})
            .given('there is an spider named Jack',
                   params={'color': 'mostly black', 'weight_kg': 0.009, 'length_m': 0.05})
            .expects_to_receive('an alligator message')
            .with_content({'name': 'John', 'document_name': 'sample_document.doc'})
            .with_metadata({'contentType': 'application/json',
                            'source': 'legacy_api',
                            'some-header': Term('\\d+-\\d+-\\d+T\\d+:\\d+:\\d+', '2022-02-15T20:16:01')})
        )

        self.assertEqual(len(target._messages), 1)

        self.assertEqual(
            target._messages[0]['providerStates'],
            [
                {
                    'name': 'there is an alligator named John',
                    'params': {
                        'color': 'green',
                        'weight_kg': 130,
                        'length_m': 1.95
                    }
                },
                {
                    'name': 'there is an spider named Jack',
                    'params': {
                        'color': 'mostly black',
                        'weight_kg': 0.009,
                        'length_m': 0.05
                    }
                }
            ]
        )

        self.assertEqual(
            target._messages[0]['description'],
            'an alligator message')

        self.assertEqual(
            target._messages[0]['contents'],
            {'name': 'John', 'document_name': 'sample_document.doc'})

        self.assertTrue({'contentType': 'application/json', 'source': 'legacy_api'}.items()
                        <= target._messages[0]['metaData'].items())

        self.assertTrue(target._messages[0]['metaData']['some-header'], 'Pact::Term')

    def test_insert_new_message_once_required_attributes_provided(self):
        target = MessagePact(self.consumer, self.provider)
        (
            target
            .given('there is an alligator named John')
            .with_content({'name': 'John', 'document_name': 'sample_document.doc'})
            .with_metadata({'contentType': 'application/json'})
        )
        self.assertEqual(len(target._messages), 1)

        (
            target.expects_to_receive('an alligator message')
        )
        self.assertEqual(len(target._messages), 1)
        self.assertEqual(target._messages[0]['description'], 'an alligator message')

        (
            target.expects_to_receive('a new message description')
        )
        self.assertEqual(len(target._messages), 2)
        self.assertEqual(target._messages[0]['description'], 'a new message description')

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


class MessagePactContextManagerTestCase(MessagePactTestCase):
    def setUp(self):
        super(MessagePactContextManagerTestCase, self).setUp()
        self.addCleanup(patch.stopall)

        self.write_to_pact_file = patch.object(
            message_pact.MessagePact, 'write_to_pact_file', autospec=True).start()
        self.write_to_pact_file.return_value.returncode = 0

        self.mock_publish = patch.object(
            message_pact.MessagePact, 'publish', autospec=True).start()
        self.mock_publish.return_value.returncode = 0

    def test_successful(self):
        pact = MessagePact(
            self.consumer, self.provider, publish_to_broker=True,
            broker_base_url='http://localhost', broker_username='username', broker_password='password',
            pact_dir='some_dir')

        with pact:
            pass

        self.write_to_pact_file.assert_called_once()
        self.mock_publish.assert_called_once_with(
            pact,
            'TestConsumer',
            '0.0.0',
            auto_detect_version_properties=False,
            branch=None,
            build_url=None,
            consumer_tags=None,
            pact_dir='some_dir',
            tag_with_git_branch=False
        )

    def test_context_raises_error(self):
        pact = MessagePact(
            self.consumer, self.provider, publish_to_broker=True,
            broker_base_url='http://localhost', broker_username='username', broker_password='password')

        with self.assertRaises(RuntimeError):
            with pact:
                raise RuntimeError

        self.write_to_pact_file.assert_not_called()
        self.mock_publish.assert_not_called()


class PactGeneratePactFileTestCase(TestCase):
    def setUp(self):
        super(PactGeneratePactFileTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_Popen = patch.object(message_pact, 'Popen', autospec=True).start()
        self.mock_Popen.return_value.returncode = 0

        self.consumer = MessageConsumer('TestConsumer')
        self.provider = Provider('TestProvider')

    def test_call_pact_message_to_generate_pact_file(self):
        target = MessagePact(
            self.consumer, self.provider, pact_dir='/pacts',
            version='3.0.0', file_write_mode='merge', publish_to_broker=True)

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
            json.dumps(target._messages[0]),
            '--pact-dir', '/pacts',
            '--pact-specification-version=3.0.0',
            '--consumer', 'TestConsumer',
            '--provider', 'TestProvider',
        ])
