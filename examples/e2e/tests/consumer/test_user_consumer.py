"""pact test for user service client"""

import logging

import pytest
from pact import Consumer, Like, Provider, Term, Format

from src.consumer import UserConsumer

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
print(Format().__dict__)


PACT_FILE = "pythonclient-pythonservice.json"
PACT_BROKER_USERNAME = "dXfltyFMgNOFZAxr8io9wJ37iUpY42M"
PACT_BROKER_PASSWORD = "O5AIZWxelWbLvqMd8PkAVycBJh2Psyg1"
PACT_BROKER_URL = "https://test.pact.dius.com.au/"

PACT_MOCK_HOST = 'localhost'
PACT_MOCK_PORT = 1234
# PACT_DIR = os.path.dirname(os.path.realpath(__file__))
PACT_DIR = './'

@pytest.fixture
def consumer():
    return UserConsumer(
        'http://{host}:{port}'
        .format(host=PACT_MOCK_HOST, port=PACT_MOCK_PORT)
    )

@pytest.fixture(scope='session')
def pact(request):
    version = request.config.getoption('--publish-pact')
    publish_to_broker = (not request.node.testsfailed and version)
    print("publish to broker {}".format(publish_to_broker))

    pact = Consumer('PythonClient').has_pact_with(
        Provider('PythonService'), host_name=PACT_MOCK_HOST, port=PACT_MOCK_PORT,
        pact_dir=PACT_DIR, broker_username=PACT_BROKER_USERNAME, broker_password=PACT_BROKER_PASSWORD,
        broker_base_url=PACT_BROKER_URL, publish_to_broker=publish_to_broker, version=version)
    try:
        print('start service')
        pact.start_service()
        yield pact
    finally:
        print('stop service')
        pact.stop_service()

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
    pact.verify()


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
