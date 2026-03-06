import pytest
from handler import serialize, RESPError

def testDeserializeSimpleString():
    assert serialize("OK") == b"+OK\r\n"

def testSerializeCrlf():
    assert serialize("line\nbreak") == b"$10\r\nline\nbreak\r\n"

def testSerializeErrObject():
    err = RESPError("oops")
    assert serialize(err) == b"-ERR oops\r\n"

def testSerializeList():
    assert serialize([1, "foo", None]) == b"*3\r\n:1\r\n+foo\r\n$-1\r\n"
