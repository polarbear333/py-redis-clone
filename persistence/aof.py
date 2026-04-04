import os
import asyncio
from typing import Callable
from handler import serialize
from handler.deserialize import deserialize, IncompleteData

class AOFWriter:
    def __init__(self, path: str, policy: str) -> None:
        self.path = path
        self.policy = policy
        self._file = open(path, "ab")
        self._lock = asyncio.Lock()
        
    async def append(self, command_list: list[bytes]) -> None:
        data = serialize(command_list)
        async with self._lock:
            self._file.write(data)                    
            if self.policy == "always":
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, os.fsync, self._file.fileno())

    async def fsync_loop(self) -> None:
        if self.policy != "everysec":
            return
        loop = asyncio.get_running_loop()
        while True:
            await asyncio.sleep(1.0)
            async with self._lock:
                self._file.flush()
                await loop.run_in_executor(None, os.fsync, self._file.fileno())

    def close(self) -> None:
        self._file.flush()
        self._file.close()

async def replay(path: str, dispatch_fn: Callable) -> int:
    if not os.path.exists(path):
        return 0
    with open(path, "rb") as f:
        raw_data = bytearray(f.read())
    count = 0
    while raw_data:
        try:
            command_list, consumed = deserialize(raw_data)
            del raw_data[:consumed]
            await dispatch_fn(command_list)   
            count += 1
        except IncompleteData:
            break
    return count