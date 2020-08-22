from abc import ABC
import radio.audio.clips
from typing import Optional


class Extension(ABC):
    def __init__(self, name: str, poll_interval: float = 30*60):
        self.name = name
        self.command: Optional[str] = None
        self.poll_interval = poll_interval
        self.poll_delay: float = 5*60
        self.start_delay: float = 10

    def get_clip(self) -> Optional['radio.audio.clips.Clip']:
        return None

    def time_until_next_clip(self) -> Optional[float]:
        return None
