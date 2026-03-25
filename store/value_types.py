from typing import Any
from .sorted_set import SortedSet

T_STRING = "string"
T_LIST = "list"
T_HASH = "hash"
T_SET = "set"
T_ZSET = "zset"
T_NONE = "none"

WRONG_TYPE_ERR = "WRONGTYPE Operation against a key holding the wrong kind of value"


def type_name_for(value: Any) -> str:
    if isinstance(value, bytes):
        return T_STRING
    if isinstance(value, list):
        return T_LIST
    if isinstance(value, dict):
        return T_HASH
    if isinstance(value, set):
        return T_SET
    if isinstance(value, SortedSet):
        return T_ZSET
    return T_NONE