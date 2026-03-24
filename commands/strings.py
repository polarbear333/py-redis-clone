from typing import List
from . import command, Context
from handler import RESPError, serialize
from .generic import _wrong_arity, _parse_int

@command("SET")
async def set_key(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) < 2:
        return _wrong_arity("set")
    ctx.db.set(args[0], args[1])
    return serialize("OK")

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