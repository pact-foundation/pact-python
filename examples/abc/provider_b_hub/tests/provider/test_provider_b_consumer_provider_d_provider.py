import atexit
import logging
import os

import pytest

from pact import Consumer, Provider, EachLike
from src.provider_b import OrderConsumer

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PACT_BROKER_URL = "http://localhost"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"

PACT_MOCK_HOST = "localhost"
PACT_MOCK_PORT = 1234

PACT_DIR = os.path.dirname(os.path.realpath(__file__))

EXAMPLE_ORDER = {"id": 1, "ordered": "2021-11-01", "shipped": "2021-11-14", "product_ids": [1, 2]}


@pytest.fixture
def consumer() -> OrderConsumer:
    return OrderConsumer("http://{host}:{port}".format(host=PACT_MOCK_HOST, port=PACT_MOCK_PORT))


@pytest.fixture(scope="session")
def pact():
    version = 1

    pact = Consumer("ConsumerBClient", version=version).has_pact_with(
        Provider("ProviderDOrders"),
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


def test_get_orders(pact, consumer):
    (
        pact.given("Some orders exist")
        .upon_receiving("a request for order 1")
        .with_request("get", "/1")
        .will_respond_with(200, body=EachLike(EXAMPLE_ORDER))
    )

    with pact:
        orders = consumer.get_order(1)
        assert len(orders) > 0
        pact.verify()
