"""pact test for user service client"""

import logging

import pytest
from pact import MessageConsumer, Provider

from src.consumer import UserConsumer

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
    (pact
     .given('A document create in Document Service')
     .expects_to_receive('Provider state attribute')
     .with_content({
         'id': '42',
         'documentName': 'sample.docx',
         'creator': 'TP',
         'documentType': 'microsoft-word'
     })
     .with_metadata({
         "Content-Type": "application/json"
     }))

    with pact:
        user = UserConsumer().get_id('42')
        assert user.name == 'forty-two'
        log.info("In Python context END")
