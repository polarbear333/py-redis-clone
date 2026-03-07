from typing import List
from . import command
from handler import RESPError, serialize
from store import db
from .generic import _wrong_arity, _parse_int

@command("EXPIRE")
async def expire(args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("expire")
    try:
        return serialize(db.expire(args[0], _parse_int(args[1])))
    except ValueError:
        return serialize(RESPError("value is not an integer or out of range"))

@command("PEXPIRE")
async def pexpire(args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("pexpire")
    try:
        return serialize(db.pexpire(args[0], _parse_int(args[1])))
    except ValueError:
        return serialize(RESPError("value is not an integer or out of range"))

@command("TTL")
async def ttl(args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("ttl")
    return serialize(db.ttl(args[0]))

@command("PTTL")
async def pttl(args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("pttl")
    return serialize(db.pttl(args[0]))

@command("PERSIST")
async def persist(args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("persist")
    return serialize(db.persist(args[0]))