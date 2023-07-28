"""Utils for safe handling of c code."""
def se(s=str):
    """Encode the string parameter as a buffer or encode NULL."""
    return b"NULL" if s is None or "" else s.encode("ascii")

def ne():
    """Encode a null string as a byte."""
    return b"NULL"
