from typing import List
from .value_types import T_SET

class SetStoreMixin:
    def _get_or_create_set(self, key: bytes) -> set:
        self._assert_type(key, T_SET)
        if self._get_or_none(key) is None:
            self._data[key] = set()
        return self._data[key]

    def sadd(self, key: bytes, *members: bytes) -> int:
        s = self._get_or_create_set(key)
        added = 0
        for member in members:
            if member not in s:
                s.add(member)
                added += 1
        return added

    def srem(self, key: bytes, *members: bytes) -> int:
        self._assert_type(key, T_SET)
        s = self._get_or_none(key)
        if s is None:
            return 0
        removed = 0
        for member in members:
            if member in s:
                s.discard(member)
                removed += 1
        if not s:
            self._delete_key(key)
        return removed

    def sismember(self, key: bytes, member: bytes) -> int:
        self._assert_type(key, T_SET)
        s = self._get_or_none(key)
        return 1 if s and member in s else 0

    def smembers(self, key: bytes) -> List[bytes]:
        self._assert_type(key, T_SET)
        s = self._get_or_none(key)
        return list(s) if s else []

    def scard(self, key: bytes) -> int:
        self._assert_type(key, T_SET)
        s = self._get_or_none(key)
        return len(s) if s else 0