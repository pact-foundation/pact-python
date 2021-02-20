"""pact test for user service client"""
import logging
import os
from multiprocessing import Process
import pytest

from ..fastapi_provider import run_server

from pact import Verifier

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PACT_UPLOAD_URL = (
    "http://127.0.0.1/pacts/provider/UserService/consumer"
    "/User_ServiceClient/version"
)
PACT_FILE = "userserviceclient-userservice.json"
PACT_BROKER_URL = "http://localhost"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"

PACT_MOCK_HOST = 'localhost'
PACT_MOCK_PORT = 8000
PACT_URL = "http://{}:{}".format(PACT_MOCK_HOST, PACT_MOCK_PORT)
PACT_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture(scope="module")
def server():
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    yield proc
    proc.kill()  # Cleanup after test


def test_get_user_non_admin(server):
    verifier = Verifier(provider='UserService',
                        provider_base_url=PACT_URL)

    output, _ = verifier.verify_pacts('./userserviceclient-userservice.json',
                                      verbose=False,
                                      provider_states_setup_url="{}/_pact/provider_states".format(PACT_URL))

    assert (output == 0)
