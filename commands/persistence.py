import asyncio
import time
from typing import List
from . import command, Context
from handler import serialize
from handler.deserialize import RESPError

@command("SAVE")
async def save(ctx: Context, args: List[bytes]) -> bytes:
    if args:
        return serialize(RESPError("wrong number of arguments for 'save'"))
    try:
        ctx.db.save_rdb()          
        return b"+OK\r\n"
    except Exception as exc:
        return serialize(RESPError(f"ERR {exc}"))

@command("BGSAVE")
async def bgsave(ctx: Context, args: List[bytes]) -> bytes:
    if args:
        return serialize(RESPError("wrong number of arguments for 'bgsave'"))
    loop = asyncio.get_running_loop()
    async def _do_bgsave() -> None:
        await loop.run_in_executor(None, ctx.db.save_rdb)

    asyncio.create_task(_do_bgsave())
    return b"+Background saving started\r\n"

@command("LASTSAVE")
async def lastsave(ctx: Context, args: List[bytes]) -> bytes:
    if args:
        return serialize(RESPError("wrong number of arguments for 'lastsave'"))
    return serialize(getattr(ctx.db, "_last_save", 0))

@command("BGREWRITEAOF")
async def bgrewriteaof(ctx: Context, args: List[bytes]) -> bytes:
    if args:
        return serialize(RESPError("wrong number of arguments for 'bgrewriteaof'"))
    return b"+Background append only file rewriting started\r\n"