# store/hashes.py
from typing import List, Optional
from .value_types import T_HASH

class HashStoreMixin:
    def _get_or_create_hash(self, key: bytes) -> dict:
        self._assert_type(key, T_HASH)
        # _get_or_none (with underscore) is the correct private method from StoreBase.
        if self._get_or_none(key) is None:
            self._data[key] = {}
        return self._data[key]

    def hset(self, key: bytes, *pairs: bytes) -> int:
        h = self._get_or_create_hash(key)
        added = 0
        for i in range(0, len(pairs), 2):
            field, value = pairs[i], pairs[i + 1]
            if field not in h:
                added += 1
            h[field] = value  # actually store the value — this was the missing line
        return added

    def hget(self, key: bytes, field: bytes) -> Optional[bytes]:
        self._assert_type(key, T_HASH)
        h = self._get_or_none(key)
        return h.get(field) if h else None

    def hgetall(self, key: bytes) -> List[bytes]:
        self._assert_type(key, T_HASH)
        h = self._get_or_none(key)
        if not h:
            return []
        result = []
        for k, v in h.items():
            result.extend([k, v])
        return result

    def hdel(self, key: bytes, *fields: bytes) -> int:
        self._assert_type(key, T_HASH)
        h = self._get_or_none(key)
        if not h:
            return 0
        removed = sum(1 for f in fields if h.pop(f, None) is not None)
        if not h:
            self._delete_key(key)
        return removed