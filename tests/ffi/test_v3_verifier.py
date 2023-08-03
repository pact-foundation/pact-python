import pytest
from pact import VerifierV3
import platform
from pact.ffi.verifier import VerifyStatus
from pact.pact_exception import PactException


def test_pact_urls_or_broker_required():
    verifier = VerifierV3(provider="provider", provider_base_url="http://localhost")
    with pytest.raises(PactException) as e:
        verifier.verify_pacts()

    assert "Pact sources or pact_broker_url required" in str(e)

def test_pact_file_does_not_exist():
    verifier = VerifierV3(provider="test_provider",
                          provider_base_url="http://localhost",
                          )
    result = verifier.verify_pacts(
        sources=["consumer-provider.json"],
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

    verifier = VerifierV3(provider="test_provider",
                          provider_base_url="http://localhost",
                          )
    result = verifier.verify_pacts(
        sources=["http://broker.com/pacts/consumer-provider.json"],
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.VERIFIER_FAILED
    assert (
        "Failed to load pact 'http://broker.com/pacts/consumer-provider.json' - Request failed with status - 404 Not Found"
        in "\n".join(result.logs)
    )

def test_broker_url_does_not_exist():

    verifier = VerifierV3(provider="Example API",
                          provider_base_url="http://localhost",
                          )
    result = verifier.verify_pacts(
        broker_url="http://broker.com/",
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.VERIFIER_FAILED
    assert (
        "Failed to load pact - \x1b[31mCould not load pacts from pact broker 'http://broker.com/'"
        in "\n".join(result.logs)
    )

def test_authed_broker_without_credentials():
    verifier = VerifierV3(provider="Example API",
                          provider_base_url="http://localhost",
                          )
    result = verifier.verify_pacts(
        broker_url="https://test.pactflow.io",

    )
    assert VerifyStatus(result.return_code) == VerifyStatus.VERIFIER_FAILED
    assert (
        "Failed to load pact - \x1b[31mCould not load pacts from pact broker 'https://test.pactflow.io'"
        in "\n".join(result.logs)
    )


def test_local_http_v2_pact_with_filter_state_and_consumer_filters(httpserver):
    body = {"name": "testing matchers - string"}
    endpoint = "/alligators/Mary"
    httpserver.expect_request(endpoint).respond_with_json(
        body, content_type="application/json;charset=utf-8"
    )

    verifier = VerifierV3(provider='Example API',
                          provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
                          )

    result = verifier.verify_pacts(
        sources=['./examples/pacts'],
        broker_username='foo',
        filter_state="there is an alligator named Mary",
        no_pacts_is_error=True,
        add_custom_header=[
            {'name': 'custom_header',
             'value': 'test'}
        ],
        consumer_filters=['Example App']
    )

    assert VerifyStatus(result.return_code) == VerifyStatus.SUCCESS

def test_broker_http_v2_pact_with_filter_state(httpserver):
    body = {"name": "Mary"}
    endpoint = "/alligators/Mary"
    httpserver.expect_request(endpoint).respond_with_json(
        body, content_type="application/json;charset=utf-8"
    )

    verifier = VerifierV3(provider='Example API',
                          provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
                          )

    result = verifier.verify_pacts(
        # broker_url="http://0.0.0.0",
        # broker_username="pactbroker",
        # broker_password="pactbroker",
        no_pacts_is_error=True,
        broker_url="https://test.pactflow.io",
        broker_username="dXfltyFMgNOFZAxr8io9wJ37iUpY42M",
        broker_password="O5AIZWxelWbLvqMd8PkAVycBJh2Psyg1",
        provider="Example API",
        provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
        filter_state="there is an alligator named Mary",
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.SUCCESS

def test_pact_via_url_http_v2_pact_with_filter_state(httpserver):
    body = {"name": "Mary"}
    endpoint = "/alligators/Mary"
    httpserver.expect_request(endpoint).respond_with_json(
        body, content_type="application/json;charset=utf-8"
    )

    verifier = VerifierV3(provider='Example API',
                          provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
                          )

    result = verifier.verify_pacts(
        sources=[
            'https://test.pactflow.io/pacts/provider/Example%20API/consumer/Example%20App/latest'
        ],
        broker_username="dXfltyFMgNOFZAxr8io9wJ37iUpY42M",
        broker_password="O5AIZWxelWbLvqMd8PkAVycBJh2Psyg1",
        provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
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

    verifier = VerifierV3(provider='http-provider',
                          provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
                          )
    result = verifier.verify_pacts(
        sources=["./examples/pacts/v3-http.json"],
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.SUCCESS

def test_broker_consumer_version_selectors_http_v2_pact(httpserver):
    body = {"name": "Mary"}
    endpoint = "/alligators/Mary"
    httpserver.expect_request(endpoint).respond_with_json(
        body, content_type="application/json;charset=utf-8"
    )

    verifier = VerifierV3(provider='Example API',
                          provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
                          )

    result = verifier.verify_pacts(
        # broker_url="http://0.0.0.0",
        # broker_username="pactbroker",
        # broker_password="pactbroker",
        no_pacts_is_error=True,
        broker_url="https://test.pactflow.io",
        broker_username="dXfltyFMgNOFZAxr8io9wJ37iUpY42M",
        broker_password="O5AIZWxelWbLvqMd8PkAVycBJh2Psyg1",
        provider="Example API",
        provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
        filter_state="there is an alligator named Mary",
        provider_branch='main',
        consumer_version_selectors=[
            {"mainBranch": True},  # (recommended) - Returns the pacts for consumers configured mainBranch property
            {"deployedOrReleased": True},  # (recommended) - Returns the pacts for all versions of the consumer that are currently deployed or
            # released and currently supported in any environment.
            {"matchingBranch": True},
            {"deployed": "test"},  # Normally, this would not be needed, Any versions currently deployed to the specified environment.
            {"deployed": "production"},  # Normally, this would not be needed, Any versions currently deployed to the specified environment.
            # Normally, this would not be needed, Any versions currently deployed or released and supported in the specified environment.
            {"environment": "test"},
            # Normally, this would not be needed, Any versions currently deployed or released and supported in the specified environment.
            {"environment": "production"},
        ]
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.SUCCESS

def test_broker_publish_http_v2_pact(httpserver):
    body = {"name": "Mary"}
    endpoint = "/alligators/Mary"
    httpserver.expect_request(endpoint).respond_with_json(
        body, content_type="application/json;charset=utf-8"
    )

    verifier = VerifierV3(provider='Example API',
                          provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
                          )

    result = verifier.verify_pacts(
        # broker_url="http://0.0.0.0",
        # broker_username="pactbroker",
        # broker_password="pactbroker",
        no_pacts_is_error=True,
        broker_url="https://test.pactflow.io",
        broker_username="dXfltyFMgNOFZAxr8io9wJ37iUpY42M",
        broker_password="O5AIZWxelWbLvqMd8PkAVycBJh2Psyg1",
        provider="Example API",
        provider_base_url="http://127.0.0.1:{}".format(httpserver.port),
        filter_state="there is an alligator named Mary",
        provider_branch='main',
        consumer_version_selectors=[
            {"mainBranch": True},  # (recommended) - Returns the pacts for consumers configured mainBranch property
            {"deployedOrReleased": True},  # (recommended) - Returns the pacts for all versions of the consumer that are currently deployed or
            # released and currently supported in any environment.
            {"matchingBranch": True},
            {"deployed": "test"},  # Normally, this would not be needed, Any versions currently deployed to the specified environment.
            {"deployed": "production"},  # Normally, this would not be needed, Any versions currently deployed to the specified environment.
            # Normally, this would not be needed, Any versions currently deployed or released and supported in the specified environment.
            {"environment": "test"},
            # Normally, this would not be needed, Any versions currently deployed or released and supported in the specified environment.
            {"environment": "production"},
        ],
        publish_verification_results=True,
        provider_app_version='1.0.0'  # TODO:- defaults to NULL, should error if not set and publish_verification_results=True
    )
    assert VerifyStatus(result.return_code) == VerifyStatus.SUCCESS
