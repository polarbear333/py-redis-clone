from typing import List
from . import command
from handler import RESPError, serialize
from store import db

def _wrong_arity(name: str) -> bytes:
    return serialize(RESPError(f"wrong number of arguments for '{name}'"))

def _parse_int(raw: bytes) -> int:
    return int(raw)
    
@command("PING")
async def ping(args: List[bytes]) -> bytes:
    if not args:
        return serialize("PONG")
    if len(args) == 1:
        return serialize(args[0])
    return _wrong_arity("ping")

@command("ECHO")
async def echo(args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("echo")
    return serialize(args[0])

@command("DEL")
async def del_key(args: List[bytes]) -> bytes:
    if not args:
        return _wrong_arity("del")
    return serialize(db.delete(*args))

@command("EXISTS")
async def exists(args: List[bytes]) -> bytes:
    if not args:
        return _wrong_arity("exists")
    return serialize(db.exists(*args))

@command("KEYS")
async def keys(args: List[bytes]) -> bytes:
    if len(args) > 1:
        return _wrong_arity("keys")
    return serialize(db.keys())

@command("TYPE")
async def type_cmd(args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("type")
    return serialize(db.type(args[0]))
