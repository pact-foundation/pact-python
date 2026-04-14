"""Version information for pact-python-cli."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pact-python-cli")
except PackageNotFoundError:
    __version__ = "unknown"

__version_tuple__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())
