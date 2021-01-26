"""Contract Message Provider."""
import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry
from subprocess import Popen, PIPE

from .verifier import Verifier

class MessageProvider(object):
    """
    A Pact message provider.

    provider = MessageProvider(
        message_providers = {
            "a document created successfully": handler
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
        version="3.0.0",
        proxy_host='localhost',
        proxy_port='5000'
    ):
        """Create an Message Provider instance."""
        self.message_providers = message_providers
        self.provider = provider
        self.consumer = consumer
        self.version = version
        self.pact_dir = pact_dir

        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self._process = None

    def _proxy_url(self):
        return f'http://{self.proxy_host}:{self.proxy_port}'

    def _pact_file(self):
        return f'{self.consumer}_message-{self.provider}_message.json'.lower().replace(' ', '_')

    def _setup_states(self):
        handlers = {}
        for key, handler in self.message_providers.items():
            handlers[f'{key}'] = handler()

        resp = requests.post(f'{self._proxy_url()}/setup',
                             verify=False,
                             json={"messageHandlers": handlers},)
        assert resp.status_code == 201, resp.text
        return handlers

    def _wait_for_server_start(self):
        """
        Wait for the Http Proxy to be ready.

        :rtype: None
        :raises RuntimeError: If there is a problem starting the Http Proxy.
        """
        s = requests.Session()
        retries = Retry(total=9, backoff_factor=0.5)
        http_mount = 'http://'
        s.mount(http_mount, HTTPAdapter(max_retries=retries))

        resp = s.get(f'{self._proxy_url()}/health', verify=False)
        if resp.status_code != 200:
            self._process.terminate()
            self._process.communicate()
            raise RuntimeError(
                'There was a problem starting the proxy: %s', resp.text
            )

    def _start_proxy(self):
        print('====== Start Http Proxy Server======')
        directory = os.path.dirname(os.path.realpath(__file__))
        cmd = f'python {directory}/http_proxy.py {self.proxy_port} >/dev/null &'
        self._process = Popen(cmd.split(), stdout=PIPE)
        self._wait_for_server_start()
        self._setup_states()

    def _stop_proxy(self):
        """Stop the Http Proxy.

        For some reason, I cannot stop the Flask process using with Popen process.
        The workaround is to use the endpoint to stop the application.
        """
        resp = requests.post(f'{self._proxy_url()}/shutdown', verify=False,)
        assert resp.status_code == 200, resp.text

    def verify(self):
        """Verify pact files with executable verifier."""
        verifier = Verifier(provider=self.provider,
                            provider_base_url=self._proxy_url())

        output, _ = verifier.verify_pacts(f'{self.pact_dir}/{self._pact_file()}',
                                          verbose=False)
        assert (output == 0)

    def __enter__(self):
        """
        Enter a Python context.

        Sets up the Http Proxy.
        """
        self._start_proxy()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit a Python context.

        Stop the Http Proxy.
        """
        if (exc_type, exc_val, exc_tb) != (None, None, None):
            if exc_type is not None:
                self._stop_proxy()
                return False

        self._stop_proxy()
        return True
