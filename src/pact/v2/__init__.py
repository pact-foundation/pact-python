"""Python methods for interactive with a Pact Mock Service."""
import warnings

from pact.v2.broker import Broker
from pact.v2.consumer import Consumer
from pact.v2.matchers import EachLike, Like, SomethingLike, Term, Format
from pact.v2.message_consumer import MessageConsumer
from pact.v2.message_pact import MessagePact
from pact.v2.message_provider import MessageProvider
from pact.v2.pact import Pact
from pact.v2.provider import Provider
from pact.v2.verifier import Verifier

from pact.__version__ import __version__, __version_tuple__

warnings.warn(
    "The `pact.v2` module is deprecated.",
    stacklevel=1,
    category=DeprecationWarning,
)

__url__ = "https://github.com/pact-foundation/pact-python"
__license__ = "MIT"

__all__ = [
    '__version__',
    '__version_tuple__',
    '__url__',
    '__license__',
    'Broker',
    'Consumer',
    'EachLike',
    'Like',
    'MessageConsumer',
    'MessagePact',
    'MessageProvider',
    'Pact',
    'Provider',
    'SomethingLike',
    'Term',
    'Format',
    'Verifier',
]
