from typing import Dict, List, Optional

class DataStore:
    def __init__(self):
        self._data: Dict[bytes, bytes] = {}
    
    def set(self, key: bytes, value: bytes) -> None:
        self._data[key] = value
    
    def get(self, key: bytes) -> Optional[bytes]:
        return self._data.get(key)
    
    def delete(self, key: bytes) -> int:
        if key in self._data:
            del self._data[key]
            return 1
        return 0
    
    def exists(self, key: bytes) -> int:
        return 1 if key in self._data else 0
    
    def keys(self) -> List[bytes]:
        return list(self._data.keys())

db = DataStore()