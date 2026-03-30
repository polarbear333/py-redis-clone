from typing import List
from . import command, Context
from handler import RESPError, serialize
from .generic import _wrong_arity, _parse_int

def _parse_score(raw: bytes) -> float:
    s = raw.decode().strip()
    if s in ("+inf", "inf"):
        return float("inf")
    if s == "-inf":
        return float("-inf")
    try:
        return float(s)
    except ValueError:
        raise ValueError("ERR not a float or out of range")

@command("ZADD")
async def zadd(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) < 3 or len(args[1:]) % 2 != 0:
        return _wrong_arity("zadd")
    try:
        return serialize(ctx.db.zadd(args[0], *args[1:]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("ZREM")
async def zrem(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) < 2:
        return _wrong_arity("zrem")
    try:
        return serialize(ctx.db.zrem(args[0], *args[1:]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("ZSCORE")
async def zscore(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("zscore")
    try:
        return serialize(ctx.db.zscore(args[0], args[1]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("ZRANK")
async def zrank(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("zrank")
    try:
        return serialize(ctx.db.zrank(args[0], args[1]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("ZREVRANK")
async def zrevrank(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("zrevrank")
    try:
        return serialize(ctx.db.zrevrank(args[0], args[1]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("ZRANGE")
async def zrange(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 3:
        return _wrong_arity("zrange")
    try:
        start = _parse_int(args[1])
        stop = _parse_int(args[2])
        return serialize(ctx.db.zrange(args[0], start, stop))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("ZREVRANGE")
async def zrevrange(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 3:
        return _wrong_arity("zrevrange")
    try:
        start = _parse_int(args[1])
        stop = _parse_int(args[2])
        return serialize(ctx.db.zrevrange(args[0], start, stop))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("ZRANGEBYSCORE")
async def zrangebyscore(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) < 3:
        return _wrong_arity("zrangebyscore")
    try:
        key = args[0]
        min_score = _parse_score(args[1])
        max_score = _parse_score(args[2])
        offset = 0
        count = -1

        rest = args[3:]
        i = 0
        while i < len(rest):
            token = rest[i].upper()
            if token == b"LIMIT":
                if i + 2 >= len(rest):
                    return serialize(RESPError("syntax error"))
                try:
                    offset = int(rest[i + 1])
                    count  = int(rest[i + 2])
                except ValueError:
                    return serialize(RESPError("value is not an integer or out of range"))
                i += 3
            else:
                return serialize(RESPError("syntax error"))

        return serialize(ctx.db.zrangebyscore(key, min_score, max_score, offset, count))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("ZCOUNT")
async def zcount(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 3:
        return _wrong_arity("zcount")
    try:
        min_score = _parse_score(args[1])
        max_score = _parse_score(args[2])
        return serialize(ctx.db.zcount(args[0], min_score, max_score))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("ZCARD")
async def zcard(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("zcard")
    try:
        return serialize(ctx.db.zcard(args[0]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))