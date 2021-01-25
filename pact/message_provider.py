import requests
from subprocess import Popen, PIPE
import time
import os
from .verifier import Verifier

PACT_MOCK_HOST = 'localhost'
PACT_MOCK_PORT = 5001
PACT_URL = "http://{}:{}".format(PACT_MOCK_HOST, PACT_MOCK_PORT)
PACT_DIR = os.path.dirname(os.path.realpath(__file__))

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
        pact_dir=os.path.dirname(os.path.realpath(__file__)),
        version="3.0.0"
    ):
        """
        Create the Message Provider class.
        """
        self.message_providers = message_providers
        self.provider = provider
        self.consumer = consumer
        self.version = version
        self.pact_dir = pact_dir

    def _setup_states(self):
        handlers = {}
        for key, handler in self.message_providers.items():
            handlers[f'{key}'] = handler()

        setup_url = 'http://localhost:5001/setup'
        resp = requests.post(setup_url,
                             verify=False,
                             json={"messageHandlers": handlers},)
        assert resp.status_code == 201, resp.text
        return handlers

    def _setup_proxy(self):
        print('====== Server START, active for ~10 seconds ======')
        directory = os.path.dirname(os.path.realpath(__file__))
        cmd = f'python {directory}/http_proxy.py >/dev/null &'
        self.flask_server = Popen(cmd.split(), stdout=PIPE)
        time.sleep(10)
        self._setup_states()
        time.sleep(20)

    def _pact_file(self):
        return f'{self.consumer}_message-{self.provider}_message.json'.lower().replace(' ', '_')

    def _do_verification(self):
        verifier = Verifier(provider='UserService', provider_base_url=PACT_URL)

        output, _ = verifier.verify_pacts(f'{self.pact_dir}/{self._pact_file()}',
                                          verbose=False,
                                          provider_base_url=f"{PACT_URL}")
        assert (output == 0)

    def _terminate_proxy(self):
        print('====== Server SHUTDOWN down in 5 seconds ======')
        time.sleep(5)
        self.flask_server.terminate()

    def verify(self):
        self._setup_proxy()

        self._do_verification()

        self._terminate_proxy()
