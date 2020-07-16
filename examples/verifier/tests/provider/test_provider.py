
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
PACT_MOCK_PORT = 1234
PACT_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def provider():
    # flask start
    print('start flask')
    yield
    print('end flask')


def test_get_user_non_admin(provider):
    print('verify our test')

    # pact_broker_username = "pactbroker",
    # pact_broker_password = "pactbroker"
    # # publish_verification_result = True
    # # providerVersion = "1.0.0"
    # pactBrokerUrl = "http://localhost"

    verifier = Verifier(provider='UserService',
                        provider_base_url='http://localhost:1234')

    output, logs = verifier.verify_pacts('./userserviceclient-userservice.json')

    print(output)
    print(logs)
    assert (output == 0)
