from typing import List
from middleware.base import DispatchFn
from persistence.aof import AOFWriter

WRITE_COMMANDS = frozenset({
    b"SET", b"DEL", b"EXPIRE", b"PEXPIRE", b"PERSIST", b"RENAME", b"RENAMENX",
    b"HSET", b"HDEL", b"LPUSH", b"RPUSH", b"LPOP", b"RPOP", b"LREM",
    b"SADD", b"SREM", b"ZADD", b"ZREM", b"INCR", b"DECR", b"INCRBY",
    b"DECRBY", b"APPEND", b"MSET",
})

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
        if cmd_name in WRITE_COMMANDS and not reply.startswith(b"-"):
            await self._writer.append(command_list)

        return reply