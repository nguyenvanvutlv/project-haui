from dataclasses import dataclass, asdict
from models.whisper import Whisper

@dataclass
class Settings:
    width: int
    height: int
    sample_rate: int
    channels : int
    models: list
    gpu: bool = False
    fp16: bool = False
    device: str = ""
    beam_size : int = 4

    def dict(self):
        return asdict(self)


@dataclass
class Audio:
    id : int
    path: str
    sample_rate: int = 16000
    channels : int = 1
    text: str = ""

    def dict(self):
        return asdict(self)


@dataclass
class WhisperData:
    id       : int
    name     : str
    device   : str = "cuda"
    in_memory: bool = True
    objects: Whisper = None