import pytest
from pact import MessageProvider

def document_created_handler():
    return {
        "event": "ObjectCreated:Put",
        "bucket": "bucket_name",
        "key": "path_to_file_in_s3.pdf",
        "documentType": "application/pdf"
    }

def document_deleted_handler():
    return {
        "event": "ObjectCreated:Delete",
        "bucket": "bucket_name",
        "key": "existing_file_in_s3.pdf",
        "documentType": "application/pdf"
    }

def test_verify_success():
    provider = MessageProvider(
        message_providers={
            'A document created successfully': document_created_handler,
            'A document deleted successfully': document_deleted_handler
        },
        provider='DocumentService',
        consumer='DetectContentLambda'
    )
    with provider:
        provider.verify()

def test_verify_failure_when_a_provider_missing():
    provider = MessageProvider(
        message_providers={
            'A document created successfully': document_created_handler,
        },
        provider='DocumentService',
        consumer='DetectContentLambda'
    )

    with pytest.raises(AssertionError):
        with provider:
            provider.verify()
