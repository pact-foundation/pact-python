"""pact test for user service client"""

import logging
from unittest.mock import patch

import pytest
from pact import MessageConsumer, Provider

from src.message_handler import MessageHandler, CustomError

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PACT_BROKER_URL = "http://localhost"
PACT_FILE = "userserviceclient-userservice.json"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"
PACT_DIR = 'pacts'


@pytest.fixture(scope='session')
def pact(request):
    version = request.config.getoption('--publish-pact')
    publish = True if version else False

    pact = MessageConsumer('DetectContentLambda', version=version).has_pact_with(
        Provider('ContentProvider'),
        pact_dir=PACT_DIR, publish_to_broker=publish, broker_base_url=PACT_BROKER_URL,
        broker_username=PACT_BROKER_USERNAME, broker_password=PACT_BROKER_PASSWORD)

    yield pact


def test_generate_pact_file(pact):
    expected_event = {
        'documentName': 'document.doc',
        'creator': 'TP',
        'documentType': 'microsoft-word'
    }

    (pact
     .given('A document create in Document Service')
     .expects_to_receive('Provider state attribute')
     .with_content(expected_event)
     .with_metadata({
         'Content-Type': 'application/json'
     }))

    with patch.object(pact, 'write_to_pact_file') as mock:
        with pact:
            # handler needs 'documentType' == 'microsoft-word'
            MessageHandler(expected_event)
        mock.assert_called_once()


def test_throw_exception_handler(pact):
    wrong_event = {
        'documentName': 'spreadsheet.xls',
        'creator': 'WI',
        'documentType': 'microsoft-excel'
    }

    (pact
     .given('Another document in Document Service')
     .expects_to_receive('Description')
     .with_content(wrong_event)
     .with_metadata({
         'Content-Type': 'application/json'
     }))

    with pytest.raises(CustomError):
        with patch.object(pact, 'write_to_pact_file') as mock:
            with pact:
                # handler needs 'documentType' == 'microsoft-word'
                MessageHandler(wrong_event)
            mock.assert_not_called()
