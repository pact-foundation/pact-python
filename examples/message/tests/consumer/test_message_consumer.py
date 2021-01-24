"""pact test for user service client"""

import logging
import pytest
import time

from os import remove
from os.path import isfile

from pact import MessageConsumer, Provider
from src.message_handler import MessageHandler, CustomError

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PACT_BROKER_URL = "http://localhost"
PACT_FILE = "userserviceclient-userservice.json"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"
PACT_DIR = 'pacts'

consumer_name = 'DetectContentLambda'
provider_name = 'ContentProvider'
expected_json = (f"{consumer_name.lower().replace(' ', '_')}_message-"
                 + f"{provider_name.lower().replace(' ', '_')}_message.json")

@pytest.fixture(scope='session')
def pact(request):
    version = request.config.getoption('--publish-pact')
    publish = True if version else False

    pact = MessageConsumer(consumer_name, version=version).has_pact_with(
        Provider(provider_name),
        pact_dir=PACT_DIR, publish_to_broker=publish, broker_base_url=PACT_BROKER_URL,
        broker_username=PACT_BROKER_USERNAME, broker_password=PACT_BROKER_PASSWORD)

    yield pact


def cleanup_json(expected_json):
    """
    Remove existing json file before test if any
    """
    if (isfile(f"pacts/{expected_json}")):
        remove(f"pacts/{expected_json}")

def progressive_delay(file, time_to_wait=10, second_interval=0.5, verbose=False):
    """
    progressive delay
    defaults to wait up to 5 seconds with 0.5 second intervals
    """
    time_counter = 0
    while not isfile(file):
        time.sleep(second_interval)
        time_counter += 1
        if verbose:
            print(f'Trying for {time_counter*second_interval} seconds')
        if time_counter > time_to_wait:
            if verbose:
                print(f'Already waited {time_counter*second_interval} seconds')
            break


def test_throw_exception_handler(pact):
    cleanup_json(expected_json)

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
        with pact:
            # handler needs 'documentType' == 'microsoft-word'
            MessageHandler(wrong_event)

    progressive_delay(f"pacts/{expected_json}")
    assert isfile(f"pacts/{expected_json}") == 0


def test_generate_pact_file(pact):
    cleanup_json(expected_json)

    expected_event = {
        'documentName': 'document.doc',
        'creator': 'TP',
        'documentType': 'microsoft-word'
    }

    (pact
     .given('A document create in Document Service')
     .expects_to_receive('Description')
     .with_content(expected_event)
     .with_metadata({
         'Content-Type': 'application/json'
     }))

    with pact:
        # handler needs 'documentType' == 'microsoft-word'
        MessageHandler(expected_event)

    progressive_delay(f"pacts/{expected_json}")
    assert isfile(f"pacts/{expected_json}") == 1
