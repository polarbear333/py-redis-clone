import asyncio
import pytest
from handler import serialize
from server import dispatch
from store import DataStore  # import the class, not the singleton

@pytest.fixture
def store():
    return DataStore()

@pytest.mark.asyncio
async def test_set_get_and_type(store):
    assert await dispatch([b"SET", b"name", b"matt"], store) == serialize("OK")
    assert await dispatch([b"GET", b"name"], store) == serialize(b"matt")
    assert await dispatch([b"TYPE", b"name"], store) == serialize("string")

@pytest.mark.asyncio
async def test_pexpire_and_ttl_after_expiry(store):
    await dispatch([b"SET", b"temp", b"value"], store)
    assert await dispatch([b"PEXPIRE", b"temp", b"5"], store) == serialize(1)
    await asyncio.sleep(0.05)
    assert await dispatch([b"TTL", b"temp"], store) == serialize(-2)
    assert await dispatch([b"GET", b"temp"], store) == serialize(None)

@pytest.mark.asyncio
async def test_counter_commands_and_persist(store):
    assert await dispatch([b"INCR", b"counter"], store) == serialize(1)
    assert await dispatch([b"INCRBY", b"counter", b"4"], store) == serialize(5)
    assert await dispatch([b"DECR", b"counter"], store) == serialize(4)
    assert await dispatch([b"PEXPIRE", b"counter", b"100"], store) == serialize(1)
    assert await dispatch([b"PERSIST", b"counter"], store) == serialize(1)
    assert await dispatch([b"PTTL", b"counter"], store) == serialize(-1)