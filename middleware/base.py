from typing import Awaitable, Callable, List, Protocol
DispatchFn = Callable[[List[bytes]], Awaitable[bytes]]

class Middleware(Protocol):
    # protocol for all dispatch middleware.
    async def __call__(self, command_list: List[bytes],next_fn: DispatchFn) -> bytes:
        pass 