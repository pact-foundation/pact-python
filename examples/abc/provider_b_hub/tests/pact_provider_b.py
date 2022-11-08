import json

import pytest
import uvicorn
from fastapi import APIRouter
from pydantic import BaseModel

from src.provider_b import app, router as main_router, session
from .interactions import HUB_TO_PROVIDER_INTERACTIONS

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
    setup_chained_provider_mock_state(provider_state.state)


# Make sure the app includes both routers. This needs to be done after the
# declaration of the provider_states
app.include_router(main_router)
app.include_router(pact_router)


def run_server():
    uvicorn.run(app)


def setup_chained_provider_mock_state(given):
    """Define the expected interaction with a provider from the hub, mocking the response.

    :param given: "Given" string from the Consumer test
    """
    print(f"YYYYYY {given=}")
    interaction = HUB_TO_PROVIDER_INTERACTIONS[given]
    json_data = load_json(interaction.response_content_filename)
    print(f"XXXXXXX {json_data=}")
    session.adapters.get("https://").register_uri(
        interaction.request_args.action,
        f"{interaction.request_args.base}{interaction.request_args.path}",
        json=json_data,
        status_code=interaction.response_status,
    )


def load_json(filename: str):
    """Load and return the JSON contained in a file within the resources folder.

    :param filename: Filename to load, including the extension but not including any path e.g. "order.json"
    """
    with open(f"tests/resources/{filename}") as data_file:
        return json.loads(data_file.read())
