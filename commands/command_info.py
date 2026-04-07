from __future__ import annotations
from handler import serialize, RESPError
from . import command, Context, REGISTRY
from .key_specs import KEY_EXTRACTORS, get_keys

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
        # minimal response alternative instead of static metadata table
        if not args[1:]:
            return serialize({})   
        result = {}
        for raw_name in args[1:]:
            result[raw_name.lower()] = {}
        return serialize(result)

    if sub == b"GETKEYS":
        if len(args) < 2:
            return serialize(RESPError("ERR Invalid arguments specified"))
        target_cmd = args[1].upper()
        target_args = args[2:]
        keys = get_keys(target_cmd, target_args)
        if keys is None:
            return serialize(RESPError(
                f"ERR The command has no key arguments: '{args[1].decode()}'"
            ))
        return serialize(keys)

    if sub == b"LIST":
        names = [name.lower() for name in REGISTRY]
        return serialize(names)

    return serialize(
        RESPError(f"ERR unknown subcommand '{sub.decode()}'. Try COMMAND HELP.")
    )