from abc import abstractmethod

import numpy as np
import pyaudio
import soundfile
from queue import Queue
import speech_recognition as sr
from datetime import datetime
from pyannote.audio import Pipeline


class BaseRecord:
    def __init__(self, sample_rate: int = 16000, channels: int = 1, **kwargs):
        """
            lớp base dùng cho thu âm từ source [pyaudio] hoặc [speech recognition]
        """
        self.sample_rate: int = sample_rate
        self.channels: int = channels
        self.kwargs: dict = kwargs
        self.is_record: bool = False
        self.__data: Queue = Queue()
        self.pharse_time = None
        self.__current_audio: list = []
        self.last_get: datetime = None


    @abstractmethod
    async def start_record(self):
        pass

    @abstractmethod
    async def end_record(self):
        pass

    @abstractmethod
    def callback(self, **kwrags):
        """
            Thực hiện callback lấy dữ liệu từ source 
                    [có thể là speech recognition hoặc pyaudio]

            - recognition: audio: sr.AudioData

            - pyaudio: in_data: bytes, frame_count: int, time_info: dict, status: int

            data nhận vào phải để ở dạng bytes
        """
        if not isinstance(kwrags.get("data", None), bytes):
            raise ValueError(f"Dữ liệu nhận được phải ở dạng bytes, [{type(kwrags.get('data'))}]")
        self.__data.put(kwrags.get("data"))
        self.last_get = datetime.now()

    def get_data(self, norm: bool = True) -> np.ndarray:
        """
            Lấy dữ liệu từ queue và chuyển thành numpy array

            - norm: bool: chuẩn hóa dữ liệu, nên dùng chuẩn hóa cho việc thu âm trực tiếp từ microphone
        """
        data = np.frombuffer(b''.join(self.__data.queue), 
                        dtype = np.int16).astype(np.float32)
        if norm:
            data = data / 32768.0
        return data
    
    def clear_data(self):
        self.__data.queue.clear()


    def save_file(self, path: str, norm: bool = False):
        """
            Lưu file audio với đường dẫn path
        """
        data = self.get_data(norm)
        soundfile.write(path, data = data, samplerate=self.sample_rate)


class Record:
    def __init__(self, sample_rate = 16000, energy_threshold = 1000,
                 dynamic_energy_threshold = False):


        # phần record từ speech recognition
        self.data_queue = Queue()  # dữ liệu
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = energy_threshold
        self.recorder.dynamic_energy_threshold = dynamic_energy_threshold
        self.source = sr.Microphone(sample_rate = sample_rate)
        self.record_timeout = 2
        self.stopper = None



        # phần record từ source [pyaudio]
        self.pyaudio_object = pyaudio.PyAudio()
        self.stream = None
        self.frames = []



    @abstractmethod
    async def start_record(self, sample_rate : int, channels: int):
        pass

    @abstractmethod
    def callback(self, _, audio: sr.AudioData):
        pass


    @abstractmethod
    async def end_record(self):
        pass

    @abstractmethod
    def get_numpy(self) -> np.ndarray:
        pass

    def save_record(self, path: str, sample_rate: int):
        audio_np = self.get_numpy()
        soundfile.write(path, data = audio_np, samplerate=sample_rate)


    def clear_record(self):
        self.data_queue.queue.clear()

class ModelVads(object):
    def __init__(self, threshold: float  = 0.4):
        self.threshold = threshold
        self.__models = None

    @abstractmethod
    def __load_model(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_speech(self, audio: np.ndarray, sample_rate : int):
        pass
