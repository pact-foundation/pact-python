from pact.ffi.verifier import Verifier, VerifyStatus


def test_version():
    verifier = Verifier()
    assert verifier.version() == "0.0.1"


def test_verify_no_args():
    result = Verifier().verify(args=None)
    assert VerifyStatus(result.return_code) == VerifyStatus.NULL_POINTER


def test_verify_invalid_args():
    verifier = Verifier()
    result = verifier.verify(args="Your argument is invalid")
    assert VerifyStatus(result.return_code) == VerifyStatus.INVALID_ARGS
    assert 'UnknownArgument' in '\n'.join(result.logs)
    assert len(result.logs) == 2


def test_verify_invalid_args2():
    result = Verifier().verify(args="Your argument is still invalid")
    assert VerifyStatus(result.return_code) == VerifyStatus.INVALID_ARGS
    assert 'UnknownArgument' in '\n'.join(result.logs)
    assert len(result.logs) == 2
