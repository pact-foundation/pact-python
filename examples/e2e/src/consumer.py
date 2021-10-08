from typing import Optional

import requests
from datetime import datetime


class User(object):
    def __init__(self, name: str, created_on: str):
        self.name = name
        self.created_on = created_on


class UserConsumer(object):
    def __init__(self, base_uri: str):
        self.base_uri = base_uri

    def get_user(self, user_name: str) -> Optional[User]:
        """Fetch a user object by user_name from the server.

        :param user_name: User name to search for
        :return: User details if found, None if not found
        """
        uri = self.base_uri + "/users/" + user_name
        response = requests.get(uri)
        if response.status_code == 404:
            return None

        name = response.json()["name"]
        created_on = datetime.strptime(response.json()["created_on"], "%Y-%m-%dT%H:%M:%S")

        return User(name, created_on)
