import json


def se(s):
    return b"NULL" if s is None or "" else s.encode("ascii")

def ne():
    return b"NULL"

def check_results(pactlib, mock_server_port, pact_handle, PACT_FILE_DIR, message_pact=None):
    result = pactlib.lib.pactffi_mock_server_matched(mock_server_port)
    print(f"Pact - Got matching client requests: {result}")
    if result is True:
        print(f"Writing pact file to {PACT_FILE_DIR}")
        res_write_pact = pactlib.lib.pactffi_write_pact_file(mock_server_port, PACT_FILE_DIR.encode('ascii'), False)
        print(f"Pact file writing results: {res_write_pact}")
        if message_pact is not None:
            res_write_message_pact = pactlib.lib.pactffi_write_message_pact_file(message_pact, PACT_FILE_DIR.encode('ascii'), False)
            print(f"Pact message file writing results: {res_write_message_pact}")
    else:
        print('pactffi_mock_server_matched did not match')
        mismatches = pactlib.lib.pactffi_mock_server_mismatches(mock_server_port)
        if mismatches:
            result = json.loads(pactlib.ffi.string(mismatches))
            print(json.dumps(result, indent=4))

    # Cleanup
    pactlib.lib.pactffi_cleanup_mock_server(mock_server_port)
    pactlib.lib.pactffi_cleanup_plugins(pact_handle)
