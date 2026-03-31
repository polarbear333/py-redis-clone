# store/persistence_mixin.py
from typing import Tuple, Dict, Any
from persistence import rdb

class PersistenceMixin:
    def get_snapshot(self) -> Tuple[Dict[bytes, Any], Dict[bytes, float]]:
        return self._data.copy(), self._expiry.copy()

    def save_rdb(self) -> None:
        if not self.config:
            return
        data, expiry = self.get_snapshot()
        rdb.dump(data, expiry, self.config.rdb_path)

    def load_rdb(self) -> None:
        if not self.config:
            return
        data, expiry = rdb.load(self.config.rdb_path)
        self._data.update(data)
        self._expiry.update(expiry)