from io import BytesIO
from asyncio import StreamReader, IncompleteReadError
from asyncvnc2 import _rle_len
import pytest

def _reader(txt):
    reader = StreamReader()
    reader._buffer.extend(bytearray(txt))
    return reader

text = [ ( "1..255", b"\000\001\010\376", [1,   2,   9, 255]),
         ( "256..510", b"\377\000\377\001\377\010\377\376", [256, 257, 264, 510]),
         ( "511..765", b"\377\377\000\377\377\001\377\377\010\377\377\376", [511, 512, 519, 765])
       ]

def _to_str(val):
    if isinstance(val, str):
        return val
    else:
        return "-"

@pytest.mark.parametrize("id,data,decoded", text, ids=_to_str)
@pytest.mark.asyncio
async def test_init(id, data, decoded):
    reader = _reader(data)
    for length in decoded:
        assert length == await _rle_len(reader)

