import asyncio
from typing import Any, Tuple, List, Optional, Union, Callable

CRLF = b"\r\n"

class RESPError(Exception):
    pass

class IncompleteData(Exception):
    pass

## deserialization
def _find_crlf(data:bytes | bytearray, start: int = 0) -> int:
    return data.find(CRLF, start)

def _parse_simple_string(data: bytes | bytearray, pos: int) -> Tuple[str, int]:
    end = _find_crlf(data, pos)
    if end == -1: 
        raise IncompleteData()
    return data[pos:end].decode('utf-8'), end + 2

def _parse_error(data: bytes | bytearray, pos: int) -> Tuple[RESPError, int]:
    end = _find_crlf(data, pos)
    if end == -1: raise IncompleteData()
    return RESPError(data[pos:end].decode('utf-8')), end + 2

def _parse_integer(data: bytes | bytearray, pos: int) -> Tuple[RESPError, int]:
    end = _find_crlf(data, pos)
    if end == -1:
        raise IncompleteData()
    return int(data[pos:end]), end + 2

def _parse_bulk_string(data: bytes | bytearray, pos: int) -> Tuple[Optional[bytes], int]:
    end = _find_crlf(data, pos)
    if end == -1: 
        raise IncompleteData()
    
    length = int(data[pos:end])
    if length == -1:
        return None, end + 2
    body_start = end + 2
    body_end = body_start + length
    
    if body_end + 2 > len(data):
        raise IncompleteData()

    return bytes(data[body_start:body_end]), body_end + 2

def _parse_array(data: bytes | bytearray, pos: int) -> Tuple[Optional[List[Any]], int]:
    end = _find_crlf(data, pos)
    if end == -1: raise IncompleteData()
    
    count = int(data[pos:end])
    if count == -1:
        return None, end + 2

    current_pos = end + 2
    items = []
    for _ in range(count):
        item, current_pos = _parse_one(data, current_pos)
        items.append(item)
        
    return items, current_pos

PARSERS: dict[int, Callable[[Union[bytes, bytearray], int], Tuple[Any, int]]] = {
b'+'[0]: _parse_simple_string,
    b'-'[0]: _parse_error,
    b':'[0]: _parse_integer,
    b'$'[0]: _parse_bulk_string,
    b'*'[0]: _parse_array,
}

def _parse_one(data: bytes | bytearray, pos: int = 0) -> Tuple[Any, int]:
    if pos >= len(data):
        raise IncompleteData()

    prefix_byte = data[pos]
    handler = PARSERS.get(prefix_byte)
    
    if not handler:
        raise RESPError(f"unknown RESP type byte: {chr(prefix_byte)!r}")
        
    return handler(data, pos + 1)

def deserialize(data: bytes | bytearray) -> Tuple[Any, int]:
    return _parse_one(data, 0)