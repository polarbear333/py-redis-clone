import time
import pytest
from store import DataStore

def test_store_supports_generic_string_operations():
    store = DataStore()
    assert store.set(b"greeting", b"hello") is True
    assert store.get(b"greeting") == b"hello"
    assert store.exists(b"greeting", b"missing") == 1
    assert store.type(b"greeting") == "string"
    assert store.keys() == [b"greeting"]

def test_store_expiry_is_lazy_and_removes_expired_keys():
    store = DataStore()
    store.set(b"temp", b"value")
    assert store.pexpire(b"temp", 5) == 1
    time.sleep(0.01)
    assert store.get(b"temp") is None
    assert store.exists(b"temp") == 0
    assert store.ttl(b"temp") == -2
    assert store.keys() == []

def test_store_persist_clears_existing_expiry():
    store = DataStore()
    store.set(b"session", b"abc")
    assert store.pexpire(b"session", 100) == 1
    assert store.pttl(b"session") >= 0
    assert store.persist(b"session") == 1
    assert store.pttl(b"session") == -1

def test_store_incrby_and_type_assertions():
    store = DataStore()
    assert store.incrby(b"counter", 2) == 2
    assert store.decr(b"counter") == 1
    store.set(b"not-int", b"abc")
    with pytest.raises(ValueError, match="integer"):
        store.incr(b"not-int")
    store._data[b"list-key"] = [b"item"]
    with pytest.raises(ValueError, match="WRONGTYPE"):
        store.get(b"list-key")