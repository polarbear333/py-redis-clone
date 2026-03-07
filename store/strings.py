from typing import Optional

from .value_types import T_STRING


class StringStoreMixin:
    def set(
        self,
        key: bytes,
        value: bytes,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        exists = self._has_value(key)
        if nx and exists:
            return False
        if xx and not exists:
            return False

        self._data[key] = value
        self._clear_expiry(key)

        if ex is not None:
            self.expire(key, ex)
        if px is not None:
            self.pexpire(key, px)
        return True

    def get(self, key: bytes) -> Optional[bytes]:
        self._assert_type(key, T_STRING)
        return self._get_or_none(key)

    def incr(self, key: bytes) -> int:
        return self.incrby(key, 1)

    def decr(self, key: bytes) -> int:
        return self.incrby(key, -1)

    def incrby(self, key: bytes, amount: int) -> int:
        self._assert_type(key, T_STRING)
        raw_value = self._get_or_none(key)

        try:
            current = int(raw_value) if raw_value is not None else 0
        except ValueError as exc:
            raise ValueError("ERR value is not an integer or out of range") from exc

        next_value = current + amount
        self._data[key] = str(next_value).encode("utf-8")
        return next_value