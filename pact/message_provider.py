"""Classes and methods to describe contract Consumers."""
from .message_pact import MessagePact
from .verifier import Verifier


class MessageProvider(object):
    """
    A Pact message provider.
    TODO: update 
    """

    def __init__(
        self,
        event_generator,
        name,
        consumer_name,
        version="0.0.0",
        tags=None,
        tag_with_git_branch=False,
        download_from_broker=False,
        pact_dir=None,
        broker_base_url=None,
        broker_username=None,
        broker_password=None,
        broker_token=None,
    ):
        """
        Create the Message Provider class.

        """
        self.name = name
        self.consumer_name = consumer_name
        self.tags = tags
        self.tag_with_git_branch = tag_with_git_branch
        self.version = version
        self.pact_dir = pact_dir
        self.broker_base_url = broker_base_url
        self.broker_username = broker_username
        self.broker_password = broker_password
        self.broker_token = broker_token
        self.event_generator = event_generator

    def verify(self):
        verifier = Verifier(provider=self.name, provider_base_url=self.broker_base_url)

        # the local file should be {producer_name}-{consumer_name}.json
        output, logs = verifier.verify_pacts(f"{self.name}_message-{self.consumer_name}_message.json",
                                         verbose=False,
                                         provider_states_setup_url="{}/_pact/provider_states".format(PACT_URL))
        # Todo
        # assertEqual(event_generator(), output) ?