from asyncio import StreamReader, StreamWriter
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from itertools import product
from typing import Optional
from zlib import decompressobj

import numpy as np

from asyncvnc.utils import read_int, read_text


#: Common screen aspect ratios
screen_ratios = {Fraction(3, 2), Fraction(4, 3), Fraction(16, 10), Fraction(16, 9), Fraction(32, 9), Fraction(64, 27)}


class VideoEncoding(Enum):
    """
    Video encoding.
    """

    #: ZLib encoding
    ZLIB = 6

    #: Raw encoding
    RAW = 0


class VideoMode(Enum):
    """
    Video mode (colour channel order)
    """

    #: Blue, green, red, alpha
    BGRA = b'\x20\x18\x00\x01\x00\xff\x00\xff\x00\xff\x10\x08\x00'

    #: Red, green, blue, alpha
    RGBA = b'\x20\x18\x00\x01\x00\xff\x00\xff\x00\xff\x00\x08\x10'

    #: Alpha, red, green, blue
    ARGB = b'\x20\x18\x01\x01\x00\xff\x00\xff\x00\xff\x10\x08\x00'

    #: Alpha, blue, green, red
    ABGR = b'\x20\x18\x01\x01\x00\xff\x00\xff\x00\xff\x00\x08\x10'

    def __repr__(self) -> str:
        return '<%s.%s>' % (self.__class__.__name__, self.name)


@dataclass
class Screen:
    """
    A computer screen.
    """

    #: Horizontal position in pixels
    x: int

    #: Vertical position in pixels
    y: int

    #: Width in pixels
    width: int

    #: Height in pixels
    height: int

    @property
    def slices(self) -> tuple[slice, slice]:
        """
        Object that can be used to crop the video buffer to this screen.
        """

        return slice(self.y, self.y + self.height), slice(self.x, self.x + self.width)

    @property
    def score(self) -> float:
        """
        A measure of our confidence that this represents a real screen. For screens with standard aspect ratios, this
        is proportional to its pixel area. For non-standard aspect ratios, the score is further multiplied by the ratio
        or its reciprocal, whichever is smaller.
        """

        value = float(self.width * self.height)
        ratios = {Fraction(self.width, self.height).limit_denominator(64),
                  Fraction(self.height, self.width).limit_denominator(64)}
        if not ratios & screen_ratios:
            value *= min(ratios)
        return value


@dataclass
class Video:
    """
    Image buffer.
    """

    reader: StreamReader = field(repr=False)
    writer: StreamWriter = field(repr=False)
    decompressor: decompressobj = field(repr=False)

    #: Desktop name
    name: str

    #: Width in pixels
    width: int

    #: Height in pixels
    height: int

    #: Colour channel order
    mode: VideoMode

    #: 3D numpy array of colour data
    data: Optional[np.ndarray] = None

    @classmethod
    async def create(cls, reader: StreamReader, writer: StreamWriter):
        writer.write(b'\x01')
        width = await read_int(reader, 2)
        height = await read_int(reader, 2)
        mode = VideoMode(await reader.readexactly(13))
        await reader.readexactly(3)  # padding
        name = await read_text(reader, 'utf-8')

        writer.write(b'\x02\x00')
        writer.write(len(VideoEncoding).to_bytes(2, 'big'))
        for encoding in VideoEncoding:
            writer.write(encoding.value.to_bytes(4, 'big'))

        return cls(reader, writer, decompressobj(), name, width, height, mode)

    def refresh(self) -> None:
        """
        Sends a video buffer update request to the server.
        """

        incremental = self.data is not None
        self.writer.write(b'\x03')
        self.writer.write(incremental.to_bytes(1, 'big'))
        self.writer.write(b'\x00\x00\x00\x00')  # x, y
        self.writer.write(self.width.to_bytes(2, 'big'))
        self.writer.write(self.height.to_bytes(2, 'big'))

    async def read(self) -> None:
        x = await read_int(self.reader, 2)
        y = await read_int(self.reader, 2)
        width = await read_int(self.reader, 2)
        height = await read_int(self.reader, 2)
        encoding = VideoEncoding(await read_int(self.reader, 4))
        if encoding is VideoEncoding.RAW:
            data = await self.reader.readexactly(height * width * 4)
        elif encoding is VideoEncoding.ZLIB:
            length = await read_int(self.reader, 4)
            data = await self.reader.readexactly(length)
            data = self.decompressor.decompress(data)
        else:
            raise ValueError(encoding)
        if self.data is None:
            self.data = np.zeros((self.height, self.width, 4), 'B')
        self.data[y:y + height, x:x + width] = np.ndarray((height, width, 4), 'B', data)
        self.data[y:y + height, x:x + width, self.mode.name.index('A')] = 255

    def as_rgba(self) -> np.ndarray:
        """
        Returns the video buffer as a 3D RGBA array.
        """

        if self.data is None:
            return np.zeros((self.height, self.width, 4), 'B')
        if self.mode is VideoMode.RGBA:
            return self.data
        if self.mode is VideoMode.ABGR:
            return self.data[:, :, ::-1]
        return np.dstack((
            self.data[:, :, self.mode.name.index('R')],
            self.data[:, :, self.mode.name.index('G')],
            self.data[:, :, self.mode.name.index('B')],
            self.data[:, :, self.mode.name.index('A')]))

    def detect_screens(self) -> list[Screen]:
        """
        Detect physical screens by inspecting the alpha channel.
        """

        if self.data is None:
            return []

        mask = self.data[:, :, self.mode.name.index('A')]
        mask = np.pad(mask // 255, ((1, 1), (1, 1))).astype(np.int8)
        mask_a = mask[1:, 1:]
        mask_b = mask[1:, :-1]
        mask_c = mask[:-1, 1:]
        mask_d = mask[:-1, :-1]

        screens = []
        while True:
            # Detect corners by ANDing perpendicular pairs of differences.
            corners = product(
                np.argwhere(mask_b - mask_a & mask_c - mask_a == -1),  # top left
                np.argwhere(mask_a - mask_b & mask_d - mask_b == -1),  # top right
                np.argwhere(mask_d - mask_c & mask_a - mask_c == -1),  # bottom left
                np.argwhere(mask_c - mask_d & mask_b - mask_d == -1))  # bottom right

            # Find cases where 3 corners align, forming an  'L' shape.
            rects = set()
            for a, b, c, d in corners:
                ab = a[0] == b[0] and a[1] < b[1]  # top
                cd = c[0] == d[0] and c[1] < d[1]  # bottom
                ac = a[1] == c[1] and a[0] < c[0]  # left
                bd = b[1] == d[1] and b[0] < d[0]  # right
                if ab and ac:
                    rects.add((a[1], a[0], b[1], c[0]))
                if ab and bd:
                    rects.add((a[1], a[0], d[1], d[0]))
                if cd and ac:
                    rects.add((a[1], a[0], d[1], d[0]))
                if cd and bd:
                    rects.add((c[1], b[0], d[1], d[0]))

            # Create screen objects and sort them by their scores.
            candidates = [Screen(int(x0), int(y0), int(x1 - x0), int(y1 - y0)) for x0, y0, x1, y1 in rects]
            candidates.sort(key=lambda screen: screen.score, reverse=True)

            # Find a single fully-opaque screen
            for screen in candidates:
                if mask_a[screen.slices].all():
                    mask_a[screen.slices] = 0
                    screens.append(screen)
                    break

            # Finish up if no screens remain
            else:
                return screens
