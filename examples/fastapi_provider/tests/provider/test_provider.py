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


def test_success():
    pass


@pytest.fixture
def broker_opts():
    return {
        "broker_username": PACT_BROKER_USERNAME,
        "broker_password": PACT_BROKER_PASSWORD,
        "broker_url": PACT_BROKER_URL,
        "publish_version": "3",
        "publish_verification_results": True,
    }


def test_user_service_provider_against_broker(server, broker_opts):
    verifier = Verifier(provider="UserService", provider_base_url=PROVIDER_URL)

    # Request all Pact(s) from the Pact Broker to verify this Provider against.
    # In the Pact Broker logs, this corresponds to the following entry:
    # PactBroker::Api::Resources::ProviderPactsForVerification -- Fetching pacts for verification by UserService -- {:provider_name=>"UserService", :params=>{}}
    success, logs = verifier.verify_with_broker(
        **broker_opts,
        verbose=True,
        provider_states_setup_url=f"{PROVIDER_URL}/_pact/provider_states",
        enable_pending=False,
    )
    # If publish_verification_results is set to True, the results will be
    # published to the Pact Broker.
    # In the Pact Broker logs, this corresponds to the following entry:
    #   PactBroker::Verifications::Service -- Creating verification 200 for \
    #   pact_version_sha=c8568cbb30d2e3933b2df4d6e1248b3d37f3be34 -- \
    #   {"success"=>true, "providerApplicationVersion"=>"3", "wip"=>false, \
    #   "pending"=>"true"}

    # Note:
    #  If "successful", then the return code here will be 0
    #  This can still be 0 and so PASS if a Pact verification FAILS, as long as
    #  it has not resulted in a REGRESSION of an already verified interaction.
    #  See https://docs.pact.io/pact_broker/advanced_topics/pending_pacts/ for
    #  more details.
    assert success == 0


def test_user_service_provider_against_pact(server):
    verifier = Verifier(provider="UserService", provider_base_url=PROVIDER_URL)

    # Rather than requesting the Pact interactions from the Pact Broker, this
    # will perform the verification based on the Pact file locally.
    #
    # Because there is no way of knowing the previous state of an interaction,
    # if it has been successful in the past (since this is what the Pact Broker
    # is for), if the verification of an interaction fails then the success
    # result will be != 0, and so the test will FAIL.
    output, _ = verifier.verify_pacts(
        "../pacts/userserviceclient-userservice.json",
        verbose=False,
        provider_states_setup_url="{}/_pact/provider_states".format(PROVIDER_URL),
    )

    assert output == 0
