from subprocess import Popen, PIPE
import time
import os

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
        """
        handler
        """
        pass

    def _setup_proxy(self):
        # Create a http server (Flask), mapping root path /* to handlers
        print('====== Server START, active for ~10 seconds ======')
        directory = os.path.dirname(os.path.realpath(__file__))
        cmd = f'python {directory}/http_proxy.py >/dev/null &'
        self.flask_server = Popen(cmd.split(), stdout=PIPE)
        time.sleep(10)
        self._setup_verification_handler()

    def _do_verification(self):
        # TODO Create a http server (Flask), mapping root path /* to handlers
        pass

    def _terminate_proxy(self):

        print('====== Server SHUTDOWN down in 5 seconds ======')
        time.sleep(5)
        self.flask_server.terminate()
        # TODO Create a http server (Flask), mapping root path /* to handlers

    def verify(self):
        self._setup_proxy()

        self._do_verification()

        self._terminate_proxy()


mp = MessageProvider(message_providers='message_providers', provider_name='provider_name', consumer_name='consumer_name')
mp.verify()
