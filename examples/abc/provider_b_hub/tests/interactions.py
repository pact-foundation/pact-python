from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RequestArgs:
    action: str
    base: str
    path: str


@dataclass
class RequestResponsePair:
    provider_name: str
    request_args: RequestArgs
    response_status: int
    response_content_filename: str
    method_name: str
    method_args: Dict[str, Any]


# Define the various states which Consumers request of this Provider, along with the corresponding call this Provider will need to make
# This will then be used when this Provider then acts as a Consumer
HUB_TO_PROVIDER_INTERACTIONS: Dict[str, RequestResponsePair] = {
    "Some books exist": RequestResponsePair(
        provider_name="ProviderCProducts",
        request_args=RequestArgs("GET", "https://productstore", "/"),
        response_status=200,
        response_content_filename="books.json",
        method_name="get_products",
        method_args={},
    ),
    "No books exist": RequestResponsePair(
        provider_name="ProviderCProducts",
        request_args=RequestArgs("GET", "https://productstore", "/"),
        response_status=200,
        response_content_filename="empty_array.json",
        method_name="get_products",
        method_args={},
    ),
    "Some orders exist": RequestResponsePair(
        provider_name="ProviderDOrders",
        request_args=RequestArgs("GET", "https://orders", "/1"),
        response_status=200,
        response_content_filename="order.json",
        method_name="get_order",
        method_args={"order_id": 1},
    ),
}
