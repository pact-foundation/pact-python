from unittest import TestCase

from pact.ffi.verifier import Verifier, VerifyStatus


class VerifierTestCase(TestCase):
    def test_version(self):
        assert Verifier().version() == "0.0.1"

    def test_verify_no_args(self):
        result = Verifier().verify()
        assert result.return_code == VerifyStatus.ERR_NULL_POINTER.value
