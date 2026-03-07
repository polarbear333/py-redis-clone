from typing import Any
from .deserialize import RESPError
from .constants import CRLF, NULL_BULK

def serialize(value: Any) -> bytes:
    if value is None:
        return NULL_BULK

    if isinstance(value, bool):
        return (b":1" + CRLF) if value else (b":0" + CRLF)

    if isinstance(value, int):
        return b":%d" % value + CRLF

    if isinstance(value, bytes):
        return b"$%d" % len(value) + CRLF + value + CRLF

    if isinstance(value, str):
        encoded = value.encode('utf-8')
        if "\r" not in value and "\n" not in value:
            return b"+" + encoded + CRLF
        return b"$%d" % (len(encoded),) + CRLF + encoded + CRLF
    if isinstance(value, (Exception, RESPError)):
        msg = str(value)
        return b"-" + msg.encode("utf-8") + CRLF
    
    if isinstance(value, Exception):
        raise TypeError("cannot serialize exception of type %r" % type(value).__name__)
        
    if isinstance(value, (list, tuple)):
        parts = [b"*%d" % len(value) + CRLF]
        parts.extend(serialize(item) for item in value)
        return b"".join(parts)
    raise RESPError(f"cannot serialize type {type(value).__name__!r}")