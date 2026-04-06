import random as _random
from typing import List, Optional
from .value_types import T_NONE, type_name_for

class GenericStoreMixin:
    def exists(self, *keys: bytes) -> int:
        return sum(1 for key in keys if self._has_value(key))

    def delete(self, *keys: bytes) -> int:
        deleted = 0
        for key in keys:
            if self._has_value(key):
                self._delete_key(key)
                deleted += 1
        return deleted

    def keys(self) -> List[bytes]:
        # Rely on lazy expiry in _get_or_none; active sweep is handled by the
        # background task in server.py so this path stays O(live-keys).
        return [k for k in list(self._data.keys()) if not self._is_expired(k)]

    def type(self, key: bytes) -> str:
        value = self._get_or_none(key)
        if value is None:
            return T_NONE
        return type_name_for(value)

    def expire(self, key: bytes, seconds: int | float) -> int:
        return self._set_expiry_ms(key, int(seconds * 1000))

    def pexpire(self, key: bytes, ms: int) -> int:
        return self._set_expiry_ms(key, ms)

    def pexpireat(self, key: bytes, abs_ms: int) -> int:
        return self._set_expiry_at_ms(key, abs_ms)

    def expireat(self, key: bytes, abs_sec: int) -> int:
        return self._set_expiry_at_ms(key, abs_sec * 1000)

    def ttl(self, key: bytes) -> int:
        if not self._has_value(key):
            return -2
        expires_at = self._expiry.get(key)
        if expires_at is None:
            return -1
        return max(0, int((expires_at - self._now_ms()) / 1000))

    def pttl(self, key: bytes) -> int:
        if not self._has_value(key):
            return -2
        expires_at = self._expiry.get(key)
        if expires_at is None:
            return -1
        return max(0, int(expires_at - self._now_ms()))

    def persist(self, key: bytes) -> int:
        if not self._has_value(key) or key not in self._expiry:
            return 0
        self._clear_expiry(key)
        return 1

    def sweep_expired(self) -> int:
        with self._rw_lock:
            expired = []
            for key, exp in list(self._expiry.items()):
                if exp <= self._now_ms():
                    expired.append(key)
                    self._delete_key(key)
            return len(expired)

    def _probabilistic_expire(self, sample: int = 20) -> int:
        ## sample up to sample of keys from the expiry index and delete any that have passed their deadline.
        with self._rw_lock:
            if not self._expiry:
                return 0
            keys = _random.sample(list(self._expiry.keys()), min(sample, len(self._expiry)))
            deleted = 0
            now = self._now_ms()
            for key in keys:
                exp = self._expiry.get(key)
                if exp is not None and exp <= now:
                    self._delete_key(key)
                    deleted += 1
            return deleted

    def rename(self, key: bytes, newkey: bytes) -> None:
        with self._rw_lock:
            if not self._has_value(key):
                raise ValueError("ERR no such key")
            value = self._data[key]
            expiry = self._expiry.get(key)
            self._delete_key(newkey)
            self._data[newkey] = value
            if expiry is not None:
                self._expiry[newkey] = expiry
            self._delete_key(key)

    def renamenx(self, key: bytes, newkey: bytes) -> int:
        if not self._has_value(key):
            raise ValueError("ERR no such key")
        if self._has_value(newkey):
            return 0
        self.rename(key, newkey)
        return 1

    def randomkey(self) -> Optional[bytes]:
        ## don't sweep here and use lazy expiral instead
        live = [k for k in self._data if not self._is_expired(k)]
        if not live:
            return None
        return _random.choice(live)