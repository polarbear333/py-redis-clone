from __future__ import annotations
import threading 
from typing import Dict, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from .context import ClientState

class WatchRegistry: 
    """
    Tracks which ClientState objects are watching which keys
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._watchers: Dict[bytes, Set["ClientState"]] = {}

    def watch(self, key: bytes, state: "ClientState") -> None:
        with self._lock:
            self._watchers.setdefault(key, set()).add(state)
        state.watched.add(key)
 
    def unwatch(self, state: "ClientState") -> None:
        with self._lock:
            for key in list(state.watched):
                watchers = self._watchers.get(key)
                if watchers:
                    watchers.discard(state)
                    if not watchers:
                        del self._watchers[key]
        state.clear_watch()
    
    def mark_dirty(self, key: bytes) -> None:
        with self._lock:
            watchers = self._watchers.get(key)
            if not watchers:
                return
            for state in watchers:
                state.dirty = True