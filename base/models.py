from base import BaseModel
from base.dataclass import DataAudio, DataRecord, DataWhisper, DataVoiceActivityDetection
import pyaudio
from queue import Queue
from abc import abstractmethod
import numpy as np
from models.whisper import Whisper

class Audio(BaseModel):
    def __init__(self, audio_data : DataAudio):
        """
        :param audio_data: DataAudio
        
        """
        super(Audio, self).__init__(audio_data.id)
        self.audio_data = audio_data

    @property
    def name(self) -> str:
        return self.audio_data.path
    
    @property
    def path(self) -> str:
        return self.audio_data.path
    
    @property
    def text(self) -> str:
        return self.audio_data.text
    
    def dict(self):
        return self.audio_data.dict()
    

class RecordAudio(BaseModel):
    def __init__(self, record_data : DataRecord):
        """
        :param audio_data: DataAudio
        
        """
        super(RecordAudio, self).__init__(record_data.id)
        self.record_data = record_data
        self.data: Queue = Queue()
        self.data_process = Queue()

    @abstractmethod
    async def start_record(self):
        pass


    @abstractmethod
    async def stop_record(self):
        pass

    @abstractmethod
    def callback(self, *args, **kwargs):
        data, = args
        self.data.put(data)
        self.data_process.put(data) 
        # print("CALLBACK", len(self.data.queue))
        

    @property
    def get_data(self):
        data = np.frombuffer(b''.join(self.data.queue), 
                dtype = np.int16).astype(np.float32) / 32768.0
        return data
    
    @property
    def get_data_process(self):
        data = np.frombuffer(b''.join(self.data.queue), 
                dtype = np.int16).astype(np.float32) / 32768.0
        return data


class BaseWhispers(BaseModel):
    def __init__(self, data_whisper: DataWhisper):
        super(BaseWhispers, self).__init__(id)
        self.data_whisper = data_whisper
        self.model : Whisper | object = None
        self.is_loaded: bool = False

    @abstractmethod
    async def load_model(self):
        pass

    @abstractmethod
    def pipeline(self, data: np.array):
        pass

    @abstractmethod
    def post_process(self, **kwargs):
        pass

class BaseVAD(BaseModel):
    def __init__(self, data_vad: DataVoiceActivityDetection):
        super(BaseVAD, self).__init__(id)
        self.data_vad = data_vad
        self.model : object = None
        self.is_loaded: bool = False

    @abstractmethod
    async def load_model(self):
        pass

    @abstractmethod
    def pipeline(self, data: np.array):
        pass

    @abstractmethod
    def post_process(self, **kwargs):
        pass