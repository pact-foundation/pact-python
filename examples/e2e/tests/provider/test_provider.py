
# VERSION=$1
# if [ -x $VERSION ]; then
#     echo "ERROR: You must specify a provider version"
#     exit
# fi

# pipenv run pact-verifier --provider-base-url=http://localhost:5001 \
#   --pact-url="http://127.0.0.1/pacts/provider/UserService/consumer/UserServiceClient/latest" \
#   --provider-states-setup-url=http://localhost:5001/_pact/provider_states \
#   --provider-app-version $VERSION \
#   --pact-broker-username pactbroker \
#   --pact-broker-password pactbroker \
#   --publish-verification-results


"""pact test for user service client"""

import logging
import os

import pytest
# from flask import Flask, abort, jsonify, request
from multiprocessing import Process

from pact import Verifier

from pact_provider import app

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
PACT_MOCK_PORT = 1235
PACT_URL = "http://{}:{}".format(PACT_MOCK_HOST, PACT_MOCK_PORT)
PACT_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture(scope='session')
def provider():
    print('start flask')
    server = Process(target=app.run, kwargs={'port': PACT_MOCK_PORT})

    try:
        server.start()

        yield
    finally:
        print('end flask')
        server.terminate()


def test_get_user_non_admin(provider):
    verifier = Verifier(provider='UserService',
                        provider_base_url=PACT_URL)

    output, logs = verifier.verify_pacts('./userserviceclient-userservice.json',
                                         verbose=False,
                                         provider_states_setup_url="{}/_pact/provider_states".format(PACT_URL))

    assert (output == 0)
