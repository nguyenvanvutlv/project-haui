from dataclasses import dataclass, asdict

@dataclass
class BaseDataClass:
    id: int

    def dict(self):
        return asdict(self)
    
    
@dataclass
class DataAudio(BaseDataClass):
    name: str
    path: str
    sample_rate: int
    channels: int
    text: str


@dataclass
class DataWhisper(BaseDataClass):
    text: str