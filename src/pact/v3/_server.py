"""
Internal Pact server.

Pact typically communicates directly with the client/server under test over
HTTP. When testing message interactions, however, Pact abstracts away the
transport layer and instead verifies the message payload and metadata directly.

Internally, this verification process still requires some form of transport
layer to communication with the underlying Pact Core library. This is where the
Pact server comes in. It is a lightweight HTTP server which translates
communications from the underlying Pact Core library with direct Python function
calls.

In order to be able to both handle incoming requests, and verify the
interactions, the server is started in a separate thread within the same Python
process. This does have some risks, as the server is not isolated from the rest
of the Python process. This also relies on the requests being made sequentially
and not in parallel, as the server (and more specifically, the verification
process), is _not_ thread-safe.
"""

from __future__ import annotations

import base64
import binascii
import json
import logging
import warnings
from collections.abc import Callable
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import TYPE_CHECKING, Any, Generic, Self, TypeAlias, TypeVar
from urllib.parse import parse_qs, urlparse

from pact import __version__
from pact.v3._util import find_free_port

if TYPE_CHECKING:
    from types import TracebackType

logger = logging.getLogger(__name__)


_C = TypeVar("_C", bound=Callable[..., Any])


class HandlerHttpServer(ThreadingHTTPServer, Generic[_C]):
    """
    A simple HTTP server with an custom handler function.

    Both the message relay and state handler need to be instantiated with a
    user-provided function which is accessed during the handling of a request.
    As Python's lightweight HTTP server makes the underlying server instance
    accessible while processing a request, we can use this to pass the handler
    function to the request handler.
    """

    def __init__(
        self,
        *args: Any,  # noqa: ANN401
        handler: _C,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize the HTTP server.

        Args:
            handler:
                The handler function to call when a request is received.

            *args:
                Additional arguments to pass to the server. These are not used
                by this class and are passed to the superclass.

            **kwargs:
                Additional keyword arguments to pass to the server. These are
                not used by this class and are passed to the superclass.
        """
        self.handler = handler
        super().__init__(*args, **kwargs)


################################################################################
## Message Relay
################################################################################


MessageHandlerCallable: TypeAlias = Callable[
    [bytes | None, dict[str, Any] | None], bytes | None
]


class MessageRelay:
    """
    Internal message relay server.

    The Pact server is a lightweight HTTP server which translates communications
    from the underlying Pact Core library with direct Python function calls.

    The server is responsible for starting and stopping the Pact server, as well
    as handling the communication between the server and the underlying Pact
    Core library.
    """

    def __init__(
        self,
        handler: MessageHandlerCallable,
        host: str = "localhost",
        port: int | None = None,
    ) -> None:
        """
        Initialize the Pact server.

        Args:
            handler:
                The handler function to call when a request is received. It must
                accept two positional arguments:

                -   The body of the request if present as a byte string, or
                    `None`.
                -   The metadata of the request if present as a dictionary, or
                    `None`.

                The handler function must return a byte string response, or
                `None`.

            host:
                The host to run the server on.

            port:
                The port to run the server on. If not provided, a free port will
                be found.
        """
        self._host = host
        self._port = port or find_free_port()

        self._handler = handler

        self._server: HandlerHttpServer[MessageHandlerCallable] | None = None
        self._thread: Thread | None = None

    @property
    def host(self) -> str:
        """
        Server host.
        """
        return self._host

    @property
    def port(self) -> int:
        """
        Server port.
        """
        return self._port

    @property
    def url(self) -> str:
        """
        Server URL.
        """
        return f"http://{self.host}:{self.port}"

    def __enter__(self) -> Self:
        """
        Enter the Pact message server context.

        This method starts the Pact server in a separate thread to handle the
        communication between the server and the underlying Pact Core library.
        """
        self._server = HandlerHttpServer(
            (self.host, self.port),
            MessageRelayHandler,
            handler=self._handler,
        )
        self._thread = Thread(
            target=self._server.serve_forever,
            name="Pact Message Relay Server",
        )
        self._thread.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Exit the Pact message server context.
        """
        if not self._thread or not self._server:
            warnings.warn(
                "Exiting server context despite server not being started.",
                stacklevel=2,
            )
            return

        self._server.shutdown()
        self._thread.join()


class MessageRelayHandler(SimpleHTTPRequestHandler):
    """
    Request handler for the message relay server.

    The `do_GET` and `do_POST` methods allow the server to handle GET and POST
    requests. A new instance of this class is created for each request and
    attributes can be inspected to determine the request details and respond
    accordingly.

    Specifically, the request details can be found in the following attributes:

    - `self.path` contains the HTTP path of the request.
    - `self.headers` contains the HTTP headers of the request.
    - `self.rfile` is an input stream containing the body of the request.

    The response can be sent using:

    - `self.send_response(code, message)` to set the response code and message.
    - `self.send_header(header, value)` to set a response header.
    - `self.end_headers()` to end the headers.
    """

    if TYPE_CHECKING:
        server: HandlerHttpServer[MessageHandlerCallable]

    MESSAGE_PATH = "/_pact/message"

    def version_string(self) -> str:
        """
        Return the server version string.

        This method is overridden to return a custom server version string.
        """
        return f"Pact Python Message Relay/{__version__}"

    def _process(self) -> tuple[bytes | None, dict[str, str] | None]:
        """
        Process the request.

        Read the body and headers from the request and perform some common logic
        shared between GET and POST requests.

        Returns:
            body:
                The body of the request as a byte string, if present.

            metadata:
                The metadata of the request, if present.
        """
        if content_length := self.headers.get("Content-Length"):
            body = self.rfile.read(int(content_length))
        else:
            body = None

        if data := self.headers.get("Pact-Message-Metadata"):
            try:
                metadata = json.loads(base64.b64decode(data))
            except binascii.Error as err:
                msg = "Unable to base64 decode Pact metadata header."
                raise RuntimeError(msg) from err
            except json.JSONDecodeError as err:
                msg = "Unable to JSON decode Pact metadata header."
                raise RuntimeError(msg) from err
            else:
                return body, metadata

        return body, None

    def do_POST(self) -> None:  # noqa: N802
        """
        Handle a POST request.

        This method is called when a POST request is received by the server.
        """
        logger.debug(
            "Received POST request: %s",
            self.path,
            extra={"headers": self.headers},
        )
        self.close_connection = True
        if self.path != self.MESSAGE_PATH:
            self.send_response(404)
            self.end_headers()
            return

        body, metadata = self._process()
        self.send_response(200, "OK")
        self.end_headers()

        response = self.server.handler(body, metadata)
        if response:
            self.wfile.write(response)

    def do_GET(self) -> None:  # noqa: N802
        """
        Handle a GET request.

        This method is called when a GET request is received by the server.
        """
        logger.debug(
            "Received GET request: %s",
            self.path,
            extra={"headers": self.headers},
        )
        self.close_connection = True
        if self.path != self.MESSAGE_PATH:
            self.send_response(404)
            self.end_headers()
            return

        body, metadata = self._process()
        response = self.server.handler(body, metadata)
        self.send_response(200, "OK")
        self.end_headers()

        if response:
            self.wfile.write(response)


################################################################################
## State Handler
################################################################################


StateHandlerCallable: TypeAlias = Callable[[str, str, dict[str, Any] | None], None]
"""
State handler function.

It must accept three positional arguments:

-   The state name, for example "user exists"
-   The state action, which is either "setup" or "teardown"
-   The metadata of the request if present as a dictionary, or `None`. For
    example, `{"user_id": 123}`.
"""


class StateCallback:
    """
    Internal server for handlng state callbacks.

    The state handler is a lightweight HTTP server which listens for state
    change requests from the underlying Pact Core library. It then calls a
    user-provided function to handle the setup/teardown of the state.
    """

    def __init__(
        self,
        handler: StateHandlerCallable,
        host: str = "localhost",
        port: int | None = None,
    ) -> None:
        """
        Initialize the state handler.

        Args:
            handler:
                The handler function to call when a state callback is
                received.

                The

            host:
                The host to run the server on.

            port:
                The port to run the server on. If not provided, a free port will
                be found.
        """
        self._host = host
        self._port = port or find_free_port()

        self._handler = handler

        self._server: HandlerHttpServer[StateHandlerCallable] | None = None
        self._thread: Thread | None = None

    @property
    def host(self) -> str:
        """
        Server host.
        """
        return self._host

    @property
    def port(self) -> int:
        """
        Server port.
        """
        return self._port

    @property
    def url(self) -> str:
        """
        Server URL.
        """
        return f"http://{self.host}:{self.port}"

    def __enter__(self) -> Self:
        """
        Enter the state handler context.

        This method starts the Pact server in a separate thread to handle the
        communication between the server and the underlying Pact Core library.
        """
        self._server = HandlerHttpServer(
            (self.host, self.port),
            StateCallbackHandler,
            handler=self._handler,
        )
        self._thread = Thread(
            target=self._server.serve_forever,
            name="Pact Message Relay Server",
        )
        self._thread.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Exit the state handler context.
        """
        if not self._thread or not self._server:
            warnings.warn(
                "Exiting server context despite server not being started.",
                stacklevel=2,
            )
            return

        self._server.shutdown()
        self._thread.join()


class StateCallbackHandler(SimpleHTTPRequestHandler):
    """
    Request handler for the state callback server.

    See the docs of [`MessageRelayHandler`](#messagerelayhandler) for more
    information on how to handle requests.
    """

    if TYPE_CHECKING:
        server: HandlerHttpServer[StateHandlerCallable]

    CALLBACK_PATH = "/_pact/state"

    def version_string(self) -> str:
        """
        Return the server version string.

        This method is overridden to return a custom server version string.
        """
        return f"Pact Python State Callback/{__version__}"

    def do_POST(self) -> None:  # noqa: N802
        """
        Handle a POST request.

        This method is called when a POST request is received by the server.
        """
        logger.debug(
            "Received POST request: %s",
            self.path,
            extra={"headers": self.headers},
        )
        self.close_connection = True
        url = urlparse(self.path)
        if url.path != self.CALLBACK_PATH:
            self.send_response(404)
            self.end_headers()
            return

        if query := url.query:
            data: dict[str, Any] = parse_qs(query)
            # Convert single-element lists to single values
            for k, v in data.items():
                if isinstance(v, list) and len(v) == 1:
                    data[k] = v[0]

        else:
            content_length = self.headers.get("Content-Length")
            if not content_length:
                self.send_response(400, "Bad Request")
                self.end_headers()
                return
            data = json.loads(self.rfile.read(int(content_length)))

        state = data.pop("state")
        action = data.pop("action")

        if not state or not action:
            self.send_response(400, "Bad Request")
            self.end_headers()
            return

        self.server.handler(state, action, data)
        self.send_response(200, "OK")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        """
        Handle a GET request.

        This method is called when a GET request is received by the server.
        """
        logger.debug(
            "Received GET request: %s",
            self.path,
            extra={"headers": self.headers},
        )
        self.close_connection = True
        self.send_response(404)
        self.end_headers()
