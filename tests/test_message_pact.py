import os
from subprocess import Popen
from unittest import TestCase

from mock import patch, call, Mock
from psutil import Process

from pact.consumer import Consumer, Provider
from pact.matchers import Term
from pact.constants import MOCK_SERVICE_PATH, BROKER_CLIENT_PATH
from pact.message_pact import MessagePact
from pact import pact as pact

class MessagePactTestCase(TestCase):
    def setUp(self):
        self.consumer = Consumer('TestConsumer')
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
        self.assertEqual(target.version, '2.0.0')
        self.assertEqual(len(target._messages), [])

    def test_init_custom_mock_service(self):
        target = MessagePact(
            self.consumer, self.provider, host_name='192.168.1.1', port=8000,
            log_dir='/logs', ssl=True, sslcert='/ssl.cert', sslkey='/ssl.pem',
            cors=True, pact_dir='/pacts', version='3.0.0',
            file_write_mode='merge')

        self.assertIs(target.consumer, self.consumer)
        self.assertIs(target.cors, True)
        self.assertEqual(target.host_name, '192.168.1.1')
        self.assertEqual(target.log_dir, '/logs')
        self.assertEqual(target.pact_dir, '/pacts')
        self.assertEqual(target.port, 8000)
        self.assertIs(target.provider, self.provider)
        self.assertIs(target.ssl, True)
        self.assertEqual(target.sslcert, '/ssl.cert')
        self.assertEqual(target.sslkey, '/ssl.pem')
        self.assertEqual(target.uri, 'https://192.168.1.1:8000')
        self.assertEqual(target.version, '3.0.0')
        self.assertEqual(target.file_write_mode, 'merge')
        self.assertEqual(len(target._interactions), 0)

    def test_init_publish_to_broker(self):
        target = Pact(
            self.consumer, self.provider, publish_to_broker=True,
            broker_base_url='http://localhost', broker_username='username',
            broker_password='password', broker_token='token')

        self.assertEqual(target.broker_base_url, 'http://localhost')
        self.assertEqual(target.broker_username, 'username')
        self.assertEqual(target.broker_password, 'password')
        self.assertEqual(target.broker_token, 'token')
        self.assertIs(target.publish_to_broker, True)

    def test_definition_sparse(self):
        target = Pact(self.consumer, self.provider)
        (target
         .given('I am creating a new pact using the Pact class')
         .upon_receiving('a specific request to the server')
         .with_request('GET', '/path')
         .will_respond_with(200, body='success'))

        self.assertEqual(len(target._interactions), 1)

        self.assertEqual(
            target._interactions[0]['provider_state'],
            'I am creating a new pact using the Pact class')

        self.assertEqual(
            target._interactions[0]['description'],
            'a specific request to the server')

        self.assertEqual(target._interactions[0]['request'],
                         {'path': '/path', 'method': 'GET'})
        self.assertEqual(target._interactions[0]['response'],
                         {'status': 200, 'body': 'success'})



# class MessageConsumer():
#     MANDATORY_FIELDS = {'provider_state', 'description', 'metadata', 'content'}

#     def __init__(self):
#         self._messages = []

#     def _insert_message_if_complete(self):
#         """
#         Insert a new message if current message is complete.
#         An interaction is complete if it has all the mandatory fields.
#         If there are no message, a new message will be added.
#         :rtype: None
#         """
#         if not self._messages:
#             self._messages.append({})
#         elif all(field in self._messages[0]
#                  for field in self.MANDATORY_FIELDS):
#             self._messages.insert(0, {})

#     def given(self, provider_state):
#         self._insert_message_if_complete()
#         self._messages[0]['provider_state'] = provider_state
#         return self

#     def with_metadata(self, metadata):
#         self._insert_message_if_complete()
#         self._messages[0]['metadata'] = metadata
#         return self

#     def with_content(self, content):
#         self._insert_message_if_complete()
#         self._messages[0]['content'] = content
#         return self



#     def expects_to_receive(self, description):
#         self._insert_message_if_complete()
#         self._messages[0]['description'] = description
#         return self 

#     def get_messages(self):
#         print(self._messages)
#         return self._messages

# from unittest import TestCase

# class MessageHandler():
#     def __init__(self, messages):
#         self._messages = messages

#     def generate_contract_file(self):
#         return self._messages

#     def output_stream(self):
#         return "Hello " + self._messages[0]['content']['name']


# class MessageConsumerTestCase(TestCase):
#     def test_pact_with_hash_message(self):
#         # setup expectation
#         consumer = MessageConsumer()
#         consumer \
#             .given('there is an alligator named John') \
#             .expects_to_receive('an alligator message') \
#             .with_content({'name': 'John', 'document_name': 'sample_document.doc'}) \
#             .with_metadata({'contentType': 'application/json', 'source': 'legacy_api'})
                        
#         message_handler = MessageHandler(consumer.get_messages())


#         # expected
#         self.assertEqual(
#             message_handler.output_stream(),
#             "Hello John")


# class MessageProvider(MessageEntityBase):
#     def is_expected_to_send(self, description):
#         self._insert_message_if_complete()
#         self._messages[0]['description'] = description
#         return self
#
#
# class MessageProviderTestCase(TestCase):
#     def test_pact_with_hash_message(self):
#         provider = MessageProvider()
#         provider \
#             .given('there is an alligator named John') \
#             .is_expected_to_send('an alligator message') \
#             .with_content({"name": "John"}) \
#             .with_metadata({'contentType': 'application/json'})
#
#         message_handler = MessageHandler(provider.get_messages())
#
#         # output stream generated to send
#
#         self.assertEqual(
#             message_handler.output_stream(),
#             "Hello John")
