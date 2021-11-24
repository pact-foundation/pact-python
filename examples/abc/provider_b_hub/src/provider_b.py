import logging

import requests
from fastapi import FastAPI, APIRouter
from fastapi.logger import logger

PRODUCT_URL = "https://productstore"
ORDER_URL = "https://orders"

logger.setLevel(logging.DEBUG)

router = APIRouter()
app = FastAPI()

session = requests.Session()


class ProductConsumer(object):
    def __init__(self, base_uri: str):
        self.base_uri = base_uri

    def get_product_by_id(self, product_id: int):
        response = session.get(self.base_uri)
        product = [p for p in response.json() if p["id"] == product_id]

        if product:
            return product[0]
        else:
            return None

    def get_products(self):
        response = session.get(self.base_uri)
        return response.json()


class OrderConsumer(object):
    def __init__(self, base_uri: str):
        self.base_uri = base_uri

    def get_order(self, order_id: int):
        url = f"{self.base_uri}/{order_id}"
        response = session.get(url)
        return response.json()


product_consumer = ProductConsumer(PRODUCT_URL)
order_consumer = OrderConsumer(ORDER_URL)


@app.get("/products/{product_id}")
def get_product_by_id(product_id: int):
    return product_consumer.get_product_by_id(product_id)


@app.get("/products")
def get_products():
    return product_consumer.get_products()


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    return order_consumer.get_order(order_id)
