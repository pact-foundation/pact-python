"""pact test for user service client"""
import logging

import pytest

from pact import Verifier

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# For the purposes of this example, the broker is started up as a fixture defined
# in conftest.py. For normal usage this would be self-hosted or using Pactflow.
PACT_BROKER_URL = "http://localhost"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"

# For the purposes of this example, the FastAPI provider will be started up as
# a fixture in conftest.py ("server"). Alternatives could be, for example
# running a Docker container with a database of test data configured.
# This is the "real" provider to verify against.
PROVIDER_HOST = "127.0.0.1"
PROVIDER_PORT = 8000
PROVIDER_URL = f"http://{PROVIDER_HOST}:{PROVIDER_PORT}"
PROVIDER_NAME = "ProviderBHub"


@pytest.fixture
def broker_opts():
    return {
        "broker_username": PACT_BROKER_USERNAME,
        "broker_password": PACT_BROKER_PASSWORD,
        "broker_url": PACT_BROKER_URL,
        "publish_version": "3",
        "publish_verification_results": True,
    }


def test_provider_b_hub_against_broker(server, broker_opts, **kwargs):
    verifier = Verifier(provider=PROVIDER_NAME, provider_base_url=PROVIDER_URL)

    success, logs = verifier.verify_with_broker(
        **broker_opts,
        verbose=True,
        provider_states_setup_url=f"{PROVIDER_URL}/_pact/provider_states",
        enable_pending=False,
    )
    assert success == 0
