from typing import List, Optional
from . import command, Context
from handler import RESPError, serialize
from .generic import _wrong_arity, _parse_int

@command("SET")
async def set_key(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) < 2:
        return _wrong_arity("set")

    key, value = args[0], args[1]
    ex: Optional[int] = None
    px: Optional[int] = None
    nx: bool = False
    xx: bool = False

    i = 2
    while i < len(args):
        opt = args[i].upper()
        if opt == b"NX":
            nx = True
            i += 1
        elif opt == b"XX":
            xx = True
            i += 1
        elif opt == b"EX":
            if i + 1 >= len(args):
                return serialize(RESPError("ERR syntax error"))
            try:
                ex = _parse_int(args[i + 1])
            except (ValueError, TypeError):
                return serialize(RESPError("ERR value is not an integer or out of range"))
            i += 2
        elif opt == b"PX":
            if i + 1 >= len(args):
                return serialize(RESPError("ERR syntax error"))
            try:
                px = _parse_int(args[i + 1])
            except (ValueError, TypeError):
                return serialize(RESPError("ERR value is not an integer or out of range"))
            i += 2
        else:
            return serialize(RESPError("ERR syntax error"))

    if nx and xx:
        return serialize(RESPError("ERR XX and NX options at the same time are not compatible"))

    result = ctx.db.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
    return serialize("OK" if result else None)

@command("GET")
async def get_key(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("get")
    try:
        return serialize(ctx.db.get(args[0]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("INCR")
async def incr(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("incr")
    try:
        return serialize(ctx.db.incr(args[0]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("DECR")
async def decr(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("decr")
    try:
        return serialize(ctx.db.decr(args[0]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("INCRBY")
async def incrby(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("incrby")
    try:
        increment = _parse_int(args[1])
        return serialize(ctx.db.incrby(args[0], increment))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("DECRBY")
async def decrby(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("decrby")
    try:
        decrement = _parse_int(args[1])
        return serialize(ctx.db.decrby(args[0], decrement))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("APPEND")
async def append_cmd(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("append")
    try:
        return serialize(ctx.db.append(args[0], args[1]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("STRLEN")
async def strlen(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("strlen")
    try:
        return serialize(ctx.db.strlen(args[0]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("MSET")
async def mset(ctx: Context, args: List[bytes]) -> bytes:
    # Must have at least one pair; total arg count must be even
    if len(args) < 2 or len(args) % 2 != 0:
        return _wrong_arity("mset")
    ctx.db.mset(*args)
    return serialize("OK")

@command("MGET")
async def mget(ctx: Context, args: List[bytes]) -> bytes:
    if not args:
        return _wrong_arity("mget")
    return serialize(ctx.db.mget(*args))