from numpy.core.multiarray import array as array
from base.models import RecordAudio, BaseWhispers
from base.dataclass import DataRecord, DataWhisper
import pyaudio
import torch
import numpy as np
from models.whisper import load_model


class PyAudioRecord(RecordAudio):
    def __init__(self, sample_rate = 16000, channels = 1):
        super(PyAudioRecord, self).__init__(DataRecord(0, sample_rate, channels))
        self.stream : pyaudio.Stream = None



    async def start_record(self):
        self.data.queue.clear()
        self.stream = pyaudio.PyAudio().open(
            format = pyaudio.paInt16,
            channels = self.record_data.channels,
            rate = self.record_data.sample_rate,
            input = True,
            stream_callback = self.callback
        )
        
    async def stop_record(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

    def callback(self, in_data, frame_count, time_info, status):
        super(PyAudioRecord, self).callback(in_data)
        return in_data, pyaudio.paContinue
    

class Whispers(BaseWhispers):
    def __init__(self, data_whisper: DataWhisper):
        super(Whispers, self).__init__(data_whisper)

    async def load_model(self):
        self.model = load_model(name = self.data_whisper.path, 
                    device = torch.device("cuda" if torch.cuda.is_available() else "cpu"),
                    in_memory=True)
        return "OK"


    def pipeline(self, data: np.array):
        result = self.model.transcribe(data, language = self.data_whisper.language)
        return self.post_process(result = result)
    

    def post_process(self, **kwargs):
        result = kwargs.get("result").get('text')
        return result