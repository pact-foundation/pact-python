from pact.ffi.ffi_verifier import FFIVerify

def test_version():
    assert FFIVerify().version() == "0.0.0"
