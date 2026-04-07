from typing import List
from . import command, Context
from handler import serialize, RESPError
from .generic import _wrong_arity

@command("MULTI")
async def multi(ctx: Context, args: List[bytes]) -> bytes:
    if args:
        return _wrong_arity("multi")
    if ctx.tx_state.in_multi:
        return serialize(RESPError("ERR MULTI calls can not be nested"))
    ctx.tx_state.in_multi = True
    return b"+OK\r\n"

@command("DISCARD")
async def discard(ctx: Context, args: List[bytes]) -> bytes:
    if args:
        return _wrong_arity("discard")
    if not ctx.tx_state.in_multi:
        return serialize(RESPError("ERR DISCARD without MULTI"))
    ctx.tx_state.reset()
    ctx.tx_state.clear_watch()
    if ctx.watch_registry:
        ctx.watch_registry.unwatch(ctx.tx_state)
    return b"+OK\r\n"

@command("EXEC")
async def exec_cmd(ctx: Context, args: List[bytes]) -> bytes:
    if args:
        return _wrong_arity("exec")
    if not ctx.tx_state.in_multi:
        return serialize(RESPError("ERR EXEC without MULTI"))

    # syntax error in EXEC
    if ctx.tx_state.has_error:
        ctx.tx_state.reset()
        if ctx.watch_registry:
            ctx.watch_registry.unwatch(ctx.tx_state)
        return serialize(RESPError(
            "EXECABORT Transaction discarded because of previous errors."
        ))

    # transaction aborted if a watched key was mutated
    if ctx.tx_state.dirty:
        ctx.tx_state.reset()
        if ctx.watch_registry:
            ctx.watch_registry.unwatch(ctx.tx_state)
        return b"*-1\r\n"

    queued = list(ctx.tx_state.queued)
    ctx.tx_state.reset()
    if ctx.watch_registry:
        ctx.watch_registry.unwatch(ctx.tx_state)

    replies: List[bytes] = []
    for command_list in queued:
        reply = await ctx.dispatch(command_list)
        replies.append(reply)

    header = f"*{len(replies)}\r\n".encode()
    return header + b"".join(replies)

@command("WATCH")
async def watch(ctx: Context, args: List[bytes]) -> bytes:
    if not args:
        return _wrong_arity("watch")
    if ctx.tx_state.in_multi:
        return serialize(RESPError("ERR WATCH inside MULTI is not allowed"))
    if ctx.watch_registry:
        for key in args:
            ctx.watch_registry.watch(key, ctx.tx_state)
    return b"+OK\r\n"

@command("UNWATCH")
async def unwatch(ctx: Context, args: List[bytes]) -> bytes:
    if args:
        return _wrong_arity("unwatch")
    if ctx.watch_registry:
        ctx.watch_registry.unwatch(ctx.tx_state)
    return b"+OK\r\n"