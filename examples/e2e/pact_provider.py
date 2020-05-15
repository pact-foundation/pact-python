from flask import jsonify, request

from src.provider import app, fakedb


@app.route('/_pact/provider_states', methods=['POST'])
def provider_states():
    mapping = {'UserA does not exist': setup_no_user_a,
               'UserA exists and is not an administrator':
               setup_user_a_nonadmin}
    mapping[request.json['state']]()
    return jsonify({'result': request.json['state']})


def setup_no_user_a():
    if 'UserA' in fakedb:
        del fakedb['UserA']


def setup_user_a_nonadmin():
    id = '00000000-0000-4000-a000-000000000000'
    some_date = '2016-12-15T20:16:01'
    ip_address = '198.0.0.1'

    fakedb['UserA'] = {
                        'name': "UserA",
                        'id': id,
                        'created_on': some_date,
                        'ip_address': ip_address,
                        'admin': False
                      }


if __name__ == '__main__':
    app.run(debug=True, port=5001)
