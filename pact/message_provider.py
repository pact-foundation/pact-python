from subprocess import Popen, PIPE
import time
import os
import json
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
    )
    """

    def __init__(
        self,
        message_providers,
        provider,
        consumer,
        pact_dir=None,
        version="0.0.0"
    ):
        """
        Create the Message Provider class.

        """
        self.message_providers = message_providers
        self.provider = provider
        self.consumer = consumer
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

        self.current_handler = self.message_providers.get('Document delete successfully')

        directory = os.path.dirname(os.path.realpath(__file__))
        handler_str = json.dumps(self.current_handler()).replace(" ", "").replace("\'", "\"")
        cmd = f'python {directory}/http_proxy.py {handler_str} >/dev/null &'
        self.flask_server = Popen(cmd.split(), stdout=PIPE)

        time.sleep(10)

        # handler()
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
