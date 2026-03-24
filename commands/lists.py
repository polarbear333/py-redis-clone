from typing import List
from . import command, Context
from handler import RESPError, serialize
from .generic import _wrong_arity, _parse_int

@command("LPUSH")
async def lpush(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) < 2:
        return _wrong_arity("lpush")
    try:
        return serialize(ctx.db.lpush(args[0], *args[1:]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("RPUSH")
async def rpush(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) < 2:
        return _wrong_arity("rpush")
    try:
        return serialize(ctx.db.rpush(args[0], *args[1:]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("LPOP")
async def lpop(ctx: Context, args: List[bytes]) -> bytes:
    if not args:
        return _wrong_arity("lpop")
    try:
        count = int(args[1]) if len(args) > 1 else None
        result = ctx.db.lpop(args[0], count)

        if result is None and count is not None:
            return b"*-1\r\n"
        return serialize(result)
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("RPOP")
async def rpop(ctx: Context, args: List[bytes]) -> bytes:
    if not args:
        return _wrong_arity("rpop")
    try:
        count = int(args[1]) if len(args) > 1 else None
        result = ctx.db.rpop(args[0], count)

        if result is None and count is not None:
            return b"*-1\r\n"
        return serialize(result)
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("LRANGE")
async def lrange(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 3:
        return _wrong_arity("lrange")
    try:
        start = _parse_int(args[1])
        stop = _parse_int(args[2])
        return serialize(ctx.db.lrange(args[0], start, stop))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("LLEN")
async def llen(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("llen")
    try:
        return serialize(ctx.db.llen(args[0]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("LREM")
async def lrem(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 3: 
        return _wrong_arity("lrem")
    try:
        key = args[0]
        count = int(args[1])
        value = args[2]
        return serialize(ctx.db.lrem(key, count, value))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))  