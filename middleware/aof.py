import time
from typing import List
from middleware.base import DispatchFn
from persistence.aof import AOFWriter

WRITE_COMMANDS = frozenset({
    b"SET", b"DEL", b"EXPIRE", b"PEXPIRE", b"EXPIREAT", b"PEXPIREAT",
    b"PERSIST", b"RENAME", b"RENAMENX",
    b"HSET", b"HDEL", b"LPUSH", b"RPUSH", b"LPOP", b"RPOP", b"LREM",
    b"SADD", b"SREM", b"ZADD", b"ZREM", b"INCR", b"DECR", b"INCRBY",
    b"DECRBY", b"APPEND", b"MSET",
})

_RELATIVE_EXPIRY_CMDS = {
    b"EXPIRE":   1000,     
    b"PEXPIRE":  1,        
}
_ABSOLUTE_EXPIRY_CMDS = {
    b"EXPIREAT",  
    b"PEXPIREAT",  
}

class AOFMiddleware:
    def __init__(self, aof_writer: AOFWriter) -> None:
        self._writer = aof_writer

    async def __call__(
        self,
        command_list: List[bytes],
        next_fn: DispatchFn,
    ) -> bytes:
        reply = await next_fn(command_list)

        cmd_name = command_list[0].upper()
        if cmd_name not in WRITE_COMMANDS or reply.startswith(b"-"):
            return reply

        if cmd_name in _RELATIVE_EXPIRY_CMDS and len(command_list) == 3:
            ms_factor = _RELATIVE_EXPIRY_CMDS[cmd_name]
            try:
                offset_ms = int(command_list[2]) * ms_factor
                abs_ms = int(time.time() * 1000) + offset_ms
                aof_entry = [b"PEXPIREAT", command_list[1], str(abs_ms).encode()]
            except (ValueError, IndexError):
                aof_entry = command_list        
        else:
            aof_entry = command_list

        await self._writer.append(aof_entry)
        return reply