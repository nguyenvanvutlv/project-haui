from abc import abstractmethod

import numpy as np
import pyaudio
import soundfile


class Record:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False

    @abstractmethod
    async def start_record(self, sample_rate : int, channels: int):
        pass

    @abstractmethod
    def callback(self, in_data, frame_count, time_info, status):
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
        self.frames.clear()

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
