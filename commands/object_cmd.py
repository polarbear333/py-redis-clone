from __future__ import annotations
from collections import deque
from handler import serialize, RESPError
from . import command, Context

def _encoding_for(value) -> str:
    if isinstance(value, bytes):
        try:
            n = int(value)
            if -(2**63) <= n < 2**63:
                return "int"
        except (ValueError, OverflowError):
            pass
        return "embstr" if len(value) <= 44 else "raw"

    if isinstance(value, int):
        return "int"

    # Hashes: use listpack (ziplist equivalent) for small hashes, hashtable for large ones.
    if isinstance(value, dict):
        if len(value) <= 128 and all(
            isinstance(k, bytes) and len(k) <= 64 for k in value
        ):
            return "listpack"
        return "hashtable"

    # Lists: quicklist is the standard backing for Redis lists.
    if isinstance(value, list) or isinstance(value, deque):
        if len(value) <= 128 and all(
            isinstance(v, bytes) and len(v) <= 64 for v in value
        ):
            return "listpack"
        return "quicklist"

    # Sets: listpack for small sets, hashtable for larger ones.
    if isinstance(value, set):
        if len(value) <= 128 and all(
            isinstance(v, bytes) and len(v) <= 64 for v in value
        ):
            return "listpack"
        return "hashtable"

    # Sorted Sets: listpack for small zsets, skiplist for larger ones.
    type_name = type(value).__name__
    if "SortedSet" in type_name or "ZSet" in type_name:
        length = len(value) if hasattr(value, "__len__") else 0
        if length <= 128:
            return "listpack"
        return "skiplist"
        
    return "embstr"

@command("OBJECT")
async def cmd_object(ctx: Context, args: list) -> bytes:
    if not args:
        return serialize(
            RESPError(
                "ERR wrong number of arguments for 'OBJECT|HELP' command"
            )
        )
    sub = args[0].upper()
    if sub == b"ENCODING":
        if len(args) < 2:
            return serialize(RESPError("ERR syntax error"))
        key = args[1]
        value = ctx.db._get_or_none(key)
        if value is None:
            return serialize(None)
            
        return serialize(_encoding_for(value).encode())

    if sub == b"REFCOUNT":
        if len(args) < 2:
            return serialize(RESPError("ERR syntax error"))
        key = args[1]
        
        if not ctx.db._has_value(key):
            return serialize(None)
            
        # Python doesn't expose meaningful refcounts to the Redis level, return stub value.
        return serialize(1)

    if sub == b"IDLETIME":
        if len(args) < 2:
            return serialize(RESPError("ERR syntax error"))
        key = args[1]
        
        if not ctx.db._has_value(key):
            return serialize(None)
        # LRU clock not implemented; return 0.
        return serialize(0)

    if sub == b"FREQ":
        if len(args) < 2:
            return serialize(RESPError("ERR syntax error"))
        key = args[1]
        
        if not ctx.db._has_value(key):
            return serialize(None)
        # LFU counter not implemented; return 0.
        return serialize(0)

    if sub == b"HELP":
        help_lines = [
            b"OBJECT <subcommand> [<arg> [value] [opt] ...]. Subcommands are:",
            b"ENCODING <key>",
            b"    Return the kind of internal representation the Redis object stored at <key> is using.",
            b"FREQ <key>",
            b"    Return the logarithmic access frequency counter of a Redis object stored at <key>.",
            b"HELP",
            b"    Return subcommand help summary.",
            b"IDLETIME <key>",
            b"    Return the idle time of a Redis object stored at <key>.",
            b"REFCOUNT <key>",
            b"    Return the reference count of a Redis object stored at <key>.",
        ]
        return serialize(help_lines)

    return serialize(
        RESPError(f"ERR unknown subcommand or wrong number of arguments for '{sub.decode()}' command")
    )