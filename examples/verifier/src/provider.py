from flask import Flask, abort, jsonify

fakedb = {}

app = Flask(__name__)


@app.route('/users/<name>')
def get_user_by_name(name):
    user_data = fakedb.get(name)
    if not user_data:
        abort(404)
    response = jsonify(**user_data)
    app.logger.debug('get user for %s returns data:\n%s', name, response.data)
    return response


if __name__ == '__main__':
    app.run(debug=True, port=5001)
