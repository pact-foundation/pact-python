"""pact test for user service client"""

import json
import logging
import os
import requests
from requests.auth import HTTPBasicAuth

import pytest
from pact import Consumer, Like, Provider, Term, Format

from src.consumer import UserConsumer

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
print(Format().__dict__)

PACT_UPLOAD_URL = (
    "http://127.0.0.1/pacts/provider/UserService/consumer"
    "/UserServiceClient/version"
)
PACT_FILE = "userserviceclient-userservice.json"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"

PACT_MOCK_HOST = 'localhost'
PACT_MOCK_PORT = 1234
PACT_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def consumer():
    return UserConsumer(
        'http://{host}:{port}'
        .format(host=PACT_MOCK_HOST, port=PACT_MOCK_PORT)
    )


@pytest.fixture(scope='session')
def pact(request):
    pact = Consumer('UserServiceClient').has_pact_with(
        Provider('UserService'), host_name=PACT_MOCK_HOST, port=PACT_MOCK_PORT,
        pact_dir=PACT_DIR)
    try:
        print('start service')
        pact.start_service()
        yield pact
    finally:
        print('stop service')
        pact.stop_service()

    version = request.config.getoption('--publish-pact')
    if not request.node.testsfailed and version:
        push_to_broker(version)


def push_to_broker(version):
    """
    Push to broker
    """
    with open(os.path.join(PACT_DIR, PACT_FILE), 'rb') as pact_file:
        pact_file_json = json.load(pact_file)

    basic_auth = HTTPBasicAuth(PACT_BROKER_USERNAME, PACT_BROKER_PASSWORD)

    log.info("Uploading pact file to pact broker...")

    r = requests.put(
        "{}/{}".format(PACT_UPLOAD_URL, version),
        auth=basic_auth,
        json=pact_file_json
    )
    if not r.ok:
        log.error("Error uploading: %s", r.content)
        r.raise_for_status()


def test_get_user_non_admin(pact, consumer):
    expected = {
        'name': 'UserA',
        'id': Format().uuid,
        'created_on': Term(
            r'\d+-\d+-\d+T\d+:\d+:\d+',
            '2016-12-15T20:16:01'
        ),
        'ip_address': Format().ip_address,
        'admin': False
    }

    (pact
     .given('UserA exists and is not an administrator')
     .upon_receiving('a request for UserA')
     .with_request('get', '/users/UserA')
     .will_respond_with(200, body=Like(expected)))

    # pact.setup()

    with pact:
        user = consumer.get_user('UserA')
        assert user.name == 'UserA'

    # pact.verify()


def test_get_non_existing_user(pact, consumer):
    (pact
     .given('UserA does not exist')
     .upon_receiving('a request for UserA')
     .with_request('get', '/users/UserA')
     .will_respond_with(404))

    with pact:
        user = consumer.get_user('UserA')
        assert user is None
    # pact.verify()
