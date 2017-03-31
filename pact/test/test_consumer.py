from unittest import TestCase

from mock import Mock

from .. import Consumer, Provider
from ..pact import Pact


class ConsumerTestCase(TestCase):
    def setUp(self):
        self.mock_service = Mock(Pact)
        self.provider = Mock(Provider)
        self.consumer = Consumer('TestConsumer', service_cls=self.mock_service)

    def test_init(self):
        result = Consumer('TestConsumer')
        self.assertIsInstance(result, Consumer)
        self.assertEqual(result.name, 'TestConsumer')
        self.assertIs(result.service_cls, Pact)

    def test_has_pact_with(self):
        result = self.consumer.has_pact_with(self.provider)
        self.assertIs(result, self.mock_service.return_value)
        self.mock_service.assert_called_once_with(
            consumer=self.consumer, provider=self.provider,
            host_name='localhost', port=1234)

    def test_has_pact_with_customer_host_name_and_port(self):
        result = self.consumer.has_pact_with(
            self.provider, host_name='example.com', port=1111)

        self.assertIs(result, self.mock_service.return_value)
        self.mock_service.assert_called_once_with(
            consumer=self.consumer, provider=self.provider,
            host_name='example.com', port=1111)

    def test_has_pact_with_not_a_provider(self):
        with self.assertRaises(ValueError):
            self.consumer.has_pact_with(None)
