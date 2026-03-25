from typing import List
from . import command, Context
from handler import RESPError, serialize
from .generic import _wrong_arity


@command("SADD")
async def sadd(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) < 2:
        return _wrong_arity("sadd")
    try:
        return serialize(ctx.db.sadd(args[0], *args[1:]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))


@command("SREM")
async def srem(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) < 2:
        return _wrong_arity("srem")
    try:
        return serialize(ctx.db.srem(args[0], *args[1:]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))


@command("SISMEMBER")
async def sismember(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 2:
        return _wrong_arity("sismember")
    try:
        return serialize(ctx.db.sismember(args[0], args[1]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))


@command("SMEMBERS")
async def smembers(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("smembers")
    try:
        return serialize(ctx.db.smembers(args[0]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))


@command("SCARD")
async def scard(ctx: Context, args: List[bytes]) -> bytes:
    if len(args) != 1:
        return _wrong_arity("scard")
    try:
        return serialize(ctx.db.scard(args[0]))
    except ValueError as exc:
        return serialize(RESPError(str(exc)))