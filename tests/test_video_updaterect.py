from io import BytesIO
from asyncvnc2 import Video
import numpy as np
import pytest


@pytest.fixture
def video():
    return Video(
        reader=None,
        writer=BytesIO(),
        decompress=lambda data: data,
        name='DESKTOP',
        width=11,
        height=22,
        mode='rgba')


def test_rect(video):
    video.data = np.zeros((50, 50, 4), 'B')
    test = np.zeros((50, 50, 4), 'B')

    video._update_rect(5, 15, 5, 15, np.ndarray((10, 10, 4), 'B', b'\377\377\377\377'*100))
    test[5:15, 5:15, :] = np.ndarray((10, 10, 4), 'B', b'\377\377\377\377'*100)

    video._update_rect(15, 25, 15, 25, np.ndarray((10, 10, 3), 'B', b'\377\000\000'*100))
    test[15:25, 15:25, :] = np.ndarray((10, 10, 4), 'B', b'\377\000\000\377'*100)

    video._update_rect(25, 35, 25, 35, np.ndarray((1, 1, 4), 'B', b'\000\377\000\000'))
    test[25:35, 25:35, :] = np.ndarray((10, 10, 4), 'B', b'\000\377\000\377'*100)

    video._update_rect(35, 45, 35, 45, np.ndarray((1, 1, 3), 'B', b'\000\000\377'))
    test[35:45, 35:45, :] = np.ndarray((10, 10, 4), 'B', b'\000\000\377\377'*100)

    assert (test == video.data).all()
