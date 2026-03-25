# commands/hashes.py
from typing import List
from . import command, Context
from handler import RESPError, serialize
from .generic import _wrong_arity

@command("HSET")
async def hset(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) < 3 or len(args) % 2 == 0:
        return _wrong_arity("hset")
    try:
        return serialize(ctx.db.hset(args[0], *args[1:]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("HGET")
async def hget(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("hget")
    try:
        return serialize(ctx.db.hget(args[0], args[1]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("HGETALL")
async def hgetall(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("hgetall")
    try:
        return serialize(ctx.db.hgetall(args[0]))  
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("HDEL")
async def hdel(ctx: Context, args: List[bytes]) -> bytes:  
    if len(args) < 2:
        return _wrong_arity("hdel")
    try:
        return serialize(ctx.db.hdel(args[0], *args[1:]))  
    except ValueError as exc:
        return serialize(RESPError(str(exc)))