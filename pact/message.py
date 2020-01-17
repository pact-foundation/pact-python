class Message(object):

    HEADERS = {'X-Pact-Mock-Service': 'true'}

    MANDATORY_FIELDS = {'provider_state', 'description', 'metadata', 'contents'}

    def __init__(self):
        self._messages = []

    def _insert_message_if_complete(self):
        """
        Insert a new message if current message is complete.

        An interaction is complete if it has all the mandatory fields.
        If there are no interactions, a new interaction will be added.

        :rtype: None
        """
        if not self._messages:
            self._messages.append({})
        elif all(field in self._messages[0]
                 for field in self.MANDATORY_FIELDS):
            self._messages.insert(0, {})

    def given(self, provider_state):
        self._insert_message_if_complete()
        self._messages[0]['provider_state'] = provider_state
        return self

    def expects_to_receive(self, description):
        self._insert_message_if_complete()
        self._messages[0]['description'] = description
        return self

    def with_metadata(self, metadata):
        self._insert_message_if_complete()
        self._messages[0]['metadata'] = metadata
        return self

    def with_contents(self, contents):
        self._insert_message_if_complete()
        self._messages[0]['contents'] = contents
        return self
