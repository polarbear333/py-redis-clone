from __future__ import annotations 
from dataclasses import dataclass, field 
from typing import List, Set 

@dataclass
class ClientState: 
    # MULTI/EXEC queue
    in_multi: bool = False
    queued: List[List[bytes]] = field(default_factory=list)

    # arity error 
    has_error: bool = False
    watched: Set[bytes] = field(default_factory=set)
    dirty: bool = False

    def reset(self) -> None:
        self.in_multi = False
        self.queued.clear()
        self.has_error
        self.dirty = False
    
    def clear_watch(self) -> None:
        self.watched.clear()
        self.dirty = False 
