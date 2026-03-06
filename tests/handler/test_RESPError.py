import pytest, asyncio
from handler import RESPReader
from handler.deserialize import RESPError

@pytest.mark.asyncio
async def test_read_command_null_array():
    r = asyncio.StreamReader()
    r.feed_data(b"*-1\r\n")
    r.feed_eof()
    reader = RESPReader(r)
    with pytest.raises(RESPError):
        await reader.read_command()

@pytest.mark.asyncio
async def test_read_command_non_bytes():
    r = asyncio.StreamReader()
    r.feed_data(b"*2\r\n:1\r\n+OK\r\n")
    r.feed_eof()
    reader = RESPReader(r)
    with pytest.raises(RESPError):
        await reader.read_command()