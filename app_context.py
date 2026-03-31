from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from store import DataStore
from config import PersistenceConfig

if TYPE_CHECKING:
    from middleware.base import Middleware
    from persistence.aof import AOFWriter

@dataclass
class AppContext:
    store: DataStore
    config: PersistenceConfig
    middleware: List["Middleware"] = field(default_factory=list)
    aof_writer: Optional["AOFWriter"] = None

    # transaction_manager: Optional[TransactionManager] = None
    # repl_manager: Optional[ReplicationManager] = None