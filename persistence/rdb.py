import os
import time
import msgpack
from typing import Dict, Tuple, Any
from store.sorted_set import SortedSet

# type tag constants 
_TAG_STRING = 0  
_TAG_LIST   = 1   
_TAG_HASH   = 2   
_TAG_SET    = 3   
_TAG_ZSET   = 4   

def _encode_value(value: Any) -> Any: 
    if isinstance(value, bytes):
        # strings
        return value
    if isinstance(value, list):
        # list
        return [_TAG_LIST, value]
    if isinstance(value, dict):
        # dicts 
        return [_TAG_HASH, value]
    if isinstance(value, set):
        # sets have no msgpack equivalent, so we convert to a sorted list
        return [_TAG_SET, sorted(value)]
    if isinstance(value, SortedSet):
        # stores its score mapping in _scores dict.
        pairs = [[score, member] for member, score in value._scores.items()]
        return [_TAG_ZSET, pairs]

def _decode_value(raw: Any) -> Any:
    # reconstruct a python store value from the deserialized structure

    if isinstance(raw, bytes):
        return raw

    if not (isinstance(raw, list) and len(raw) == 2):
        raise ValueError(f"Unexpected encoded value structure: {raw!r}")

    tag, payload = raw

    if tag == _TAG_LIST:
        return payload  

    if tag == _TAG_HASH:
        return {bytes(k): bytes(v) for k, v in payload.items()}

    if tag == _TAG_SET:
        return set(payload)  # reconstruct from the sorted list

    if tag == _TAG_ZSET:
        zset = SortedSet()
        for score, member in payload:
            zset.add(member, score)  
        return zset

    raise ValueError(f"Unknown type tag: {tag!r}")

def dump(data: Dict[bytes, Any], expiry: Dict[bytes, float], path: str) -> None:
    tmp_path = path + ".tmp"
    try:
        # encode all values before serializing
        encoded_data = {k: _encode_value(v) for k, v in data.items()}
        payload = {
            b"data":   encoded_data,
            b"expiry": expiry,  
        }

        with open(tmp_path, "wb") as f:
            msgpack.pack(payload, f, use_bin_type=True)
        os.replace(tmp_path, path)

    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

def load(path: str) -> Tuple[Dict[bytes, Any], Dict[bytes, float]]:
    import logging
    if not os.path.exists(path):
        return {}, {}

    try:
        with open(path, "rb") as f:
            payload = msgpack.unpack(f, raw=True)

        raw_data   = payload[b"data"]
        raw_expiry = payload[b"expiry"]

        now = time.time() * 1000
        data   = {}
        expiry = {}

        for key, encoded_value in raw_data.items():
            exp = raw_expiry.get(key)
            if exp is not None and exp <= now:
                continue
            data[key]   = _decode_value(encoded_value)
            if exp is not None:
                expiry[key] = exp

        return data, expiry

    except Exception as e:
        bak_path = path + ".bak"
        logging.warning(
            "RDB file %r is incompatible or corrupt (%s: %s). "
            "Renaming to %r and starting with an empty store.",
            path, type(e).__name__, e, bak_path,
        )
        try:
            os.replace(path, bak_path)
        except OSError:
            pass
        return {}, {}