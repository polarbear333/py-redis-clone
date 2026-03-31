import asyncio
from . import command, Context
from handler import serialize
from handler.deserialize import RESPError

@command("BGSAVE")
async def bgsave(ctx: Context, args: list[bytes]) -> bytes:
    if args:
        return serialize(RESPError("wrong number of arguments for 'bgsave'"))
    loop = asyncio.get_running_loop()
    asyncio.create_task(loop.run_in_executor(None, ctx.db.save_rdb))
    return b"+Background saving started\r\n"

@command("BGREWRITEAOF")
async def bgrewriteaof(ctx: Context, args: list[bytes]) -> bytes:
    if args:
        return serialize(RESPError("wrong number of arguments for 'bgrewriteaof'"))
    return b"+Background append only file rewriting started\r\n"

