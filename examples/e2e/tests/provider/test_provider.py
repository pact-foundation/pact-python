"""pact test for user service client"""

import logging
import os
from testcontainers.compose import DockerCompose

from pact import Verifier
import pytest

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


def test_get_user_non_admin():
    verifier = Verifier(provider='UserService',
                        provider_base_url=PACT_URL)

    output, logs = verifier.verify_pacts('./userserviceclient-userservice.json',
                                         verbose=False,
                                         provider_states_setup_url="{}/_pact/provider_states".format(PACT_URL))

    assert (output == 0)


# @pytest.fixture(scope='session')
# def broker():
#     print('Starting broker')
#     with DockerCompose("../broker",
#                        compose_file_name=["docker-compose.yml"],
#                        pull=True) as compose:

#         stdout, stderr = compose.get_logs()
#         if stderr:
#             print("Errors\\n:{}".format(stderr))
#         print(stdout)
#         yield
