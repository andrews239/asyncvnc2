import pytest

from asyncvnc2 import Enc, EncList

testinit = [
    (None, [Enc.RAW], [Enc.COPY, Enc.ZLIB]),
    ([], [Enc.RAW, Enc.COPY, Enc.ZLIB], []),

    ([Enc.RAW, Enc.ZLIB], [Enc.COPY], [Enc.RAW, Enc.ZLIB]),
    ([Enc.RAW, Enc.COPY], [Enc.ZLIB], [Enc.COPY, Enc.RAW]),
    ([Enc.COPY, Enc.ZLIB], [Enc.RAW], [Enc.COPY, Enc.ZLIB]),
]


testadd = [
    ([Enc.RAW, Enc.ZLIB], [], [Enc.RAW, Enc.ZLIB]),

    ([Enc.RAW, Enc.ZLIB], Enc.RAW, [Enc.RAW, Enc.ZLIB]),
    ([Enc.RAW, Enc.ZLIB], Enc.ZLIB, [Enc.ZLIB, Enc.RAW]),
    ([Enc.RAW, Enc.ZLIB], Enc.COPY, [Enc.COPY, Enc.RAW, Enc.ZLIB]),

    ([Enc.RAW, Enc.ZLIB], [Enc.RAW], [Enc.RAW, Enc.ZLIB]),
    ([Enc.RAW, Enc.ZLIB], [Enc.ZLIB], [Enc.ZLIB, Enc.RAW]),
    ([Enc.RAW, Enc.ZLIB], [Enc.COPY], [Enc.COPY, Enc.RAW, Enc.ZLIB]),

    ([Enc.RAW, Enc.ZLIB], [Enc.RAW, Enc.ZLIB], [Enc.RAW, Enc.ZLIB]),
    ([Enc.RAW, Enc.ZLIB], [Enc.ZLIB, Enc.RAW], [Enc.ZLIB, Enc.RAW]),
    ([Enc.RAW, Enc.ZLIB], [Enc.COPY, Enc.RAW], [Enc.COPY, Enc.RAW, Enc.ZLIB]),
    ([Enc.RAW, Enc.ZLIB], [Enc.COPY, Enc.ZLIB], [Enc.COPY, Enc.ZLIB, Enc.RAW]),
    ([Enc.RAW, Enc.ZLIB], [Enc.COPY, Enc.RAW, Enc.ZLIB], [Enc.COPY, Enc.RAW, Enc.ZLIB]),
    ([Enc.RAW, Enc.ZLIB], [Enc.COPY, Enc.ZLIB, Enc.RAW], [Enc.COPY, Enc.ZLIB, Enc.RAW]),

]

testsub = [
    ([Enc.RAW, Enc.ZLIB], [], [Enc.RAW, Enc.ZLIB]),

    ([Enc.RAW, Enc.ZLIB], Enc.RAW, [Enc.ZLIB]),
    ([Enc.RAW, Enc.ZLIB], Enc.ZLIB, [Enc.RAW]),
    ([Enc.RAW, Enc.ZLIB], Enc.COPY, [Enc.RAW, Enc.ZLIB]),

    ([Enc.RAW, Enc.ZLIB], [Enc.RAW], [Enc.ZLIB]),
    ([Enc.RAW, Enc.ZLIB], [Enc.ZLIB], [Enc.RAW]),
    ([Enc.RAW, Enc.ZLIB], [Enc.COPY], [Enc.RAW, Enc.ZLIB]),

    ([Enc.RAW, Enc.ZLIB], [Enc.RAW, Enc.ZLIB], []),
    ([Enc.RAW, Enc.ZLIB], [Enc.ZLIB, Enc.RAW], []),
    ([Enc.RAW, Enc.ZLIB], [Enc.COPY, Enc.RAW], [Enc.ZLIB]),
    ([Enc.RAW, Enc.ZLIB], [Enc.COPY, Enc.ZLIB], [Enc.RAW]),
    ([Enc.RAW, Enc.ZLIB], [Enc.COPY, Enc.RAW, Enc.ZLIB], []),
    ([Enc.RAW, Enc.ZLIB], [Enc.COPY, Enc.ZLIB, Enc.RAW], []),

    ([Enc.RAW, Enc.ZLIB, Enc.COPY], [], [Enc.RAW, Enc.ZLIB, Enc.COPY]),

    ([Enc.RAW, Enc.ZLIB, Enc.COPY], Enc.RAW, [Enc.ZLIB, Enc.COPY]),
    ([Enc.RAW, Enc.ZLIB, Enc.COPY], Enc.ZLIB, [Enc.RAW, Enc.COPY]),
    ([Enc.RAW, Enc.ZLIB, Enc.COPY], Enc.COPY, [Enc.RAW, Enc.ZLIB]),

    ([Enc.RAW, Enc.ZLIB, Enc.COPY], [Enc.RAW], [Enc.ZLIB, Enc.COPY]),
    ([Enc.RAW, Enc.ZLIB, Enc.COPY], [Enc.ZLIB], [Enc.RAW, Enc.COPY]),
    ([Enc.RAW, Enc.ZLIB, Enc.COPY], [Enc.COPY], [Enc.RAW, Enc.ZLIB]),

    ([Enc.RAW, Enc.ZLIB, Enc.COPY], [Enc.RAW, Enc.ZLIB], [Enc.COPY]),
    ([Enc.RAW, Enc.ZLIB, Enc.COPY], [Enc.ZLIB, Enc.RAW], [Enc.COPY]),
    ([Enc.RAW, Enc.ZLIB, Enc.COPY], [Enc.COPY, Enc.RAW], [Enc.ZLIB]),
    ([Enc.RAW, Enc.ZLIB, Enc.COPY], [Enc.COPY, Enc.ZLIB], [Enc.RAW]),
    ([Enc.RAW, Enc.ZLIB, Enc.COPY], [Enc.COPY, Enc.RAW, Enc.ZLIB], []),
    ([Enc.RAW, Enc.ZLIB, Enc.COPY], [Enc.COPY, Enc.ZLIB, Enc.RAW], []),



]

def _to_str(val):
    if val is None:
        return "None"
    if type(val) is list:
        brackets = "[{}]"
    else:
        brackets = "{}"
        val = [val]
    r = ",".join(map(lambda x: x.name, val))
    return brackets.format(r)


@pytest.mark.parametrize("init,unexpected,expected", testinit, ids=_to_str)
def test_init(init, unexpected, expected):
    if init is None:
        a = EncList()
    else:
        a = EncList(init)
    for x in unexpected:
        assert not x in a
    for x in expected:
        assert x in a

@pytest.mark.parametrize("init,add,expected", testadd, ids=_to_str)
def test_add(init, add, expected):
    a = EncList(init)
    b = a + add
    assert b == expected

@pytest.mark.parametrize("init,sub,expected", testsub, ids=_to_str)
def test_sub(init, sub, expected):
    a = EncList(init)
    b = a - sub
    assert b == expected
