import platform
from os.path import join, dirname
import subprocess
import pytest
import mock
from pact.ffi.verifier import VerifyStatus

from pact.pact_exception import PactException
from pact.ffi.ffi_verifier import FFIVerify
# import sys
# sys.path.insert(0, './examples/area_calculator')
# from area_calculator_server import serve

def test_version():
    assert FFIVerify().version() == "0.4.5"

@mock.patch("os.listdir")
def test_pact_urls_or_broker_required(mock_Popen):
    verifier = FFIVerify()

    with pytest.raises(PactException) as e:
        verifier.verify(provider="provider", provider_base_url="http://localhost")

    assert "Pact urls or Pact broker required" in str(e)

def test_pact_file_does_not_exist():
    wrapper = FFIVerify()
    result = wrapper.verify(
        "consumer-provider.json",
        provider="test_provider",
        provider_base_url="http://localhost",
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.VERIFIER_FAILED
    target_platform = platform.platform().lower()

    if 'windows' in target_platform:
        assert (
            "Failed to load pact 'consumer-provider.json' - The system cannot find the file specified."
            in "\n".join(result.logs)
        )
    else:
        assert (
            "Failed to load pact 'consumer-provider.json' - No such file or directory"
            in "\n".join(result.logs)
        )

def test_pact_url_does_not_exist():
    wrapper = FFIVerify()
    result = wrapper.verify(
        "http://broker.com/pacts/consumer-provider.json",
        provider="test_provider",
        provider_base_url="http://localhost",
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.VERIFIER_FAILED
    assert (
        "Failed to load pact 'http://broker.com/pacts/consumer-provider.json' - Request failed with status - 404 Not Found"
        in "\n".join(result.logs)
    )

def test_broker_url_does_not_exist():
    wrapper = FFIVerify()
    result = wrapper.verify(
        broker_url="http://broker.com/",
        provider="test_provider",
        provider_base_url="http://localhost",
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.VERIFIER_FAILED
    assert (
        "Failed to load pact - \x1b[31mCould not load pacts from the pact broker 'http://broker.com/'"
        in "\n".join(result.logs)
    )

def test_authed_broker_without_credentials():
    wrapper = FFIVerify()
    result = wrapper.verify(
        broker_url="https://test.pactflow.io",
        provider="Example API",
        provider_base_url="http://localhost",
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.VERIFIER_FAILED
    assert (
        "Failed to load pact - \x1b[31mCould not load pacts from the pact broker 'https://test.pactflow.io'"
        in "\n".join(result.logs)
    )

def test_broker_http_v2_pact_with_filter_state(httpserver):
    body = {"name": "Mary"}
    endpoint = "/alligators/Mary"
    httpserver.expect_request(endpoint).respond_with_json(
        body, content_type="application/json;charset=utf-8"
    )

    wrapper = FFIVerify()
    result = wrapper.verify(
        broker_url="https://test.pactflow.io",
        broker_username="dXfltyFMgNOFZAxr8io9wJ37iUpY42M",
        broker_password="O5AIZWxelWbLvqMd8PkAVycBJh2Psyg1",
        provider="Example API",
        provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
        filter_state="there is an alligator named Mary",
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.SUCCESS

def test_local_http_v2_pact_with_filter_state(httpserver):
    body = {"name": "testing matchers - string"}
    endpoint = "/alligators/Mary"
    httpserver.expect_request(endpoint).respond_with_json(
        body, content_type="application/json;charset=utf-8"
    )

    wrapper = FFIVerify()
    result = wrapper.verify(
        "./examples/pacts/v2-http.json",
        provider="Example API",
        provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
        request_timeout=10,
        filter_state="there is an alligator named Mary",
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.SUCCESS

def test_local_http_v3_pact(httpserver):
    body = {
        "@context": "/api/contexts/Book",
        "@id": "/api/books/0114b2a8-3347-49d8-ad99-0e792c5a31e6",
        "@type": "Book",
        "author": "testing matchers - using regex for id and pub date",
        "description": "testing matchers - string",
        "publicationDate": "2023-02-13T00:00:00+07:00",
        "reviews": [],
        "title": "testing matchers - string"
    }
    endpoint = "/api/books"
    httpserver.expect_request(endpoint).respond_with_json(
        body, content_type="application/ld+json;charset=utf-8"
    )

    wrapper = FFIVerify()
    result = wrapper.verify(
        "./examples/pacts/v3-http.json",
        provider="Example API",
        provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
        request_timeout=10,
        # filter_state="there is an alligator named Mary",
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.SUCCESS

def test_grpc_local_pact():

    grpc_server_process = subprocess.Popen(['python', 'area_calculator_server.py'],
                                           cwd=join(dirname(__file__), '..', '..', 'examples', 'area_calculator'))

    wrapper = FFIVerify()
    result = wrapper.verify(
        "./examples/pacts/v4-grpc.json",
        provider="area-calculator-provider",
        provider_base_url="tcp://127.0.0.1:37757",
        request_timeout=30,
        log_level="INFO",
        provider_transport="protobuf"
    )
    grpc_server_process.terminate()
    assert VerifyStatus(result.return_code) == VerifyStatus.SUCCESS
    # TODO - Plugin success or failure not returned in logs
