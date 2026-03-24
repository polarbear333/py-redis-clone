from typing import List, Optional
from .value_types import T_LIST
from . import waiters as waiter_registry

class ListStoreMixin:
    def lpush(self, key: bytes, *values: bytes) -> int:
        self._assert_type(key, T_LIST)
        current = self._get_or_none(key)
        
        # store list directly into _data
        if current is None: 
            current = []
            self._data[key] = current 
        
        ## inserts left to right
        for v in values:
            current.insert(0, v)
        """
        After the push is committed, wake the first sleeping client if any.
        notify() will resolve their future with the key name, causing their
        coroutine to resume and perform the actual pop.
        """
        waiter_registry.notify(key)
        return len(current)
    
    def rpush(self, key:bytes, *values: bytes) -> int:
        self._assert_type(key, T_LIST)
        current = self._get_or_none(key)

        # store list directly into _data
        if current is None: 
            current = []
            self._data[key] = current 
            
        for v in values:
            current.append(v)

        waiter_registry.notify(key)
        return len(current)
    
    def lpop(self, key:bytes, count: Optional[int] = None) -> int:
        self._assert_type(key, T_LIST)
        if count is not None and count < 0:
            raise ValueError("ERR value is out of range, must be positive")
        current = self._get_or_none(key)
        if current is None:
            return None 
        if count is None:
            val = current.pop(0)
            if not current:
                self._delete_key(key)
            return val 
        result = [current.pop(0) for _ in range(min(count, len(current)))]
        if not current:
            self._delete_key(key)
        return result 
    
    def rpop(self, key:bytes, count: Optional[int] = None) -> int:
        self._assert_type(key, T_LIST)
        if count is not None and count < 0:
            raise ValueError("ERR value is out of range, must be positive")
        current = self._get_or_none(key)
        if current is None:
            return None 
        if count is None:
            val = current.pop()
            if not current:
                self._delete_key(key)
            return val 
        result = [current.pop() for _ in range(min(count, len(current)))]
        if not current:
            self._delete_key(key)
        return result 
    
    def lrange(self, key: bytes, start: int, stop: int) -> List[bytes]:
        self._assert_type(key, T_LIST)
        current = self._get_or_none(key)
        if current is None:
            return []
        length = len(current)

        if start < 0:
            start = max(0, length + start)
        if stop < 0:
            stop = length + stop
        stop = min(stop, length - 1)
        if start > stop:
            return []
        
        return current[start:stop + 1]
    
    def llen(self, key:bytes) -> int: 
        self._assert_type(key, T_LIST)
        current = self._get_or_none(key)
        return len(current) if current else 0
    
    def lrem(self, key: bytes, count: int, value: bytes) -> int:
        self._assert_type(key, T_LIST)
        current = self._get_or_none(key)
        if current is None:
            return 0
        
        removed = 0
        if count == 0:
            before = len(current)
            current[:] = [x for x in current if x != value]
            removed = before - len(current)
        elif count > 0:
            result = []
            for x in current:
                if x == value and removed < count:
                    removed += 1
                else:
                    result.append(x)
            current[:] = result
        else:
            result = []
            limit = abs(count)
            for x in reversed(current):
                if x == value and removed < limit:
                    removed += 1
                else:
                    result.append(x)
            current[:] = list(reversed(result))

        if not current:
            self._delete_key(key)
        return removed