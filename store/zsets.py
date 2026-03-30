# store/zsets.py
from typing import List, Optional
from .value_types import T_ZSET
from .sorted_set import SortedSet


class ZSetStoreMixin:

    def _get_or_create_zset(self, key: bytes) -> SortedSet:
        self._assert_type(key, T_ZSET)
        if self._get_or_none(key) is None:
            self._data[key] = SortedSet()
        return self._data[key]

    def zadd(self, key: bytes, *pairs: bytes) -> int:
        zset = self._get_or_create_zset(key)
        added = 0
        for i in range(0, len(pairs), 2):
            score = float(pairs[i])
            member = pairs[i + 1]
            if zset.add(member, score):
                added += 1
        return added

    def zrem(self, key: bytes, *members: bytes) -> int:
        self._assert_type(key, T_ZSET)
        zset = self._get_or_none(key)
        if zset is None:
            return 0
        removed = sum(1 for m in members if zset.remove(m))
        if not zset:
            self._delete_key(key)
        return removed

    def zscore(self, key: bytes, member: bytes) -> Optional[str]:
        self._assert_type(key, T_ZSET)
        zset = self._get_or_none(key)
        if zset is None:
            return None
        s = zset.score(member)
        return str(s) if s is not None else None

    def zrank(self, key: bytes, member: bytes) -> Optional[int]:
        self._assert_type(key, T_ZSET)
        zset = self._get_or_none(key)
        if zset is None:
            return None
        return zset.rank(member)

    def zrevrank(self, key: bytes, member: bytes) -> Optional[int]:
        self._assert_type(key, T_ZSET)
        zset = self._get_or_none(key)
        if zset is None:
            return None
        return zset.rev_rank(member)

    def zrange(self, key: bytes, start: int, stop: int) -> List[bytes]:
        self._assert_type(key, T_ZSET)
        zset = self._get_or_none(key)
        if zset is None:
            return []
        length = len(zset)
        if length == 0:
            return []
        if start < 0:
            start = max(0, length + start)
        if stop < 0:
            stop = length + stop
        stop = min(stop, length - 1)
        if start > stop:
            return []
        return zset.range_by_rank(start, stop)

    def zrevrange(self, key: bytes, start: int, stop: int) -> List[bytes]:
        self._assert_type(key, T_ZSET)
        zset = self._get_or_none(key)
        if zset is None:
            return []
        return zset.rev_range(start, stop)

    def zrangebyscore(
        self,
        key: bytes,
        min_score: float,
        max_score: float,
        offset: int = 0,
        count: int = -1,
    ) -> List[bytes]:
        self._assert_type(key, T_ZSET)
        zset = self._get_or_none(key)
        if zset is None:
            return []
        return zset.range_by_score(min_score, max_score, offset=offset, count=count)

    def zcount(self, key: bytes, min_score: float, max_score: float) -> int:
        self._assert_type(key, T_ZSET)
        zset = self._get_or_none(key)
        if zset is None:
            return 0
        return zset.count(min_score, max_score)

    def zcard(self, key: bytes) -> int:
        self._assert_type(key, T_ZSET)
        zset = self._get_or_none(key)
        return len(zset) if zset else 0