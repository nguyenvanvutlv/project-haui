import asyncio
import pyaudio
import numpy as np
import speech_recognition
import torch
from pyannote.audio import Pipeline
from base.models import Record, ModelVads, BaseRecord


class RecordAudio(Record):
    def __init__(self):
        super().__init__()
        self.chunk_size = 1024

    def callback(self, _, audio: speech_recognition.AudioData):
        self.data_queue.put(audio.get_raw_data())
        print("RECORD...")

    async def start_record(self, sample_rate : int, channels: int):
        await asyncio.sleep(1)
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)

        self.stopper = self.recorder.listen_in_background(self.source,
                                self.callback, phrase_time_limit = self.record_timeout)

        return

    async def end_record(self):
        await asyncio.sleep(1)
        if self.stopper is not None:
            await self.stopper(wait_for_stop=True)
            self.stopper = None

    def get_numpy(self) -> np.ndarray | None:
        # if len(self.data_queue.queue):
        #     audio_np = np.frombuffer(b''.join(self.frames), dtype = np.int16).astype(np.float32) / 32768.0
        #     return audio_np
        # return None
        return None
    

class RecordPyaudio(BaseRecord):
    def __init__(self, sample_rate: int = 16000, channels: int = 1, **kwargs):
        super().__init__(sample_rate, channels, **kwargs)
        self.__pyaudio_object = pyaudio.PyAudio()
        self.__stream = None

    async def start_record(self):
        self.__stream = self.__pyaudio_object.open(channels=self.channels, 
                                                   rate = self.sample_rate,
                                                   stream_callback = self.callback,
                                                   **self.kwargs)
        self.is_record = True
        self.__stream.start_stream()

    async def end_record(self):
        if self.__stream is not None:
            self.__stream.stop_stream()
            self.__stream.close()
    
    def callback(self, in_data, frame_count, time_info, status):
        super().callback(data = in_data)
        return (in_data, pyaudio.paContinue)
    

class RecordSpeechRecognition(BaseRecord):
    def __init__(self, sample_rate: int = 16000, channels: int = 1, **kwargs):
        """
            param:

            sample_rate: int = 16000
            channels: int = 1
            kwargs:
                energy_threshold: int = 1000
                dynamic_energy_threshold: bool = False
                device_index: int = None
                chunk_size: int = 1024
                record_timeout: int = 2
                phrase_timeout = 3
        """
        super().__init__(sample_rate, channels, **kwargs)

        self.__recognizer = speech_recognition.Recognizer()
        self.__recognizer.energy_threshold = kwargs.get("energy_threshold", 1000)
        self.__recognizer.dynamic_energy_threshold = kwargs.get("dynamic_energy_threshold", False)
        self.__source = speech_recognition.Microphone(
            device_index = self.kwargs.get("device_index", None),
            sample_rate = self.sample_rate,
            chunk_size = self.kwargs.get("chunk_size", 1024)
        )
        self.stopper = None

    async def start_record(self):
        with self.__source:
            self.__recognizer.adjust_for_ambient_noise(
                self.__source)
        self.stopper = self.__recognizer.listen_in_background(
            self.__source, self.callback, 
            phrase_time_limit=self.kwargs.get('record_timeout', 2))
        
    async def end_record(self):
        if self.stopper is not None:
            self.stopper(wait_for_stop=True)
            self.stopper = None

    def callback(self, _, audio: speech_recognition.AudioData):
        super().callback(data = audio.get_raw_data())
        


class ModelVad(ModelVads):
    def __init__(self, repo_or_dir = "snakers4/silero-vad",
                 model = "silero_vad",
                 onnx = False,
                 threshold: float  = 0.4):
        super().__init__(threshold)
        self.__load_model(repo_or_dir, model, onnx)

    def __load_model(self, repo_or_dir, model, onnx):
        self.__model, utils = torch.hub.load(
            repo_or_dir=repo_or_dir, model=model, onnx=onnx, trust_repo=True
        )
        self.__get_speech_timestamps = utils[0]

    def get_speech(self, audio, sample_rate):
        return self.__get_speech_timestamps(audio,
                            self.__model, sampling_rate=sample_rate, threshold=self.threshold)


class VoiceActivityDetection(ModelVads):
    def __init__(self):
        super().__init__()
        self.__load_model(checkpoint_path = "assets/models/vad.yaml")

    def __load_model(self, *args, **kwargs):
        self.__models = Pipeline.from_pretrained(**kwargs)

    def get_speech(self, audio: np.ndarray, sample_rate: int):
        audio_chunk_torch = torch.as_tensor(audio).reshape(1, -1)
        segments = self.__models({"waveform": audio_chunk_torch, 
                            "sample_rate": sample_rate})
        results = []
        for segment, _, _ in segments.itertracks(yield_label=True):
            start = int(segment.start * sample_rate)
            end = int(segment.end * sample_rate)
            results.append({
                "start": start,
                "end": end
            })
        return results