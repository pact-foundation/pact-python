from pact import MessageProvider

def success_handler():
    return {
        'documentName': 'document.doc',
        'creator': 'TP',
        'documentType': 'microsoft-word'
    }

def delete_handler():
    return {
        'message_delete': True
    }

def test_start_http_server():
    provider = MessageProvider(
        message_providers={
            'A document create in Document Service': success_handler,
            'Document delete successfully': delete_handler
        },
        provider='ContentProvider',
        consumer='DetectContentLambda',
        pact_dir='pacts'
    )

    with provider:
        provider.verify()
