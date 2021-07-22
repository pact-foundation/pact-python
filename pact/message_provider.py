"""Contract Message Provider."""
import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry
from subprocess import Popen, PIPE
from .verifier import Verifier

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
        broker_username,
        broker_password,
        broker_url,
        pact_dir=os.getcwd(),
        version="3.0.0",
        proxy_host='localhost',
        proxy_port='1234'
    ):
        """Create a Message Provider instance."""
        self.message_providers = message_providers
        self.provider = provider
        self.consumer = consumer
        self.version = version
        self.pact_dir = pact_dir
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self._process = None
        self.broker_username = broker_username
        self.broker_password = broker_password 
        self.broker_url = broker_url 

    def _proxy_url(self):
        return f'http://{self.proxy_host}:{self.proxy_port}'

    def _pact_file(self):
        return f'{self.consumer}_message-{self.provider}_message.json'.lower().replace(' ', '_')

    def _setup_states(self):
        message_handlers = {}
        for key, handler in self.message_providers.items():
            message_handlers[f'{key}'] = handler()

        resp = requests.post(f'{self._proxy_url()}/setup',
                             verify=False,
                             json={"messageHandlers": message_handlers})
        assert resp.status_code == 201, resp.text
        return message_handlers

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
        resp = s.get(f'{self._proxy_url()}/ping', verify=False)
        if resp.status_code != 200:
            self._stop_proxy()
            raise RuntimeError(
                'There was a problem starting the proxy: %s', resp.text
            )

    def _start_proxy(self):
        log.info('Start Http Proxy Server')
        current_dir = os.path.dirname(os.path.realpath(__file__))
        cmd = f'python {current_dir}/http_proxy.py {self.proxy_port} >/dev/null &'
        self._process = Popen(cmd.split(), stdout=PIPE)
        self._wait_for_server_start()
        self._setup_states()

    def _stop_proxy(self):
        """Stop the Http Proxy.

        For some reason, I cannot stop the Flask process using with Popen process.
        The workaround is to use the API endpoint.
        """
        log.info('Stop Http Proxy Serve')
        resp = requests.post(f'{self._proxy_url()}/shutdown', verify=False,)
        assert resp.status_code == 200, resp.text

    def verify(self):
        """Verify pact files with executable verifier."""
        #pact_files = f'{self.pact_dir}/{self._pact_file()}'
        verifier = Verifier(provider=self.provider,
                            provider_base_url=self._proxy_url())
        #return_code, _ = verifier.verify_pacts(pact_files, verbose=False)
        return_code, _ = verifier.verify_with_broker(broker_username = self.broker_username,
                                                    broker_password = self.broker_password,
                                                    broker_url = self.broker_url,
                                                    publish_version = self.version)
        assert (return_code == 0), f'Expected returned_code = 0, actual = {return_code}'

    def __enter__(self):
        """
        Enter a Python context.

        Sets up the Http Proxy.
        """
        self._start_proxy()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit a Python context.

        Return False to cascade the exception in context manager's body.
        Otherwise it will be supressed and the test will always pass.
        """
        if (exc_type, exc_val, exc_tb) != (None, None, None):
            if exc_type is not None:
                self._stop_proxy()
                return False
        self._stop_proxy()
        return True
