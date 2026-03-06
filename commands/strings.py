from typing import List
from . import command

from handler import serialize, RESPError
from store import db

@command("PING")
async def ping(args: List[bytes]) -> bytes:
    if not args:
        return serialize("PONG")  
    if len(args) == 1:
        return serialize(args[0]) 
    return serialize(RESPError("wrong number of arguments for 'ping'"))

@command("ECHO")
async def echo(args: List[bytes]) -> bytes:
    if len(args) != 1:
        return serialize(RESPError("wrong number of arguments for 'echo'"))
    return serialize(args[0])

@command("SET")
async def set_key(args: List[bytes]) -> bytes:
    if len(args) < 2:
        return serialize(RESPError("wrong number of arguments for 'set'"))
    
    key = args[0]
    value = args[1]
    db.set(key, value)
    
    return serialize("OK")

@command("GET")
async def get_key(args: List[bytes]) -> bytes:
    if len(args) != 1:
        return serialize(RESPError("wrong number of arguments for 'get'"))
    
    key = args[0]
    value = db.get(key)
    return serialize(value) 

@command("DEL")
async def del_key(args: List[bytes]) -> bytes:
    if not args:
        return serialize(RESPError("wrong number of arguments for `del`"))    
    deleted_count = 0
    for key in args:
        deleted_count += db.delete(key)
    return serialize(deleted_count)