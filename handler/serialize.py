from typing import Any 
from deserialize import RESPError

def serialize(value: Any) -> bytes:
    if value is None:
        return b"$-1\r\n"
    
    if isinstance(value, bool):
        return b":1\r\n" if value else b":0\r\n"
        
    if isinstance(value, int):
        return b":%d\r\n" % value
        
    if isinstance(value, bytes):
        return b"$%d\r\n%s\r\n" % (len(value), value)
        
    if isinstance(value, str):
        if "\r" not in value and "\n" not in value:
            return b"+%s\r\n" % value.encode('utf-8')
        encoded = value.encode('utf-8')
        return b"$%d\r\n%s\r\n" % (len(encoded), encoded)
        
    if isinstance(value, (Exception, RESPError)):
        msg = str(value)
        if not any(msg.startswith(p) for p in ("ERR", "WRONGTYPE", "NOAUTH")):
            msg = f"ERR {msg}"
        return b"-%s\r\n" % msg.encode('utf-8')
        
    if isinstance(value, (list, tuple)):
        parts = [b"*%d\r\n" % len(value)]
        parts.extend(serialize(item) for item in value)
        return b"".join(parts)
        
    raise RESPError(f"cannot serialize type {type(value).__name__!r}")