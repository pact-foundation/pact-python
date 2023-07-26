"""Http Proxy to be used as provider url in verifier."""
from fastapi import FastAPI, Response, status, Request, HTTPException
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
async def root(request: Request, response: Response):
    """Match states with provided message handlers."""
    payload = await request.json()
    message = _match_states(payload)
    # TODO:- Read message metadata from request, parse as json
    # and base64 encode - the example below is {"Content-Type": "application/json"}
    # https://github.com/pact-foundation/pact-reference/tree/master/rust/pact_verifier_cli#verifying-metadata
    response.headers["Pact-Message-Metadata"] = "eyJDb250ZW50LVR5cGUiOiAiYXBwbGljYXRpb24vanNvbiJ9Cg=="
    return message


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
