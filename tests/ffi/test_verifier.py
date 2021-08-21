from unittest import TestCase

from pact.ffi.verifier import Verifier, VerifyStatus


class VerifierTestCase(TestCase):
    def test_version(self):
        assert Verifier().version() == "0.0.1"

    def test_verify_no_args(self):
        result = Verifier().verify(args=None)
        self.assertEqual(VerifyStatus(result.return_code), VerifyStatus.NULL_POINTER)

    def test_verify_invalid_args(self):
        result = Verifier().verify(args="Your argument is invalid")
        assert VerifyStatus(result.return_code) == VerifyStatus.INVALID_ARGS
        self.assertIn('UnknownArgument', '\n'.join(result.logs))
