import atexit
import json
import logging
import os
import pathlib

import pytest

from interactions import HUB_TO_PROVIDER_INTERACTIONS
from pact import Consumer, Provider, EachLike
from src.provider_b import ProductConsumer

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PACT_BROKER_URL = "http://localhost"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"

PACT_MOCK_HOST = "localhost"
PACT_MOCK_PORT = 1234

PROVIDER_NAME = "ProviderCProducts"

PACT_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def product_consumer() -> ProductConsumer:
    return ProductConsumer("http://{host}:{port}".format(host=PACT_MOCK_HOST, port=PACT_MOCK_PORT))


@pytest.fixture(scope="session")
def pact(request):
    version = 1
    pact = Consumer("ConsumerBClient", version=version).has_pact_with(
        Provider(PROVIDER_NAME),
        host_name=PACT_MOCK_HOST,
        port=PACT_MOCK_PORT,
        pact_dir=PACT_DIR,
        publish_to_broker=False,
        broker_base_url=PACT_BROKER_URL,
        broker_username=PACT_BROKER_USERNAME,
        broker_password=PACT_BROKER_PASSWORD,
    )

    pact.start_service()
    atexit.register(pact.stop_service)

    yield pact

    pact.stop_service()
    pact.publish_to_broker = False


@pytest.mark.parametrize(
    "given,pair",
    [(given, pair) for given, pair in HUB_TO_PROVIDER_INTERACTIONS.items() if pair.provider_name == PROVIDER_NAME],
)
def test_interactions(pact, product_consumer, given, pair):
    """For every interaction state defined, which is used by the Consumer A -> Provider B states, perform the appropriate call with B acting as Consumer.

    This ensures that we are actually mocking up valid expected responses from the chained service, since this will ensure that there is a valid Pact between
    B and C, D etc.
    """
    source = str(pathlib.Path.cwd().joinpath("tests/resources").joinpath(pair.response_content_filename).resolve())
    with open(source) as json_file:
        payload = json.load(json_file)

    # TODO: Needs to be more generic / able to handle other cases
    if len(payload) > 0:
        body = EachLike(payload[0])
    else:
        body = []

    (
        pact.given(given)
        .upon_receiving("todo")
        .with_request(pair.request_args.action, pair.request_args.path)
        .will_respond_with(pair.response_status, body=body)
    )

    with pact:
        getattr(product_consumer, pair.method_name)(**pair.method_args)
        pact.verify()
