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
import json
import logging
import warnings
from collections.abc import Callable
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import TYPE_CHECKING, Any, Generic, TypeVar
from urllib.parse import urlparse

from typing_extensions import Self

from pact import __version__
from pact.v3._util import find_free_port
from pact.v3.types import Message

if TYPE_CHECKING:
    from types import TracebackType


logger = logging.getLogger(__name__)


_C = TypeVar("_C", bound=Callable[..., Any])
_CM = TypeVar("_CM", bound=Callable[..., Message])
_CN = TypeVar("_CN", bound=Callable[..., None])


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


class MessageProducer(Generic[_CM]):
    """
    Internal message producer server.

    The Pact server is a lightweight HTTP server which translates communications
    from the underlying Pact Core library with direct Python function calls.

    The server is responsible for starting and stopping the Pact server, as well
    as handling the communication between the server and the underlying Pact
    Core library.
    """

    def __init__(
        self,
        handler: _CM,
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

        self._server: HandlerHttpServer[_CM] | None = None
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
    def path(self) -> str:
        """
        Server path.
        """
        return MessageProducerHandler.MESSAGE_PATH

    @property
    def url(self) -> str:
        """
        Server URL.
        """
        return f"http://{self.host}:{self.port}{self.path}"

    def __enter__(self) -> Self:
        """
        Enter the Pact message server context.

        This method starts the Pact server in a separate thread to handle the
        communication between the server and the underlying Pact Core library.
        """
        self._server = HandlerHttpServer(
            (self.host, self.port),
            MessageProducerHandler,
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


class MessageProducerHandler(SimpleHTTPRequestHandler, Generic[_CM]):
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
        server: HandlerHttpServer[_CM]

    MESSAGE_PATH = "/_pact/message"

    def version_string(self) -> str:
        """
        Return the server version string.

        This method is overridden to return a custom server version string.
        """
        return f"Pact Python Message Relay/{__version__}"

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
            self.send_error(404, "Not Found")
            return

        data: dict[str, Any] = json.loads(
            self.rfile.read(int(self.headers.get("Content-Length", -1)))
        )

        description: str | None = data.pop("description", None)
        if not description:
            logger.error("No description provided in message.")
            self.send_error(400, "Bad Request")
            return

        self.send_response(200, "OK")

        message = self.server.handler(description, data)

        metadata = message.get("metadata") or {}
        if content_type := message.get("content_type"):
            self.send_header("Content-Type", content_type)
            if "contentType" not in metadata:
                metadata["contentType"] = content_type

        if metadata:
            self.send_header(
                "Pact-Message-Metadata",
                base64.b64encode(json.dumps(metadata).encode()).decode(),
            )

        contents = message.get("contents", b"")
        self.send_header("Content-Length", str(len(contents)))
        self.end_headers()
        self.wfile.write(contents)

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
        self.send_error(404, "Not Found")


################################################################################
## State Handler
################################################################################


class StateCallback(Generic[_CN]):
    """
    Internal server for handling state callbacks.

    The state handler is a lightweight HTTP server which listens for state
    change requests from the underlying Pact Core library. It then calls a
    user-provided function to handle the setup/teardown of the state.
    """

    def __init__(
        self,
        handler: _CN,
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

        self._server: HandlerHttpServer[_CN] | None = None
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
        return f"http://{self.host}:{self.port}{StateCallbackHandler.CALLBACK_PATH}"

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


class StateCallbackHandler(SimpleHTTPRequestHandler, Generic[_CN]):
    """
    Request handler for the state callback server.

    See the docs of [`MessageRelayHandler`](#messagerelayhandler) for more
    information on how to handle requests.
    """

    if TYPE_CHECKING:
        server: HandlerHttpServer[_CN]

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
            self.send_error(404, "Not Found")
            return

        content_length = self.headers.get("Content-Length")
        if not content_length:
            self.send_error(400, "Bad Request")
            return
        data = json.loads(self.rfile.read(int(content_length)))

        state = data.pop("state")
        action = data.pop("action")
        params = data.pop("params")

        if state is None or action is None:
            self.send_error(400, "Bad Request")
            return

        self.server.handler(state, action, params)
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
        self.send_error(404, "Not Found")
