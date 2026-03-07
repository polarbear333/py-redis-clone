from typing import List
from . import command
from handler import RESPError, serialize
from store import db
from .generic import _wrong_arity, _parse_int

@command("SET")
async def set_key(args: List[bytes]) -> bytes:
    if len(args) < 2:
        return _wrong_arity("set")
    db.set(args[0], args[1])
    return serialize("OK")

@command("GET")
async def get_key(args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("get")
    try:
        return serialize(db.get(args[0]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("INCR")
async def incr(args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("incr")
    try:
        return serialize(db.incr(args[0]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("DECR")
async def decr(args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("decr")
    try:
        return serialize(db.decr(args[0]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))

@command("INCRBY")
async def incrby(args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("incrby")
    try:
        increment = _parse_int(args[1])
        return serialize(db.incrby(args[0], increment))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))