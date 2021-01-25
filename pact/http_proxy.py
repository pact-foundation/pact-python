from flask import Flask, jsonify, request

import logging
import sys
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

global handlers
handlers = {}

# log.info('Number of arguments:', len(sys.argv), 'arguments.')
# log.info('Argument List:', str(sys.argv))
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


if __name__ == '__main__':
    app.run(debug=True, port=5001)
