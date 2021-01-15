class MessageHandler(object):
    def __init__(self, messages):
        self.messages = messages

    def get_provider_states(self):
        return self.messages[0]['providerStates'][0]['name']

    def get_metadata(self):
        return self.messages[0]['metaData']

    def get_contents(self):
        return self.messages[0]['contents']

    def get_description(self):
        return self.messages[0]['description']
