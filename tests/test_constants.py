from unittest import TestCase

from mock import patch

from pact import constants as constants


class BrokerClientExeTestCase(TestCase):
    def setUp(self):
        super(BrokerClientExeTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_os = patch.object(constants, 'os', autospec=True).start()

    def test_other(self):
        self.mock_os.name = 'posix'
        self.assertEqual(constants.broker_client_exe(), 'pact-broker')

    def test_windows(self):
        self.mock_os.name = 'nt'
        self.assertEqual(constants.broker_client_exe(), 'pact-broker.bat')


class MockServiceExeTestCase(TestCase):
    def setUp(self):
        super(MockServiceExeTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_os = patch.object(constants, 'os', autospec=True).start()

    def test_other(self):
        self.mock_os.name = 'posix'
        self.assertEqual(constants.mock_service_exe(), 'pact-mock-service')

    def test_windows(self):
        self.mock_os.name = 'nt'
        self.assertEqual(constants.mock_service_exe(), 'pact-mock-service.bat')


class MessageExeTestCase(TestCase):
    def setUp(self):
        super(MessageExeTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_os = patch.object(constants, 'os', autospec=True).start()

    def test_other(self):
        self.mock_os.name = 'posix'
        self.assertEqual(constants.message_exe(), 'pact-message')

    def test_windows(self):
        self.mock_os.name = 'nt'
        self.assertEqual(constants.message_exe(), 'pact-message.bat')


class ProviderVerifierExeTestCase(TestCase):
    def setUp(self):
        super(ProviderVerifierExeTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_os = patch.object(constants, 'os', autospec=True).start()

    def test_other(self):
        self.mock_os.name = 'posix'
        self.assertEqual(
            constants.provider_verifier_exe(), 'pact-provider-verifier')

    def test_windows(self):
        self.mock_os.name = 'nt'
        self.assertEqual(
            constants.provider_verifier_exe(), 'pact-provider-verifier.bat')
