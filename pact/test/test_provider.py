from unittest import TestCase

from .. import Provider


class ProviderTestCase(TestCase):
    def test_init(self):
        result = Provider('TestProvider')
        self.assertIsInstance(result, Provider)
        self.assertEqual(result.name, 'TestProvider')
