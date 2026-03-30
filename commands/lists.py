import asyncio
from typing import List
from . import command, Context
from handler import RESPError, serialize
from .generic import _wrong_arity, _parse_int
from store import waiters as waiter_registry

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

@command("BLPOP")
async def blpop(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) < 2:
        return _wrong_arity("blpop")
    try:
        timeout = float(args[-1])
    except ValueError:
        return serialize(RESPError("timeout is not a float or out of range"))

    keys = args[:-1]
    for key in keys:
        try:
            val = ctx.db.lpop(key)
        except ValueError:
            return serialize(RESPError(
                "WRONGTYPE Operation against a key holding the wrong kind of value"
            ))
        if val is not None:
            return serialize([key, val])
    
    loop = asyncio.get_event_loop()
    future: asyncio.Future = loop.create_future()
    for key in keys:
        waiter_registry.register(key, future)

    try:
        wait_timeout = timeout if timeout > 0 else None  # 0 means block forever
        ready_key = await asyncio.wait_for(asyncio.shield(future), timeout=wait_timeout)

    except asyncio.TimeoutError:
        for key in keys:
            waiter_registry.cancel(key, future)
        return b"*-1\r\n"  

    val = ctx.db.lpop(ready_key)

    for key in keys:
        if key != ready_key:
            waiter_registry.cancel(key, future)

    if val is None:
        return b"*-1\r\n"
    return serialize([ready_key, val])

@command("BRPOP")
async def brpop(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) < 2:
        return _wrong_arity("brpop")
    try:
        timeout = float(args[-1])
    except ValueError:
        return serialize(RESPError("timeout is not a float or out of range"))

    keys = args[:-1]
    for key in keys:
        try:
            val = ctx.db.rpop(key)
        except ValueError:
            return serialize(RESPError(
                "WRONGTYPE Operation against a key holding the wrong kind of value"
            ))
        if val is not None:
            return serialize([key, val])
    
    loop = asyncio.get_event_loop()
    future: asyncio.Future = loop.create_future()
    for key in keys:
        waiter_registry.register(key, future)

    try:
        wait_timeout = timeout if timeout > 0 else None  # 0 means block forever
        ready_key = await asyncio.wait_for(asyncio.shield(future), timeout=wait_timeout)

    except asyncio.TimeoutError:
        for key in keys:
            waiter_registry.cancel(key, future)
        return b"*-1\r\n"  

    val = ctx.db.rpop(ready_key)

    for key in keys:
        if key != ready_key:
            waiter_registry.cancel(key, future)

    if val is None:
        return b"*-1\r\n"
    return serialize([ready_key, val])