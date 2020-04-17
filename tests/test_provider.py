from unittest import TestCase

from pact.provider import Provider


class ProviderTestCase(TestCase):
    def test_init(self):
        result = Provider('TestProvider')
        self.assertIsInstance(result, Provider)
        self.assertEqual(result.name, 'TestProvider')
