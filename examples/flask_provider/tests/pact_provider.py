"""additional endpoints to facilitate provider_states"""

from flask import jsonify, request

from src.provider import app, fakedb


@app.route("/_pact/provider_states", methods=["POST"])
def provider_states():
    """Implement the "functionality" to change the state, to prepare for a test.

    When a Pact interaction is verified, it provides the "given" part of the
    description from the Consumer in the X_PACT_PROVIDER_STATES header.
    This can then be used to perform some operations on a database for example,
    so that the actual request can be performed and respond as expected.
    See: https://docs.pact.io/getting_started/provider_states

    This provider_states endpoint is deemed test only, and generally should not
    be available once deployed to an environment. It would represent both a
    potential data loss risk, as well as a security risk.

    As such, when running the Provider to test against, this is defined as the
    FLASK_APP to run, adding this additional route to the app while keeping the
    source separate.
    """
    mapping = {
        "UserA does not exist": setup_no_user_a,
        "UserA exists and is not an administrator": setup_user_a_nonadmin,
    }
    mapping[request.json["state"]]()
    return jsonify({"result": request.json["state"]})


def setup_no_user_a():
    if "UserA" in fakedb:
        del fakedb["UserA"]


def setup_user_a_nonadmin():
    id = "00000000-0000-4000-a000-000000000000"
    some_date = "2016-12-15T20:16:01"
    ip_address = "198.0.0.1"

    fakedb["UserA"] = {"name": "UserA", "id": id, "created_on": some_date, "ip_address": ip_address, "admin": False}


if __name__ == "__main__":
    app.run(debug=True, port=5001)
