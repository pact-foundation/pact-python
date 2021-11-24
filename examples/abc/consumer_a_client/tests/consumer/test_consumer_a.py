"""pact test for hub service consumer"""

import atexit
import logging
import os

import pytest

from pact import Consumer, Like, Provider, EachLike
from src.consumer_a import HubConsumer

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

EXAMPLE_ORDER = {"id": 1, "ordered": "2021-11-01", "shipped": "2021-11-14", "product_ids": [1, 2]}


@pytest.fixture
def consumer() -> HubConsumer:
    return HubConsumer("http://{host}:{port}".format(host=PACT_MOCK_HOST, port=PACT_MOCK_PORT))


@pytest.fixture(scope="session")
def pact(request):
    """Setup a Pact Consumer, which provides the Provider mock service. This
    will generate and optionally publish Pacts to the Pact Broker"""

    # When publishing a Pact to the Pact Broker, a version number of the Consumer
    # is required, to be able to construct the compatability matrix between the
    # Consumer versions and Provider versions
    version = request.config.getoption("--publish-pact")
    publish = True if version else False

    pact = Consumer("ConsumerAClient", version=version).has_pact_with(
        Provider("ProviderBHub"),
        host_name=PACT_MOCK_HOST,
        port=PACT_MOCK_PORT,
        pact_dir=PACT_DIR,
        publish_to_broker=publish,
        broker_base_url=PACT_BROKER_URL,
        broker_username=PACT_BROKER_USERNAME,
        broker_password=PACT_BROKER_PASSWORD,
    )

    pact.start_service()

    # Make sure the Pact mocked provider is stopped when we finish, otherwise
    # port 1234 may become blocked
    atexit.register(pact.stop_service)

    yield pact

    # This will stop the Pact mock server, and if publish is True, submit Pacts
    # to the Pact Broker
    pact.stop_service()

    # Given we have cleanly stopped the service, we do not want to re-submit the
    # Pacts to the Pact Broker again atexit, since the Broker may no longer be
    # available if it has been started using the --run-broker option, as it will
    # have been torn down at that point
    pact.publish_to_broker = False


def test_get_product(pact, consumer):
    (
        pact.given("Some books exist")
        .upon_receiving("a request for product 1")
        .with_request("get", "/products/1")
        .will_respond_with(200, body=Like(EXAMPLE_BOOK))
    )

    with pact:
        product = consumer.get_product(1)
        assert product.title == "The Last Continent"
        pact.verify()


def test_get_products(pact, consumer):

    (
        pact.given("Some books exist")
        .upon_receiving("a request for products")
        .with_request("get", "/products")
        .will_respond_with(200, body=EachLike(EXAMPLE_BOOK))
    )

    with pact:
        products = consumer.get_products()
        assert len(products) > 0
        pact.verify()


def test_get_order(pact, consumer):
    (
        pact.given("Some orders exist")
        .upon_receiving("a request for order 1")
        .with_request("get", "/orders/1")
        .will_respond_with(200, body=Like(EXAMPLE_ORDER))
    )

    with pact:
        order = consumer.get_order(1)
        assert order.ordered == "2021-11-01"
        pact.verify()
