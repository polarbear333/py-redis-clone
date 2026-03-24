import asyncio
from typing import Dict, List

_waiters: Dict[bytes, List[asyncio.Future]] = {}

def register(key: bytes, future: asyncio.Future) -> None:
    # Register a future as a waiter for the given key.
    _waiters.setdefault(key, []).append(future)

def notify(key: bytes) -> bool:
    # wake the first pending waiter for this key.
    waiters = _waiters.get(key, [])
    while waiters:
        future = waiters.pop(0) #FIFO
        
        if not future.done():
            future.set_result(key)
            if not waiters:
                del _waiters[key]
            return True
    if key in _waiters:
        del _waiters[key]
    return False

def cancel(key: bytes, future: asyncio.Future) -> None:
    # remove a specific future from a key's waiter list.
    waiters = _waiters.get(key, [])
    try:
        waiters.remove(future)
    except ValueError:
        pass
    if not waiters and key in _waiters:
        del _waiters[key]
