from unittest import TestCase

from mock import Mock

from pact.message_consumer import MessageConsumer
from pact.provider import Provider
from pact.message_pact import MessagePact


class MessageConsumerTestCase(TestCase):
    def setUp(self):
        self.mock_service = Mock(MessagePact)
        self.provider = Mock(Provider)
        self.message_consumer = MessageConsumer('TestMessageConsumer', service_cls=self.mock_service)

    def test_init(self):
        result = MessageConsumer('TestMessageConsumer')
        self.assertIsInstance(result, MessageConsumer)
        self.assertEqual(result.name, 'TestMessageConsumer')
        self.assertIs(result.service_cls, MessagePact)

    def test_has_pact_with(self):
        result = self.message_consumer.has_pact_with(self.provider)
        self.assertIs(result, self.mock_service.return_value)
        self.mock_service.assert_called_once_with(
            consumer=self.message_consumer, provider=self.provider,
            pact_dir=None, version='3.0.0',
            broker_base_url=None, publish_to_broker=False,
            broker_username=None, broker_password=None,
            broker_token=None, file_write_mode='merge')

    def test_has_pact_with_customer_all_options(self):
        result = self.message_consumer.has_pact_with(
            self.provider, pact_dir='/pacts', version='3.0.0',
            file_write_mode='merge')

        self.assertIs(result, self.mock_service.return_value)
        self.mock_service.assert_called_once_with(
            consumer=self.message_consumer, provider=self.provider,
            pact_dir='/pacts', version='3.0.0',
            broker_base_url=None, publish_to_broker=False,
            broker_username=None, broker_password=None, broker_token=None,
            file_write_mode='merge')

    def test_has_pact_with_not_a_provider(self):
        with self.assertRaises(ValueError):
            self.message_consumer.has_pact_with(None)
