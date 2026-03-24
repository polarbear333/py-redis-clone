from typing import List
from . import command, Context
from handler import RESPError, serialize
from .generic import _wrong_arity, _parse_int

@command("EXPIRE")
async def expire(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("expire")
    try:
        return serialize(ctx.db.expire(args[0], _parse_int(args[1])))
    except ValueError:
        return serialize(RESPError("value is not an integer or out of range"))

@command("PEXPIRE")
async def pexpire(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("pexpire")
    try:
        return serialize(ctx.db.pexpire(args[0], _parse_int(args[1])))
    except ValueError:
        return serialize(RESPError("value is not an integer or out of range"))

@command("TTL")
async def ttl(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("ttl")
    return serialize(ctx.db.ttl(args[0]))

@command("PTTL")
async def pttl(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("pttl")
    return serialize(ctx.db.pttl(args[0]))

@command("PERSIST")
async def persist(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("persist")
    return serialize(ctx.db.persist(args[0]))