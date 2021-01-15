class UserConsumer(object):

    def __init__(self):
        self.conversion = {
            '42': 'forty-two',
            '24': 'twenty-four',
        }

    def get_id(self, id):
        """Compare that from the message block."""
        return User(self.conversion[id])


class User(object):
    def __init__(self, name):
        self.name = name
