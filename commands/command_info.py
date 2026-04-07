from __future__ import annotations
from handler import serialize, RESPError
from . import command, Context, REGISTRY


def _command_entry(name_bytes: bytes):
    # [name, arity, flags, first_key, last_key, step]
    return [name_bytes.lower(), -1, [], 0, 0, 0]

@command("COMMAND")
async def cmd_command(ctx: Context, args: list) -> bytes:
    if not args:
        entries = [_command_entry(name) for name in REGISTRY]
        return serialize(entries)

    sub = args[0].upper()
    if sub == b"COUNT":
        return serialize(len(REGISTRY))

    if sub == b"INFO":
        if len(args) < 2:
            return serialize(RESPError("ERR wrong number of arguments for 'COMMAND|INFO' command"))
        result = []
        for raw_name in args[1:]:
            key = raw_name.upper()
            if key in REGISTRY:
                result.append(_command_entry(key))
            else:
                result.append(None)  
        return serialize(result)

    if sub == b"DOCS":
        # stub: return an empty map.
        return serialize([])

    if sub == b"GETKEYS":
        # stub
        return serialize([])

    if sub == b"LIST":
        names = [name.lower() for name in REGISTRY]
        return serialize(names)

    return serialize(
        RESPError(f"ERR unknown subcommand '{sub.decode()}'. Try COMMAND HELP.")
    )