import pytest
import uvicorn
from fastapi import APIRouter
from pydantic import BaseModel

from src.provider_b import app, router as main_router, session

pact_router = APIRouter()

monkey_patch = None


@pytest.fixture(autouse=True)
def set_monkey_patch(monkeypatch):
    global monkey_patch
    monkey_patch = monkeypatch


class ProviderState(BaseModel):
    state: str  # noqa: E999


@pact_router.post("/_pact/provider_states")
async def provider_states(provider_state: ProviderState):
    mapping = {"Some books exist": setup_books, "No books exist": setup_no_books, "Some orders exist": setup_order_1}
    mapping[provider_state.state]()

    return {"result": mapping[provider_state.state]}


# Make sure the app includes both routers. This needs to be done after the
# declaration of the provider_states
app.include_router(main_router)
app.include_router(pact_router)


def run_server():
    uvicorn.run(app)


def get_no_books():
    return []


def get_books():
    return [
        {
            "id": 1,
            "title": "The Last Continent",
            "author": "Terry Pratchett",
            "category": "Fantasy",
            "isbn": "0385409893",
            "published": "1998",
        },
        {
            "id": 2,
            "title": "Northern Lights",
            "author": "Philip Pullman",
            "category": "Fantasy",
            "isbn": "0-590-54178-1",
            "published": "1995-07-09",
        },
    ]


def get_order_1():
    return {"id": 1, "ordered": "2021-11-01", "shipped": "2021-11-14", "product_ids": [1, 2]}


def setup_books():
    session.adapters.get("https://").register_uri("GET", "https://productstore/", json=get_books(), status_code=200)


def setup_no_books():
    session.adapters.get("https://").register_uri("GET", "https://productstore/", json=get_no_books(), status_code=200)


def setup_order_1():
    session.adapters.get("https://").register_uri("GET", "https://orders/1", json=get_order_1(), status_code=200)
