import sys
from unittest import TestCase
import mock
sys.modules["radio.audio.ffmpeg_load_audio"] = mock.MagicMock()


class TestClips(TestCase):
    def test_this(self):
        print(sys.modules.keys())
