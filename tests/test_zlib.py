from io import BytesIO
from asyncio import StreamReader, run, IncompleteReadError
from asyncvnc import StreamZReader
from zlib import compress, decompressobj
import pytest


@pytest.fixture
def textandreader():
    text = b"""
Nv5InqATV5iLkFt5CVGEDS0XqhmStqZL
oLYBnj5CklOUoFZGzR6OgyP7swr57MWK
Ffm8ZyrMhf52NdYde8Y6P8tOk64hpGoA
o15WdpBg75YiSgWNy6f3EKWqnPzgSvFU
bVyfs2xoT5yUD1GLnX4JW3r8cM9O4JCM
tUZnva9xjLJwrxCvzWN87V78EQVHY8qW
vzXGdXb92w0dJZ7E0f6jQ2HzcBGfzzkt
haBB7pKB4IOSH5V9AQ7D6wRA3zK4Q7BE
da8lQnGPniWz3ROWqvbc4eHMI9K4ivmC
OzN5edG3iOW57xS6c9mJhQYzpWtT8SvO
"""
    ztext = compress(text)
    reader = StreamReader()
    reader._buffer.extend(bytearray(ztext))
    zreader = StreamZReader(reader, decompressobj(), len(ztext))
    return (text, zreader)

@pytest.mark.asyncio
async def test_readall(textandreader):
    text, zreader = textandreader
    assert text  == await zreader.read()

@pytest.mark.asyncio
async def test_readexactly5(textandreader):
    text, zreader = textandreader
    result = b''
    if len(text) % 5:
        result += await zreader.readexactly(len(text) % 5)
    try:
        while True:
            result += await zreader.readexactly(5)
    except IncompleteReadError as e:
        if len(e.partial):
            result += b"ErrorErrorError"
    assert text == result

@pytest.mark.asyncio
async def test_readexactlyexpect(textandreader):
    text, zreader = textandreader
    result = b''
    try:
        while True:
            result += await zreader.readexactly(len(text)+10)
            result += b"ErrorErrorError"
    except IncompleteReadError as e:
        result += e.partial
    assert text == result
