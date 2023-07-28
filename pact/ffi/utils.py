import json

def se(s):
    return b"NULL" if s is None or "" else s.encode("ascii")

def ne():
    return b"NULL"
