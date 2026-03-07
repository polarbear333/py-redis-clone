import pytest
from unittest.mock import AsyncMock
from handler import serialize, RESPError
from server import dispatch, REGISTRY

@pytest.fixture(autouse=True)
def isolate_registry():
    original_registry = REGISTRY.copy()
    REGISTRY.clear()
    yield
    REGISTRY.clear()
    REGISTRY.update(original_registry)

@pytest.mark.asyncio
async def test_dispatch_unknown_command():
    result = await dispatch([b"NOTACOMMAND"])
    assert result == serialize(RESPError("unknown command 'NOTACOMMAND'"))

@pytest.mark.asyncio
async def test_dispatch_known_command():
    REGISTRY[b"PING"] = AsyncMock(return_value=serialize("PONG"))
    result = await dispatch([b"ping"])  
    assert result == serialize("PONG")

@pytest.mark.asyncio
async def test_dispatch_handler_raises():
    REGISTRY[b"BOOM"] = AsyncMock(side_effect=Exception("oops"))
    result = await dispatch([b"BOOM"])
    assert result == serialize(RESPError("internal server error"))