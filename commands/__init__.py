from typing import Callable, Dict, Awaitable, List, Protocol
from store import DataStore

class Context:
    def __init__(self, db: DataStore) -> None:
        self.db = db

CommandHandler = Callable[["Context", List[bytes]], Awaitable[bytes]]
REGISTRY: Dict[bytes, CommandHandler] = {}

def command(name: str) -> Callable[[CommandHandler], CommandHandler]:
    def decorator(func: CommandHandler) -> CommandHandler:
        key = name.upper().encode('utf-8')
        REGISTRY[key] = func
        return func
    return decorator

from . import generic, strings, expiry, lists
