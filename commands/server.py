from __future__ import annotations
import asyncio
from handler import serialize, RESPError
from . import command, Context

@command("INFO")
async def cmd_info(ctx: Context, args: list) -> bytes:
    section = args[0].decode() if args else ""
    if ctx.app_ctx is None:
        return serialize(b"")
    from server_info import build_info
    text = build_info(section, ctx.app_ctx)
    return serialize(text.encode())

@command("DBSIZE")
async def cmd_dbsize(ctx: Context, args: list) -> bytes:
    count = len([k for k in ctx.db._data if not ctx.db._is_expired(k)])
    return serialize(count)

@command("FLUSHDB")
async def cmd_flushdb(ctx: Context, args: list) -> bytes:
    # ASYNC variant is accepted but treated synchronously as single threaded event loop
    with ctx.db._rw_lock:
        ctx.db._data.clear()
        ctx.db._expiry.clear()
    return serialize(b"OK")

@command("FLUSHALL")
async def cmd_flushall(ctx: Context, args: list) -> bytes:
    # When multi-db is added, iterate all stores. For now same as FLUSHDB.
    with ctx.db._rw_lock:
        ctx.db._data.clear()
        ctx.db._expiry.clear()
    return serialize(b"OK")

@command("DEBUG")
async def cmd_debug(ctx: Context, args: list) -> bytes:
    if not args:
        return serialize(RESPError("ERR wrong number of arguments for 'DEBUG' command"))
    sub = args[0].upper()
    if sub == b"SLEEP":
        if len(args) < 2:
            return serialize(RESPError("ERR syntax error"))
        try:
            secs = float(args[1])
        except ValueError:
            return serialize(RESPError("ERR value is not a float or out of range"))
        await asyncio.sleep(secs)
        return serialize(b"OK")
    if sub == b"JMAP":
        return serialize(b"OK")
    return serialize(RESPError(f"ERR unknown DEBUG subcommand '{sub.decode()}'"))

@command("WAIT")
async def cmd_wait(ctx: Context, args: list) -> bytes:
    # stub: replication not implemented, return 0 replicas for now.
    return serialize(0)