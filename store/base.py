import time
from typing import Any, Dict
from .value_types import WRONG_TYPE_ERR, type_name_for

class StoreBase:
    def __init__(self) -> None:
        self._data: Dict[bytes, Any] = {}
        self._expiry: Dict[bytes, float] = {}

    def _now_ms(self) -> float:
        return time.time() * 1000

    def _is_expired(self, key: bytes) -> bool:
        expires_at = self._expiry.get(key)
        return expires_at is not None and self._now_ms() >= expires_at

    def _delete_key(self, key: bytes) -> None:
        self._data.pop(key, None)
        self._expiry.pop(key, None)

    def _get_or_none(self, key: bytes) -> Any:
        if self._is_expired(key):
            self._delete_key(key)
        return self._data.get(key)
    
    def _has_value(self, key: bytes) -> bool:
        return self._get_or_none(key) is not None

    def _clear_expiry(self, key: bytes) -> None:
        self._expiry.pop(key, None)

    def _set_expiry_ms(self, key: bytes, ttl_ms: int) -> int:
        if not self._has_value(key):
            return 0
        if ttl_ms <= 0:
            self._delete_key(key)
            return 1
        self._expiry[key] = self._now_ms() + ttl_ms
        return 1

    def _assert_type(self, key: bytes, expected_type: str) -> None:
        value = self._get_or_none(key)
        if value is None:
            return
        if type_name_for(value) != expected_type:
            raise ValueError(WRONG_TYPE_ERR)