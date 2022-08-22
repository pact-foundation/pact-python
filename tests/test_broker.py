import os
from unittest import TestCase

from mock import patch

from pact.broker import Broker
from pact.consumer import Consumer, Provider
from pact.constants import BROKER_CLIENT_PATH
from pact import broker as broker


class BrokerTestCase(TestCase):

    def setUp(self):
        self.consumer = Consumer('TestConsumer')
        self.provider = Provider('TestProvider')
        self.addCleanup(patch.stopall)
        self.mock_Popen = patch.object(broker, 'Popen', autospec=True).start()
        self.mock_Popen.return_value.returncode = 0
        self.mock_fnmatch = patch.object(
            broker.fnmatch, 'filter', autospec=True).start()
        self.mock_fnmatch.return_value = ['TestConsumer-TestProvider.json']

    def test_publish_without_broker_url(self):
        broker = Broker()

        with self.assertRaises(RuntimeError):
            broker.publish("TestConsumer", "2.0.1")

        self.mock_Popen.assert_not_called()

    def test_publish_fails(self):
        self.mock_Popen.return_value.returncode = 1
        broker = Broker(broker_base_url="http://localhost",
                        broker_username="username",
                        broker_password="password",
                        broker_token="token")

        with self.assertRaises(RuntimeError):
            broker.publish("TestConsumer",
                           "2.0.1",
                           pact_dir='.')

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=2.0.1',
            '--broker-base-url=http://localhost',
            '--broker-username=username',
            '--broker-password=password',
            '--broker-token=token',
            './TestConsumer-TestProvider.json'])

    def test_publish_with_broker_url_environment_variable(self):
        BROKER_URL_ENV = 'http://broker.url'
        os.environ["PACT_BROKER_BASE_URL"] = BROKER_URL_ENV

        broker = Broker(broker_username="username",
                        broker_password="password")

        broker.publish("TestConsumer",
                       "2.0.1",
                       pact_dir='.')

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=2.0.1',
            f"--broker-base-url={BROKER_URL_ENV}",
            '--broker-username=username',
            '--broker-password=password',
            './TestConsumer-TestProvider.json'])

        del os.environ["PACT_BROKER_BASE_URL"]

    def test_basic_authenticated_publish(self):
        broker = Broker(broker_base_url="http://localhost",
                        broker_username="username",
                        broker_password="password")

        broker.publish("TestConsumer",
                       "2.0.1",
                       pact_dir='.')

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=2.0.1',
            '--broker-base-url=http://localhost',
            '--broker-username=username',
            '--broker-password=password',
            './TestConsumer-TestProvider.json'])

    def test_token_authenticated_publish(self):
        broker = Broker(broker_base_url="http://localhost",
                        broker_username="username",
                        broker_password="password",
                        broker_token="token")

        broker.publish("TestConsumer",
                       "2.0.1",
                       pact_dir='.')

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=2.0.1',
            '--broker-base-url=http://localhost',
            '--broker-username=username',
            '--broker-password=password',
            '--broker-token=token',
            './TestConsumer-TestProvider.json'])

    def test_git_tagged_publish(self):
        broker = Broker(broker_base_url="http://localhost")

        broker.publish("TestConsumer",
                       "2.0.1",
                       tag_with_git_branch=True,
                       pact_dir='.')

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=2.0.1',
            '--broker-base-url=http://localhost',
            './TestConsumer-TestProvider.json',
            '--tag-with-git-branch'])

    def test_manual_tagged_publish(self):
        broker = Broker(broker_base_url="http://localhost")

        broker.publish("TestConsumer",
                       "2.0.1",
                       consumer_tags=['tag1', 'tag2'],
                       pact_dir='.')

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=2.0.1',
            '--broker-base-url=http://localhost',
            './TestConsumer-TestProvider.json',
            '-t', 'tag1',
            '-t', 'tag2'])

    def test_branch_publish(self):
        broker = Broker(broker_base_url="http://localhost")

        broker.publish("TestConsumer",
                       "2.0.1",
                       branch='consumer-branch',
                       pact_dir='.')

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=2.0.1',
            '--broker-base-url=http://localhost',
            './TestConsumer-TestProvider.json',
            '--branch=consumer-branch'])

    def test_build_url_publish(self):
        broker = Broker(broker_base_url="http://localhost")

        broker.publish("TestConsumer",
                       "2.0.1",
                       build_url='http://ci',
                       pact_dir='.')

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=2.0.1',
            '--broker-base-url=http://localhost',
            './TestConsumer-TestProvider.json',
            '--build-url=http://ci'])

    def test_auto_detect_version_properties_publish(self):
        broker = Broker(broker_base_url="http://localhost")

        broker.publish("TestConsumer",
                       "2.0.1",
                       auto_detect_version_properties=True,
                       pact_dir='.')

        self.mock_Popen.assert_called_once_with([
            BROKER_CLIENT_PATH, 'publish',
            '--consumer-app-version=2.0.1',
            '--broker-base-url=http://localhost',
            './TestConsumer-TestProvider.json',
            '--auto-detect-version-properties'])
