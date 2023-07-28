from pact.__version__ import __version__
from pact.ffi.pact_ffi import PactFFI
from pact.ffi.utils import se, ne
import json
pactlib = PactFFI()

def new_pact(consumer:str,provider: str):
    pact_handle = pactlib.lib.pactffi_new_pact(se(consumer), se(provider))
    pactlib.lib.pactffi_with_pact_metadata(pact_handle, b'pact-python', b'version', se(__version__))
    return pact_handle

def with_specification(pact_handle, specification=int):
    return pactlib.lib.pactffi_with_specification(pact_handle, specification)

def using_plugin(pact_handle, name=str, version=str):
    return pactlib.lib.pactffi_using_plugin(pact_handle, se(name), se(version))

def new_interaction(pact_handle,description=str):
    return pactlib.lib.pactffi_new_interaction(pact_handle, se(description))

def new_message(pact_handle, description=str):
    return pactlib.lib.pactffi_new_message(pact_handle, se(description))

def upon_receiving(interaction_handle, description=str):
    return pactlib.lib.pactffi_upon_receiving(interaction_handle, se(description))

def given(interaction_handle, description=str):
    return pactlib.lib.pactffi_given(interaction_handle, se(description))

def with_request(interaction_handle, method=str, path=str):
    return pactlib.lib.pactffi_with_request(interaction_handle, se(method), se(path))

def with_header(interaction_handle, req_or_res="res" or "req", name=str, index=int, value=str):
    return pactlib.lib.pactffi_with_header_v2(interaction_handle, 0 if req_or_res == 'req' else 1, se(name), index, se(value))
    
def with_request_header(interaction_handle, name=str, index=int, value=str):
    return with_header(interaction_handle, "req", name, index, value)
    
def with_response_header(interaction_handle, name=str, index=int, value=str):
    return with_header(interaction_handle, "res", name, index, value)
    
def with_body(interaction_handle, req_or_res="res" or "req", content_type=str, body=str):
    if 'json' in content_type:
        encoded_body = se(json.dumps(body))
    else:
        encoded_body = se(body)
    return pactlib.lib.pactffi_with_body(interaction_handle, 0 if req_or_res == 'req' else 1, se(content_type), encoded_body)

def with_request_body(interaction_handle, content_type=str, body=str):
    return with_body(interaction_handle, "req", content_type, body)

def with_response_body(interaction_handle, content_type=str, body=str):
    return with_body(interaction_handle, "res", content_type, body)

def response_status(interaction_handle, code=int):
    return pactlib.lib.pactffi_response_status(interaction_handle, code)

def message_expects_to_receive(message_handle,description=str):
    pactlib.lib.pactffi_message_expects_to_receive(message_handle, se(description))

def message_given(message_handle, description=str):
    pactlib.lib.pactffi_message_given(message_handle, se(description))

def message_with_contents(message_handle, content_type=str, body=str):
    if 'json' in content_type:
        length = len(json.dumps(body))
        size = length + 1
        encoded_body = pactlib.ffi.new("char[]", se(json.dumps(body)))
    else:
        length = len(body)
        size = length + 1
        encoded_body = pactlib.ffi.new("char[]", se(body))
    return pactlib.lib.pactffi_message_with_contents(message_handle, se(content_type), encoded_body, size)

def start_mock_server(pact_handle,hostname=str, port=int,transport=str, transport_config=str or None):
    # Start mock server
    mock_server_port = pactlib.lib.pactffi_create_mock_server_for_transport(pact_handle, se(hostname), port, se(transport), pactlib.ffi.cast("void *", 0) if transport_config is None else se(transport_config))
    print(f"Mock server started: {mock_server_port}")
    return mock_server_port

def message_reify(message_handle):
    reified = pactlib.lib.pactffi_message_reify(message_handle)
    return pactlib.ffi.string(reified).decode('utf-8')

def new_sync_message_interaction(pact_handle, description: str):
    return pactlib.lib.pactffi_new_sync_message_interaction(pact_handle, se(description))

def interaction_contents(message_handle, req_or_res="res" or "req", content_type=str, body=str or json):
    if 'json' in content_type:
        encoded_body = pactlib.ffi.new("char[]", se(json.dumps(body)))
    else:
        encoded_body = pactlib.ffi.new("char[]", se(body))
    return pactlib.lib.pactffi_interaction_contents(message_handle,  0 if req_or_res == 'req' else 1, se(content_type), encoded_body)

def with_message_request_contents(message_handle, content_type=str, body=str or json):
    interaction_contents(message_handle, "req", content_type, body)

def with_message_response_contents(message_handle, content_type=str, body=str or json):
    interaction_contents(message_handle, "req", content_type, body)

def verify(mock_server_port, pact_handle, PACT_FILE_DIR, message_pact=None):
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
