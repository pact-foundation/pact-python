"""Contract Message Provider."""
import os
import time
import warnings

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry
from multiprocessing import Process
from .verifier import Verifier
from .http_proxy import run_proxy

import logging
logging.getLogger("urllib3").setLevel(logging.ERROR)


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
        pact_dir=os.getcwd(),
        version="3.0.0",
        proxy_host='localhost',
        proxy_port='1234'
    ):
        """Create a Message Provider instance."""
        warnings.warn(
            "This class will be deprecated Pact Python v3 "
            "(see pact-foundation/pact-python#396)",
            PendingDeprecationWarning,
            stacklevel=2,
        )
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
        return f'{self.consumer}-{self.provider}.json'.lower().replace(' ', '_')

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

    def _wait_for_server_stop(self):
        """Wait for server to finish, or raise exception after timeout."""
        retry = 20
        while True:
            self._process.terminate()
            time.sleep(0.1)
            try:
                assert not self._process.is_alive()
                return 0
            except AssertionError:
                if retry == 0:
                    raise RuntimeError("Process timed out")
                retry -= 1

    def _start_proxy(self):
        self._process = Process(target=run_proxy, args=(), daemon=True)
        self._process.start()
        self._wait_for_server_start()
        self._setup_states()

    def _stop_proxy(self):
        """Stop the Http Proxy."""
        if isinstance(self._process, Process):
            self._wait_for_server_stop()

    def verify(self):
        """Verify pact files with executable verifier."""
        pact_files = f'{self.pact_dir}/{self._pact_file()}'
        verifier = Verifier(provider=self.provider,
                            provider_base_url=self._proxy_url())
        return_code, _ = verifier.verify_pacts(pact_files, verbose=False)
        assert (return_code == 0), f'Expected returned_code = 0, actual = {return_code}'

    def verify_with_broker(self, enable_pending=False, include_wip_pacts_since=None, **kwargs):
        """Use Broker to verify.

        Args:
            broker_username ([String]): broker username
            broker_password ([String]): broker password
            broker_url ([String]): url of broker
            enable_pending ([Boolean])
            include_wip_pacts_since ([String])
            publish_version ([String])

        """
        verifier = Verifier(provider=self.provider,
                            provider_base_url=self._proxy_url())

        return_code, _ = verifier.verify_with_broker(enable_pending, include_wip_pacts_since, **kwargs)

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
