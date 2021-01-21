"""Classes and methods to describe contract Consumers."""
from .message_pact import MessagePact
from .verifier import Verifier
from subprocess import Popen


class MessageProvider(object):
    """
    A Pact message provider.

    provider = MessageProvider(
        message_providers = {
            "a document created successfully": handlerfn
        },
        provider='DocumentService',
        pact_dir='pacts',
        version='3.0.0'
        
    provider.verify()
    )
    """

    def __init__(
        self,
        message_providers,
        provider_name,
        consumer_name,
        pact_dir=None,
        version="0.0.0"
    ):
        """
        Create the Message Provider class.

        """
        self.message_providers = message_providers
        self.provider_name = provider_name
        self.consumer_name = consumer_name
        self.version = version
        self.pact_dir = pact_dir


    def _setup_verification_handler(self):
        pass

    def _setup_proxy(self): 
        # Create a http server (Flask), mapping root path /* to handlers

        command = 'pact_provider.py python -m flask run -p 1235 & &>/dev/null'
        Popen([command], ..., shell=True)

        self._setup_verification_handler()
        pass

    def _do_verification(self): 
        # TODO Create a http server (Flask), mapping root path /* to handlers
        pass

    def _terminate_proxy(self): 
        # TODO Create a http server (Flask), mapping root path /* to handlers
        # server.stop();
        pass

    def verify(self):
        self._setup_proxy(self)

        self._do_verification(self)

        self._terminate_proxy(self)
