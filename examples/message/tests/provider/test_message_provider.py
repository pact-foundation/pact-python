from pact import MessageProvider

def handler():
    return {
        'success': True
    }


def delete_handler():
    return {
        'message_delete': True
    }

def test_start_http_server():
    provider = MessageProvider(
        message_providers={
            'Document created successfully': handler(),
            'Document delete successfully': delete_handler()
        },
        provider='DocumentService',
        consumer='ExtractContentLambda',
        pact_dir='pacts',
        version='3.0.0'
    )

    provider.verify()
