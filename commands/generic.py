from typing import List
from . import command, Context
from handler import RESPError, serialize

def _wrong_arity(name: str) -> bytes:
    return serialize(RESPError(f"wrong number of arguments for '{name}'"))

def _parse_int(raw: bytes) -> int:
    return int(raw)

@command("PING")
async def ping(ctx: Context, args: List[bytes]) -> bytes:
    if not args:
        return serialize("PONG")
    if len(args) == 1:
        return serialize(args[0])
    return _wrong_arity("ping")

@command("ECHO")
async def echo(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("echo")
    return serialize(args[0])

@command("DEL")
async def del_key(ctx: Context, args: List[bytes]) -> bytes:
    if not args:
        return _wrong_arity("del")
    return serialize(ctx.db.delete(*args))

@command("EXISTS")
async def exists(ctx: Context, args: List[bytes]) -> bytes:
    if not args:
        return _wrong_arity("exists")
    return serialize(ctx.db.exists(*args))

@command("KEYS")
async def keys(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) > 1:
        return _wrong_arity("keys")
    return serialize(ctx.db.keys())

@command("TYPE")
async def type_cmd(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("type")
    return serialize(ctx.db.type(args[0]))

@command("RENAME")
async def rename(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("rename")
    try:
        ctx.db.rename(args[0], args[1])
        return serialize("OK")
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("RENAMENX")
async def renamenx(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("renamenx")
    try:
        return serialize(ctx.db.renamenx(args[0], args[1]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("RANDOMKEY")
async def randomkey(ctx: Context, args: List[bytes]) -> bytes:
    if args:
        return _wrong_arity("randomkey")
    return serialize(ctx.db.randomkey())