import asyncio
import pyaudio
import numpy as np
import torch

from base.models import Record, ModelVads


class RecordAudio(Record):
    def __init__(self):
        super().__init__()
        self.chunk_size = 1024

    # def callback(self, in_data, frame_count, time_info, status):
    #     if self.is_recording:
    #         self.frames.append(in_data)
    #     print(self.is_recording, type(in_data))
    #     return in_data, pyaudio.paContinue

    async def _record_loop(self):
        while self.is_recording:
            if self.stream is not None and self.stream.is_active():
                data = self.stream.read(self.chunk_size)
                self.frames.append(data)
            await asyncio.sleep(0.01)

    async def start_record(self, sample_rate : int, channels: int):
        await asyncio.sleep(1)
        self.frames.clear()
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format = pyaudio.paInt16,
                                  channels = channels,
                                  rate = sample_rate,
                                  input = True,
                                  frames_per_buffer = self.chunk_size)
        self.is_recording = True
        asyncio.create_task(self._record_loop())
        print("start record")
        return

    async def end_record(self):
        await asyncio.sleep(1)
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        self.stream = None

    def get_numpy(self) -> np.ndarray | None:
        if len(self.frames):
            audio_np = np.frombuffer(b''.join(self.frames), dtype = np.int16).astype(np.float32) / 32768.0
            return audio_np
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