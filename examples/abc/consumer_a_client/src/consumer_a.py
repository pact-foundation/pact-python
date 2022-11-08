from typing import Optional, List

import requests
from pydantic import BaseModel


class Product(BaseModel):
    id: int
    title: str
    author: Optional[str]
    category: Optional[str]
    isbn: Optional[str]
    published: Optional[int]


class Account(BaseModel):
    id: int
    name: str
    phone: Optional[str]


class Order(BaseModel):
    id: int
    ordered: str
    shipped: Optional[str]
    product_ids: List[int]


class HubConsumer(object):
    def __init__(self, base_uri: str):
        self.base_uri = base_uri

    def get_account(self, account_id: int) -> Optional[Account]:
        uri = f"{self.base_uri}/accounts/{account_id}"
        response = requests.get(uri)
        if response.status_code == 404:
            return None

        name = response.json()["name"]
        phone = response.json()["phone"]

        return Account(id=account_id, name=name, phone=phone)

    def get_products(self) -> List[Product]:
        uri = f"{self.base_uri}/products"
        response = requests.get(uri)

        products = [Product(id=j["id"], title=j["title"]) for j in response.json()]

        return products

    def get_product(self, product_id) -> Optional[Product]:
        uri = f"{self.base_uri}/products/{product_id}"
        response = requests.get(uri)

        j = response.json()
        product = Product(
            id=j["id"],
            title=j["title"],
            author=j["author"],
            category=j["category"],
            isbn=j["isbn"],
            published=j["published"],
        )

        return product

    def get_order(self, order_id: int) -> Optional[Order]:
        uri = f"{self.base_uri}/orders/{order_id}"
        response = requests.get(uri)

        j = response.json()
        order = Order(id=j["id"], ordered=j["ordered"], shipped=j["shipped"], product_ids=j["product_ids"])

        return order
