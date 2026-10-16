"""
URL type returned by Pact servers.
"""

from __future__ import annotations

from functools import cached_property
from urllib.parse import SplitResult, quote, urlsplit, urlunsplit

DEFAULT_PORTS = {"http": 80, "https": 443}

# RFC 3986 `pchar` characters, which stay unencoded in appended segments.
_PATH_SAFE = "/:@!$&'()*+,;="


class URL(str):
    """
    A URL which supports appending path segments with `/`.

    `URL` is a `str`, so it can be passed anywhere a string URL is accepted.
    Appending a segment returns a new `URL`:

    ```python
    srv.url / "users" / "123"
    ```

    The `scheme`, `host`, `port` and `path` attributes are parsed on first
    access.
    """

    # `cached_property` stores the parsed URL in the instance dictionary.
    __slots__ = ("__dict__",)

    @cached_property
    def _parts(self) -> SplitResult:
        return urlsplit(self)

    @property
    def scheme(self) -> str:
        """
        URL scheme, such as `http`.
        """
        return self._parts.scheme

    @property
    def host(self) -> str | None:
        """
        Lowercased host name, without brackets for IPv6 addresses.
        """
        return self._parts.hostname

    @property
    def port(self) -> int | None:
        """
        Port number.

        Defaults to 80 for `http` and 443 for `https` when the URL gives no
        port, and is `None` for other schemes.
        """
        port = self._parts.port
        if port is not None:
            return port
        return DEFAULT_PORTS.get(self._parts.scheme)

    @property
    def path(self) -> str:
        """
        URL path, `/` when empty.
        """
        return self._parts.path or "/"

    def __truediv__(self, segment: str | object) -> URL:
        """
        Append a path segment.

        The segment is percent-encoded. The query and fragment are dropped.

        Args:
            segment:
                Path segment to append. It may contain `/`, but must not start
                with one.

        Returns:
            A new URL with the segment appended.

        Raises:
            ValueError:
                If the segment starts with `/`.
        """
        if not isinstance(segment, str):
            return NotImplemented
        if segment.startswith("/"):
            msg = f"Cannot append a path starting with '/': {segment!r}"
            raise ValueError(msg)

        path = self._parts.path
        if segment:
            path = path.removesuffix("/") + "/" + quote(segment, safe=_PATH_SAFE)
        return URL(urlunsplit(self._parts._replace(path=path, query="", fragment="")))

    def __repr__(self) -> str:
        """
        Representation distinguishing a `URL` from a plain string.
        """
        return f"URL({str.__repr__(self)})"
