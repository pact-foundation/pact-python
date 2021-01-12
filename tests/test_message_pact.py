"""pact test for user message consumer"""

import logging
import os
import atexit

import pytest
from pact import Consumer, Like, Provider, Term, Format


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
print(Format().__dict__)

PACT_BROKER_URL = "http://localhost"
PACT_FILE = "userserviceclient-userservice.json"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"

PACT_MOCK_HOST = 'localhost'
PACT_MOCK_PORT = 1234
PACT_DIR = os.path.dirname(os.path.realpath(__file__))

@pytest.fixture
def consumer():
    return UserConsumer(
        'http://{host}:{port}'
        .format(host=PACT_MOCK_HOST, port=PACT_MOCK_PORT)
    )

@pytest.fixture(scope='session')
def pact(request):
    version = request.config.getoption('--publish-pact')
    publish = True if version else False

    pact = Consumer('UserServiceClient', version=version).has_pact_with(
        Provider('UserService'), host_name=PACT_MOCK_HOST, port=PACT_MOCK_PORT,
        pact_dir=PACT_DIR, publish_to_broker=publish, broker_base_url=PACT_BROKER_URL,
        broker_username=PACT_BROKER_USERNAME, broker_password=PACT_BROKER_PASSWORD)

    print('start service')
    pact.start_service()
    atexit.register(pact.stop_service)

    yield pact
    print('stop service')
    pact.stop_service()

def test_pact_with_hash_message(pact, consumer):
    expected = {
        'name': 'UserA',
        'id': Format().uuid,
        'created_on': Term(
            r'\d+-\d+-\d+T\d+:\d+:\d+',
            '2016-12-15T20:16:01'
        ),
        'ip_address': Format().ip_address,
        'admin': False
    }

    (pact
     .given('UserA exists and is not an administrator')
     .upon_receiving('a request for UserA')
     .with_request('get', '/users/UserA')
     .will_respond_with(200, body=Like(expected)))

    with pact:
        user = consumer.get_user('UserA')
        assert user.name == 'UserA'


# class MessageConsumer():
#     MANDATORY_FIELDS = {'provider_state', 'metadata', 'content'}

#     def __init__(self):
#         self._messages = []

#     def _insert_message_if_complete(self):
#         """
#         Insert a new message if current message is complete.
#         An interaction is complete if it has all the mandatory fields.
#         If there are no interactions, a new interaction will be added.
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

#     def get_messages(self):
#         print(self._messages)
#         return self._messages

#     def expects_to_receive(self, description):
#         self._insert_message_if_complete()
#         self._messages[0]['description'] = description
#         return self 


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
