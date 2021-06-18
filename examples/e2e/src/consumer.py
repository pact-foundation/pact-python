import requests
from datetime import datetime


class UserConsumer(object):
    def __init__(self, base_uri):
        self.base_uri = base_uri

    def get_user(self, user_name):
        """Fetch a user object by user_name from the server."""
        uri = self.base_uri + '/users/' + user_name
        response = requests.get(uri)
        if response.status_code == 404:
            return None

        name = response.json()['name']
        created_on = datetime.strptime(response.json()['created_on'], '%Y-%m-%dT%H:%M:%S')

        return User(name, created_on)


class User(object):
    def __init__(self, name, created_on):
        self.name = name
        self.created_on = created_on
