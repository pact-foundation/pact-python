from pact import MessageProvider
import os

def success_handler():
    return {
        'documentName': 'document.doc',
        'creator': 'TP',
        'documentType': 'microsoft-word'
    }

def test_a_document_create_successfully():
    provider = MessageProvider(
        message_providers={
            'A document create in Document Service': success_handler
        },
        provider='ContentProvider',
        consumer='DetectContentLambda',
        pact_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    )

    with provider:
        provider.verify()
