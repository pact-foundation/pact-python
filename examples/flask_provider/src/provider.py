from flask import Flask, abort, jsonify

fakedb = {}  # Use a simple dict to represent a database

app = Flask(__name__)


@app.route("/users/<name>")
def get_user_by_name(name: str):
    """Handle requests to retrieve a single user from the simulated database.

    :param name: Name of the user to "search for"
    :return: The user data if found, None (HTTP 404) if not
    """
    user_data = fakedb.get(name)
    if not user_data:
        app.logger.debug(f"GET user for: '{name}', HTTP 404 not found")
        abort(404)
    response = jsonify(**user_data)
    app.logger.debug(f"GET user for: '{name}', returning: {response.data}")
    return response


if __name__ == "__main__":
    app.run(debug=True, port=5001)
