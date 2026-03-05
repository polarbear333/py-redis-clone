import asyncio
import deserialize, serialize
from typing import Any, List

class RESPReader: 
    def __init__(self, stream_reader: asyncio.StreamReader):
        self._reader = stream_reader
        self._buf = bytearray() # mutable buffer

    async def read_value(self) -> Any:
        while True:
            try:
                value, consumed = deserialize(self._buf)

                del self._buf[:consumed]
                return value 
            except deserialize.IncompleteData:
                chunk = await self._reader.read(4096)
                if not chunk:
                    if not self._buf:
                        raise ConnectionAbortedError("client disconnected cleanly")
                    raise ConnectionError("client disconnected mid-message")
                self._buf.extend(chunk)
    async def read_command(self) -> List[bytes]:
        value = await self.read_value()
        if not isinstance(value, list):
            raise deserialize.RESPError(f"expected Array, got {type(value).__name__}")
        return value