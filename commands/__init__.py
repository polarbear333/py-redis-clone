from typing import Callable, Dict, Awaitable, List, Optional, TYPE_CHECKING
from app_context import AppContext
from store import DataStore

if TYPE_CHECKING:
    from app_context import AppContext

class Context:
    def __init__(
        self,
        db: DataStore,
        tx_state=None,
        watch_registry=None,
        dispatch: Optional[Callable[[List[bytes]], Awaitable[bytes]]] = None,
        app_ctx: Optional["AppContext"] = None,
    ) -> None:
        self.db = db
        self.tx_state = tx_state        
        self.watch_registry = watch_registry  
        self.dispatch = dispatch        
        self.app_ctx = app_ctx

CommandHandler = Callable[["Context", List[bytes]], Awaitable[bytes]]
REGISTRY: Dict[bytes, CommandHandler] = {}

def command(name: str) -> Callable[[CommandHandler], CommandHandler]:
    def decorator(func: CommandHandler) -> CommandHandler:
        key = name.upper().encode('utf-8')
        REGISTRY[key] = func
        return func
    return decorator

from . import generic, strings, expiry, lists, hashes, redis_set, zsets, persistence, transaction
from . import server, object_cmd, command_info, config_cmd