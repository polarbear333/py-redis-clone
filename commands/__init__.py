from typing import Callable, Dict, Awaitable, List, Optional, Protocol
from store import DataStore

class Context:
    def __init__(
        self,
        db: DataStore,
        tx_state=None,
        watch_registry=None,
        dispatch: Optional[Callable[[List[bytes]], Awaitable[bytes]]] = None,
    ) -> None:
        self.db = db
        self.tx_state = tx_state        
        self.watch_registry = watch_registry  
        self.dispatch = dispatch        

CommandHandler = Callable[["Context", List[bytes]], Awaitable[bytes]]
REGISTRY: Dict[bytes, CommandHandler] = {}

def command(name: str) -> Callable[[CommandHandler], CommandHandler]:
    def decorator(func: CommandHandler) -> CommandHandler:
        key = name.upper().encode('utf-8')
        REGISTRY[key] = func
        return func
    return decorator

from . import generic, strings, expiry, lists, hashes, redis_set, zsets, persistence, transaction