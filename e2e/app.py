import json

from flask import Flask, Response, request
from werkzeug.datastructures import Headers

HTTP_METHODS = ['DELETE', 'GET', 'OPTIONS', 'POST', 'PUT']

app = Flask(__name__)
current_state = ''

provider_states = {
    'consumer': {
        'a simple json blob exists': Response(
            status=200,
            response=json.dumps({'name': 'Jonas'}),
            headers=Headers([('Content-Type', 'application/json')])),
        'the user `bob` exists': Response(
            status=200,
            headers={'Content-Type': 'application/json'},
            response=json.dumps(
                {'username': 'bob',
                 'id': '100',
                 'groups': ['users', 'admins']})),
        'a list of users exists': Response(
            status=200,
            headers={'Content-Type': 'application/json'},
            response=json.dumps({'results': [
                {'username': 'bob', 'id': 101, 'groups': [234, 123]},
                {'username': 'sue', 'id': 102, 'groups': [345, 123]}]}))
    }}


@app.route('/_pact/provider-states', methods=['GET'])
def states():
    return json.dumps({k: v.keys() for k, v in provider_states.items()})


@app.route('/_pact/provider-states/active', methods=['POST'])
def set_active():
    body = request.get_json()
    global current_state
    current_state = provider_states[body['consumer']][body['state']]

    return Response(status=200)


@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
def catch_all(path):
    return current_state


if __name__ == '__main__':
    app.run(port='5000')
