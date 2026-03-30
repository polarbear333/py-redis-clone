import asyncio
from typing import Callable, Dict, List, Optional, Tuple
_waiters: Dict[bytes, List[Tuple[asyncio.Future, Callable]]] = {}

def register(key: bytes, future: asyncio.Future, pop_fn: Callable) -> None:
    _waiters.setdefault(key, []).append((future, pop_fn))

def notify_and_pop(key: bytes) -> bool:
    waiters = _waiters.get(key, [])
    while waiters:
        future, pop_fn = waiters.pop(0)  # FIFO

        if future.done():
            ## skip and try the next waiter if already cancelled.
            continue

        value = pop_fn(key)
        if value is None:
            ## list was drained by a concurrent non-blocking pop 
            break

        future.set_result((key, value))
        if not waiters:
            del _waiters[key]
        return True

    ## clean up the key if the waiter list is now empty.
    if key in _waiters and not _waiters[key]:
        del _waiters[key]
    return False

def cancel(key: bytes, future: asyncio.Future) -> None:
    waiters = _waiters.get(key, [])
    for i, (f, _) in enumerate(waiters):
        if f is future:
            waiters.pop(i)
            break
    if not waiters and key in _waiters:
        del _waiters[key]
