from abc import abstractmethod

import numpy as np
import pyaudio
import soundfile
from queue import Queue
import speech_recognition as sr


class Record:
    def __init__(self, sample_rate = 16000, energy_threshold = 1000,
                 dynamic_energy_threshold = False):

        self.data_queue = Queue()  # dữ liệu
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = energy_threshold
        self.recorder.dynamic_energy_threshold = dynamic_energy_threshold
        self.source = sr.Microphone(sample_rate = sample_rate)
        self.record_timeout = 2
        self.stopper = None

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
        self.__model = None
        self.__get_speech_timestamps = None
        self.threshold = threshold

    @abstractmethod
    def __load_model(self, repo_or_dir, model, onnx):
        pass

    @abstractmethod
    def get_speech(self, audio, sample_rate):
        pass
