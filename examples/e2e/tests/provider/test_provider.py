
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

PACT_FILE = "pythonclient-pythonservice.json"
PACT_BROKER_URL = "https://test.pact.dius.com.au/"
PACT_BROKER_USERNAME = "dXfltyFMgNOFZAxr8io9wJ37iUpY42M"
PACT_BROKER_PASSWORD = "O5AIZWxelWbLvqMd8PkAVycBJh2Psyg1"

PACT_MOCK_HOST = 'localhost'
PACT_MOCK_PORT = 1235
PACT_URL = "http://{}:{}".format(PACT_MOCK_HOST, PACT_MOCK_PORT)
PACT_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture()
def provider():
    print('start flask')
    server = Process(target=app.run, kwargs={'port': PACT_MOCK_PORT})

    try:
        server.start()
        yield

    finally:
        print('end flask')
        server.terminate()


def test_get_user_non_admin_file(provider):
    verifier = Verifier(provider='PythonService',
                        provider_base_url=PACT_URL)

    output, logs = verifier.verify_pacts(PACT_FILE,
                                         verbose=False,
                                         provider_states_setup_url="{}/_pact/provider_states".format(PACT_URL))

    assert (output == 0)


def test_get_user_non_admin_broker(provider):
    verifier = Verifier(provider='PythonService',
                        provider_base_url=PACT_URL)

    output, logs = verifier.verify_with_broker(broker_username=PACT_BROKER_USERNAME,
                                               broker_password=PACT_BROKER_PASSWORD,
                                               broker_url=PACT_BROKER_URL,
                                               verbose=False,
                                               provider_states_setup_url="{}/_pact/provider_states".format(PACT_URL))

    assert (output == 0)
