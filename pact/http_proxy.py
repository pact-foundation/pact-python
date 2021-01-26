from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
import json
import logging
import sys
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

global handlers
handlers = {}

PROXY_PORT = sys.argv[1]


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def _match_states(payload):
    """
    Match state with provided message handler.
    """
    log.debug(f'Find handler from payload: {payload}')
    global handlers
    states = handlers['messageHandlers']
    log.debug(f'Setup states: {handlers}')
    provider_states = payload['providerStates']

    for state in provider_states:
        matching_state = state['name']
        if matching_state in states:
            return states[matching_state]
    raise RuntimeError('No matched handler.')

@app.route('/', methods=['POST'])
def home():
    res = jsonify(sys.argv[1])
    res.status_code = 200
    return res

@app.route('/health', methods=['GET'])
def health():
    """
    Check whether the server is available before setting up states.
    """
    res = jsonify({
        'ping': 'pong'
    })
    res.status_code = 200
    return res

@app.route("/setup", methods=['POST'])
def setup():
    """
    Setup message handers for provided states.
    """
    global handlers
    payload = request.json
    handlers = payload
    res = jsonify(payload)
    res.status_code = 201
    return res

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""

    res = e.get_response()

    res.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    res.content_type = "application/json"
    return res


if __name__ == '__main__':
    app.run(debug=True, port=PROXY_PORT)
