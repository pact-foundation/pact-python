"""pact test for user service client"""

import logging
import os
import atexit

from testcontainers.compose import DockerCompose

import pytest
from pact import Consumer, Like, Provider, Term, Format

from src.consumer import UserConsumer

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
print(Format().__dict__)

PACT_BROKER_URL = "http://localhost"
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
def broker(request):
    version = request.config.getoption('--publish-pact')
    publish = True if version else False

    if not publish:
        return

    print('Starting broker')
    with DockerCompose("../broker",
                       compose_file_name=["docker-compose.yml"],
                       pull=True) as compose:

        stdout, stderr = compose.get_logs()
        if stderr:
            print("Errors\\n:{}".format(stderr))
        print(stdout)
        yield


@pytest.fixture(scope='session')
def pact(request):
    version = request.config.getoption('--publish-pact')
    publish = True if version else False

    pact = Consumer('UserServiceClient', version=version).has_pact_with(
        Provider('UserService'), host_name=PACT_MOCK_HOST, port=PACT_MOCK_PORT,
        pact_dir=PACT_DIR, publish_to_broker=publish, broker_base_url=PACT_BROKER_URL,
        broker_username=PACT_BROKER_USERNAME, broker_password=PACT_BROKER_PASSWORD)

    print('start service')
    pact.start_service()
    # atexit.register(pact.stop_service)

    yield pact
    print('stop service')
    pact.stop_service()

def test_get_user_non_admin(broker, pact, consumer):
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

    with pact:
        user = consumer.get_user('UserA')
        assert user.name == 'UserA'


def test_get_non_existing_user(broker, pact, consumer):
    (pact
     .given('UserA does not exist')
     .upon_receiving('a request for UserA')
     .with_request('get', '/users/UserA')
     .will_respond_with(404))

    with pact:
        user = consumer.get_user('UserA')
        assert user is None
    # pact.verify()
