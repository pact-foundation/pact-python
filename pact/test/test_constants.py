from unittest import TestCase

from mock import patch

from .. import constants


class broker_client_exeTestCase(TestCase):
    def setUp(self):
        super(broker_client_exeTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_os = patch.object(constants, 'os', autospec=True).start()

    def test_other(self):
        self.mock_os.name = 'posix'
        self.assertEqual(constants.broker_client_exe(), 'pact-broker')

    def test_windows(self):
        self.mock_os.name = 'nt'
        self.assertEqual(constants.broker_client_exe(), 'pact-broker.bat')


class mock_service_exeTestCase(TestCase):
    def setUp(self):
        super(mock_service_exeTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.mock_os = patch.object(constants, 'os', autospec=True).start()

    def test_other(self):
        self.mock_os.name = 'posix'
        self.assertEqual(constants.mock_service_exe(), 'pact-mock-service')

    def test_windows(self):
        self.mock_os.name = 'nt'
        self.assertEqual(constants.mock_service_exe(), 'pact-mock-service.bat')


class provider_verifier_exeTestCase(TestCase):
    def setUp(self):
        super(provider_verifier_exeTestCase, self).setUp()
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
