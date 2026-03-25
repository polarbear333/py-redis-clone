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