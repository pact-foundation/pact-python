from unittest import TestCase

from mock import Mock

from pact.consumer import Consumer
from pact.provider import Provider
from pact.pact import Pact


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
            host_name='localhost', port=1234,
            log_dir=None, ssl=False, sslcert=None, sslkey=None,
            cors=False, pact_dir=None, specification_version='2.0.0',
            broker_base_url=None, publish_to_broker=False,
            broker_username=None, broker_password=None,
            broker_token=None, file_write_mode='overwrite')

    def test_has_pact_with_customer_all_options(self):
        result = self.consumer.has_pact_with(
            self.provider, host_name='example.com', port=1111,
            log_dir='/logs', ssl=True, sslcert='/ssl.cert', sslkey='ssl.pem',
            cors=True, pact_dir='/pacts', specification_version='3.0.0',
            file_write_mode='merge')

        self.assertIs(result, self.mock_service.return_value)
        self.mock_service.assert_called_once_with(
            consumer=self.consumer, provider=self.provider,
            host_name='example.com', port=1111,
            log_dir='/logs', ssl=True, sslcert='/ssl.cert', sslkey='ssl.pem',
            cors=True, pact_dir='/pacts', specification_version='3.0.0',
            broker_base_url=None, publish_to_broker=False,
            broker_username=None, broker_password=None, broker_token=None,
            file_write_mode='merge')

    def test_has_pact_with_not_a_provider(self):
        with self.assertRaises(ValueError):
            self.consumer.has_pact_with(None)
