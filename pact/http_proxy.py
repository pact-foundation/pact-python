"""Http Proxy to be used as provider url in verifier."""
from fastapi import FastAPI, status, Request, HTTPException
import uvicorn as uvicorn
import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
PROXY_PORT = 1234
UVICORN_LOGGING_LEVEL = "error"
items = {
    "states": None
}


def _match_states(payload):
    """Match states in payload against stored message handlers."""
    log.debug(f'Find handler from payload: {payload}')
    handlers = items["states"]
    states = handlers['messageHandlers']
    log.debug(f'Setup states: {handlers}')
    provider_states = payload['providerStates']

    for state in provider_states:
        matching_state = state['name']
        if matching_state in states:
            return states[matching_state]
    raise HTTPException(status_code=500, detail='No matched handler.')


@app.post("/")
async def root(request: Request):
    """Match states with provided message handlers."""
    payload = await request.json()
    message = _match_states(payload)
    return {'contents': message}


@app.get('/ping', status_code=status.HTTP_200_OK)
def ping():
    """Check whether the server is available before setting up states."""
    return {"ping": "pong"}


@app.post("/setup", status_code=status.HTTP_201_CREATED)
async def setup(request: Request):
    """Endpoint to setup states.

    Use localstack to store payload.
    """
    payload = await request.json()
    items["states"] = payload
    return items["states"]


def run_proxy():
    """Rub HTTP Proxy."""
    uvicorn.run("pact.http_proxy:app", port=PROXY_PORT, log_level=UVICORN_LOGGING_LEVEL)
