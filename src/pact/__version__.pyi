from typing_extensions import TypeAlias

__all__ = ["__version__", "__version_tuple__", "version", "version_tuple"]

VERSION_TUPLE: TypeAlias = tuple[int | str, ...]

version: str
__version__: str
__version_tuple__: VERSION_TUPLE
version_tuple: VERSION_TUPLE
