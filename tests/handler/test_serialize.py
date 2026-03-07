import pytest
from handler import serialize, RESPError, CRLF, NULL_BULK

def testDeserializeSimpleString():
    assert serialize("OK") == b"+OK" + CRLF

def testSerializeCrlf():
    assert serialize("line\nbreak") == b"$10" + CRLF + b"line\nbreak" + CRLF

def testSerializeErrObject():
    err = RESPError("oops")
    assert serialize(err) == b"-ERR oops" + CRLF

def testSerializeList():
    assert serialize([1, "foo", None]) == b"*3" + CRLF + b":1" + CRLF + b"+foo" + CRLF + NULL_BULK
