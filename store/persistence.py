import copy
import time
from typing import Tuple, Dict, Any
from persistence import rdb

class PersistenceMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_save: int = 0 

    def get_snapshot(self) -> Tuple[Dict[bytes, Any], Dict[bytes, float]]:
        with self._rw_lock:
            return copy.deepcopy(self._data), self._expiry.copy()

    def save_rdb(self) -> None:
        if not self.config:
            return
        data, expiry = self.get_snapshot()
        rdb.dump(data, expiry, self.config.rdb_path)
        now = int(time.time())
        self._last_save = max(now, self._last_save + 1)

    def load_rdb(self) -> None:
        if not self.config:
            return
        data, expiry = rdb.load(self.config.rdb_path)
        self._data.update(data)
        self._expiry.update(expiry)