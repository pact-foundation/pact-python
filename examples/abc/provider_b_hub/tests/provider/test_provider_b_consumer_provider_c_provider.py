import atexit
import logging
import os

import pytest

from pact import Consumer, Provider, EachLike
from src.provider_b import ProductConsumer

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PACT_BROKER_URL = "http://localhost"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"

PACT_MOCK_HOST = "localhost"
PACT_MOCK_PORT = 1234

PACT_DIR = os.path.dirname(os.path.realpath(__file__))

EXAMPLE_BOOK = {
    "id": 1,
    "title": "The Last Continent",
    "author": "Terry Pratchett",
    "category": "Fantasy",
    "isbn": "0385409893",
    "published": "1998",
}


@pytest.fixture
def consumer() -> ProductConsumer:
    return ProductConsumer("http://{host}:{port}".format(host=PACT_MOCK_HOST, port=PACT_MOCK_PORT))


@pytest.fixture(scope="session")
def pact(request):
    version = 1
    pact = Consumer("ConsumerBClient", version=version).has_pact_with(
        Provider("ProviderCProducts"),
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


def test_get_products(pact, consumer):
    (
        pact.given("Some books exist")
        .upon_receiving("a request for products")
        .with_request("get", "/")
        .will_respond_with(200, body=EachLike(EXAMPLE_BOOK))
    )

    with pact:
        products = consumer.get_products()
        assert len(products) > 0
        pact.verify()
