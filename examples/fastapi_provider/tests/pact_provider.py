import uvicorn

from fastapi import APIRouter
from pydantic import BaseModel

from src.provider import app, fakedb, router as main_router

pact_router = APIRouter()


class ProviderState(BaseModel):
    state: str  # noqa: E999


@pact_router.post("/_pact/provider_states")
async def provider_states(provider_state: ProviderState):
    mapping = {
        "UserA does not exist": setup_no_user_a,
        "UserA exists and is not an administrator": setup_user_a_nonadmin,
    }
    mapping[provider_state.state]()

    return {"result": mapping[provider_state.state]}


# Make sure the app includes both routers. This needs to be done after the
# declaration of the provider_states
app.include_router(main_router)
app.include_router(pact_router)


def run_server():
    uvicorn.run(app)


def setup_no_user_a():
    if "UserA" in fakedb:
        del fakedb["UserA"]


def setup_user_a_nonadmin():
    id = "00000000-0000-4000-a000-000000000000"
    some_date = "2016-12-15T20:16:01"
    ip_address = "198.0.0.1"

    fakedb["UserA"] = {"name": "UserA", "id": id, "created_on": some_date, "ip_address": ip_address, "admin": False}
