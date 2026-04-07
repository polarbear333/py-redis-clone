from typing import List
from middleware.base import DispatchFn
from transaction import ClientState, WatchRegistry

_ALWAYS_EXEC = frozenset({
    b"MULTI", b"EXEC", b"DISCARD", b"WATCH", b"UNWATCH",
})

class TransactionMiddleware:
    def __init__(self, tx_state: ClientState, watch_registry: WatchRegistry) -> None:
        self._tx = tx_state
        self._registry = watch_registry
 
    async def __call__(self, command_list: List[bytes], next_fn: DispatchFn) -> bytes:
        if not self._tx.in_multi:
            return await next_fn(command_list)
 
        cmd_name = command_list[0].upper()
        if cmd_name in _ALWAYS_EXEC:
            return await next_fn(command_list)
        self._tx.queued.append(command_list)
        return b"+QUEUED\r\n"