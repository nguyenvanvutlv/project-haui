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
class DataRecord(BaseDataClass):
    sample_rate: int = 16000
    channels : int = 1


@dataclass
class DataWhisper(BaseDataClass):
    path: str = ""
    fp16: bool = False
    language: str = "vi"
    gpu: bool = False


@dataclass
class DataVoiceActivityDetection(BaseDataClass):
    path: str = ""
    min_duration: float = 0.3