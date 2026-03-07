from typing import List

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
        self.sweep_expired()
        return list(self._data.keys())

    def type(self, key: bytes) -> str:
        value = self._get_or_none(key)
        if value is None:
            return T_NONE
        return type_name_for(value)

    def expire(self, key: bytes, seconds: int | float) -> int:
        return self._set_expiry_ms(key, int(seconds * 1000))

    def pexpire(self, key: bytes, ms: int) -> int:
        return self._set_expiry_ms(key, ms)

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
        expired_keys = [key for key in list(self._expiry) if self._is_expired(key)]
        for key in expired_keys:
            self._delete_key(key)
        return len(expired_keys)