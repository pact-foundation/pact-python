from pact import MessageProvider

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
        pact_dir='pacts'
    )

    with provider:
        provider.verify()
