import asyncio
import pyaudio
import numpy as np
import speech_recognition
import torch

from base.models import Record, ModelVads


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