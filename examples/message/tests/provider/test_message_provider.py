import os
import pytest
from pact import MessageProvider

use_pactflow = int(os.getenv('USE_HOSTED_PACT_BROKER', '0'))
if use_pactflow == 1:
    PACT_BROKER_URL = os.getenv("PACT_BROKER_URL", "https://test.pactflow.io")
    PACT_BROKER_USERNAME = os.getenv("PACT_BROKER_USERNAME", "dXfltyFMgNOFZAxr8io9wJ37iUpY42M")
    PACT_BROKER_PASSWORD = os.getenv("PACT_BROKER_PASSWORD", "O5AIZWxelWbLvqMd8PkAVycBJh2Psyg1")
else:
    PACT_BROKER_URL = os.getenv("PACT_BROKER_URL", "http://localhost")
    PACT_BROKER_USERNAME = os.getenv("PACT_BROKER_USERNAME", "pactbroker")
    PACT_BROKER_PASSWORD = os.getenv("PACT_BROKER_PASSWORD", "pactbroker")
PACT_DIR = "pacts"


@pytest.fixture
def default_opts():
    return {
        'broker_username': PACT_BROKER_USERNAME,
        'broker_password': PACT_BROKER_PASSWORD,
        'broker_url': PACT_BROKER_URL,
        'publish_version': '3',
        'publish_verification_results': True
    }


def document_created_handler():
    return {
        "event": "ObjectCreated:Put",
        "documentName": "document.doc",
        "creator": "TP",
        "documentType": "microsoft-word"
    }


def document_deleted_handler():
    return {
        "event": "ObjectCreated:Delete",
        "documentName": "document.doc",
        "creator": "TP",
        "documentType": "microsoft-word"
    }


def test_verify_success():
    provider = MessageProvider(
        message_providers={
            'A document created successfully': document_created_handler,
            'A document deleted successfully': document_deleted_handler
        },
        provider='ContentProvider',
        consumer='DetectContentLambda',
        pact_dir='pacts'

    )
    with provider:
        success, logs = provider.verify()
        assert success == 0


def test_verify_failure_when_a_handler_missing():
    provider = MessageProvider(
        message_providers={
            'A document created successfully': document_created_handler,
        },
        provider='ContentProvider',
        consumer='DetectContentLambda',
        pact_dir='pacts'

    )

    with provider:
        success, logs = provider.verify()
        assert success == 1


def test_verify_from_broker(default_opts):
    provider = MessageProvider(
        message_providers={
            'A document created successfully': document_created_handler,
            'A document deleted successfully': document_deleted_handler
        },
        provider='ContentProvider',
        consumer='DetectContentLambda',
    )

    with provider:
        success, logs = provider.verify_with_broker(**default_opts)
        assert success == 0
