import asyncio
import pytest
from handler import RESPReader
from handler.deserialize import RESPError

def make_reader(*chunks: bytes) -> RESPReader:
    r = asyncio.StreamReader()
    for chunk in chunks:
        r.feed_data(chunk)
    r.feed_eof()
    return RESPReader(r)

@pytest.mark.asyncio
async def testReadCommandNullArray():
    with pytest.raises(RESPError):
        await make_reader(b"*-1\r\n").read_command()

@pytest.mark.asyncio
async def testReadCommandEmptyArray():
    with pytest.raises(RESPError):
        await make_reader(b"*0\r\n").read_command()

@pytest.mark.asyncio
async def testReadCommandNonBytesElements():
    with pytest.raises(RESPError):
        await make_reader(b"*2\r\n:1\r\n+OK\r\n").read_command()

@pytest.mark.asyncio
async def testReadCommandValid():
    result = await make_reader(b"*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n").read_command()
    assert result == [b"GET", b"foo"]

@pytest.mark.asyncio
async def testReadCommandPipelined():
    reader = make_reader(b"*1\r\n$4\r\nPING\r\n*1\r\n$4\r\nPING\r\n")
    assert await reader.read_command() == [b"PING"]
    assert await reader.read_command() == [b"PING"]


@pytest.mark.asyncio
async def test_read_command_chunked():
    # Data arrives in two TCP-like chunks
    result = await make_reader(b"*2\r\n$3\r\nGET", b"\r\n$3\r\nfoo\r\n").read_command()
    assert result == [b"GET", b"foo"]