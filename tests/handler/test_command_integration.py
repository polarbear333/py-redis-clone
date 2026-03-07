import asyncio
import pytest
from handler import serialize
from server import dispatch
from store import db

@pytest.fixture(autouse=True)
def reset_store():
    db._data.clear()
    db._expiry.clear()
    yield
    db._data.clear()
    db._expiry.clear()

@pytest.mark.asyncio
async def test_set_get_and_type():
    assert await dispatch([b"SET", b"name", b"matt"]) == serialize("OK")
    assert await dispatch([b"GET", b"name"]) == serialize(b"matt")
    assert await dispatch([b"TYPE", b"name"]) == serialize("string")

@pytest.mark.asyncio
async def test_pexpire_and_ttl_after_expiry():
    await dispatch([b"SET", b"temp", b"value"])
    assert await dispatch([b"PEXPIRE", b"temp", b"5"]) == serialize(1)
    await asyncio.sleep(0.05)  # 10× the TTL for reliable expiry
    assert await dispatch([b"TTL", b"temp"]) == serialize(-2)
    assert await dispatch([b"GET", b"temp"]) == serialize(None)

@pytest.mark.asyncio
async def test_counter_commands_and_persist():
    assert await dispatch([b"INCR", b"counter"]) == serialize(1)
    assert await dispatch([b"INCRBY", b"counter", b"4"]) == serialize(5)
    assert await dispatch([b"DECR", b"counter"]) == serialize(4)
    assert await dispatch([b"PEXPIRE", b"counter", b"100"]) == serialize(1)
    assert await dispatch([b"PERSIST", b"counter"]) == serialize(1)
    assert await dispatch([b"PTTL", b"counter"]) == serialize(-1)