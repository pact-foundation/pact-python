import platform
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
    # mock_Popen.return_value.returncode = 2
    verifier = FFIVerify()

    with pytest.raises(PactException) as e:
        verifier.verify(provider="provider", provider_base_url="http://localhost")

    assert "Pact urls or Pact broker required" in str(e)


def test_pact_local_file_provided_but_does_not_exist():
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


def test_pact_url_provided_but_does_not_exist():
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


def test_with_broker_url_no_auth_unable_to_load():
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


def test_with_authenticated_broker_without_credentials():
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

def test_with_authenticated_broker_with_credentials_and_logs_to_buffer(httpserver):
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

def test_with_authenticated_broker_with_credentials_and_logs_to_file(httpserver):
    body = {"name": "Mary"}
    endpoint = "/alligators/Mary"
    httpserver.expect_request(endpoint).respond_with_json(
        body, content_type="application/json;charset=utf-8"
    )

    wrapper = FFIVerify()
    result = wrapper.verify(
        # broker_url="http://localhost",
        broker_url="https://test.pactflow.io",
        broker_username="dXfltyFMgNOFZAxr8io9wJ37iUpY42M",
        broker_password="O5AIZWxelWbLvqMd8PkAVycBJh2Psyg1",
        # broker_token="129cCdfCWhMzcC9pFwb4bw",
        provider="Example API",
        provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
        filter_state="there is an alligator named Mary",
        # log_dir="./logs"
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.SUCCESS

# def test_grpc_local_pact():
#     wrapper = FFIVerify()
#     result = wrapper.verify(
#         "./examples/pacts/v4-grpc.json",
#         provider="area-calculator-provider",
#         provider_base_url="tcp://127.0.0.1:37757",
#         # provider_base_url="tcp://127.0.0.1:{}".format(httpserver.port),
#         request_timeout=10,
#         log_level="TRACE",
#         # plugin_name="protobuf",
#         provider_transport="protobuf"
#         # scheme="grpc",
#         # host="localhost",
#         # port=37757,
#         # path="/",
#     )
#     assert VerifyStatus(result.return_code) == VerifyStatus.NULL_POINTER
#     assert (
#         "Failed to load pact - \x1b[31mCould not load pacts from the pact broker 'http://localhost.com'"
#         in "\n".join(result.logs)
#     )
