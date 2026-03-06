from handler import deserialize, RESPError

def parse(data: bytes):
    return deserialize(data)[0]

def testDeserializeInteger():
    assert parse(b":123\r\n") == 123

def testDeserializeSimpleString():
    assert parse(b"+OK\r\n") == "OK"

def testDeserializeError():
    val = parse(b"-ERR boom\r\n")
    assert isinstance(val, RESPError)

def testDeserializeBulkString():
    assert parse(b"$3\r\nfoo\r\n") == b"foo"

def testDeserializeArray():
    assert parse(b"*2\r\n:1\r\n+two\r\n") == [1, "two"]
