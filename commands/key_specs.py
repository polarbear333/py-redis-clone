from __future__ import annotations
from typing import Callable, Dict, List, Optional

KeyExtractor = Callable[[List[bytes]], List[bytes]]

def extract_first(args: List[bytes]) -> List[bytes]:
    return [args[0]] if args else []

def extract_all(args: List[bytes]) -> List[bytes]:
    return args

def extract_first_two(args: List[bytes]) -> List[bytes]:
    return args[:2]

def extract_object_key(args: List[bytes]) -> List[bytes]:
    return [args[1]] if len(args) >= 2 else []

def extract_interleaved(args: List[bytes]) -> List[bytes]:
    return args[::2]

def extract_all_but_last(args: List[bytes]) -> List[bytes]:
    return args[:-1] if len(args) > 1 else []

_KEY_EXTRACTORS: Dict[bytes, KeyExtractor] = {}

def _register(extractor: KeyExtractor, *commands: bytes) -> None:
    for cmd in commands:
        _KEY_EXTRACTORS[cmd] = extractor

_register(
    extract_all,
    b"DEL", b"EXISTS", b"MGET", b"WATCH", b"UNLINK", b"SUNIONSTORE", b"SINTERSTORE", b"SDIFFSTORE",
    b"ZUNIONSTORE", b"ZINTERSTORE", b"ZDIFFSTORE"
)

_register(
    extract_interleaved, b"MSET", b"MSETNX"
)

_register(extract_first, b"GETDEL", b"GETEX", b"LPOS")

_register(
    extract_first_two, b"RENAME", b"RENAMENX", b"SMOVE", b"COPY", b"LMOVE", b"BRPOPLPUSH"
)

_register(
    extract_all_but_last, b"BLPOP", b"BRPOP", b"BZPOPMIN", b"BZPOPMAX"
)

_register(extract_object_key, b"OBJECT")

_register(
    extract_first,
    b"GET", b"SET", b"INCR", b"DECR", b"INCRBY", b"DECRBY", b"APPEND", b"STRLEN", b"TYPE",
    b"EXPIRE", b"PEXPIRE", b"EXPIREAT", b"PEXPIREAT", b"TTL", b"PTTL", b"PERSIST",
    b"HSET", b"HGET", b"HGETALL", b"HDEL", b"HLEN", b"HINCRBY",
    b"SADD", b"SREM", b"SISMEMBER", b"SMEMBERS", b"SCARD",
    b"LPUSH", b"RPUSH", b"LPOP", b"RPOP", b"LRANGE", b"LLEN", b"LREM",
    b"ZADD", b"ZREM", b"ZSCORE", b"ZRANK", b"ZREVRANK", b"ZRANGE", b"ZREVRANGE", 
    b"ZRANGEBYSCORE", b"ZCOUNT", b"ZCARD"
)

def extract_sintercard(args: List[bytes]) -> List[bytes]:
    try:
        n = int(args[0])
        return list(args[1:1 + n])
    except (ValueError, IndexError):
        return []

_KEY_EXTRACTORS[b"SINTERCARD"] = extract_sintercard

_NO_KEY_COMMANDS: frozenset[bytes] = frozenset([
    b"PING", b"ECHO", b"QUIT", b"AUTH", b"SELECT",
    b"DBSIZE", b"FLUSHDB", b"FLUSHALL", b"SAVE", b"BGSAVE",
    b"BGREWRITEAOF", b"INFO", b"COMMAND", b"CONFIG",
    b"TIME", b"DEBUG", b"OBJECT", b"MULTI", b"EXEC", b"DISCARD",
    b"WAIT", b"RESET",
])

def get_keys(command_name: bytes, args: List[bytes]) -> Optional[List[bytes]]:
    cmd = command_name.upper()
    extractor = _KEY_EXTRACTORS.get(cmd)
    if extractor:
        return extractor(args)
    if cmd in _NO_KEY_COMMANDS:
        return []
    return None  

