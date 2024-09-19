from numpy.core.multiarray import array as array
from base.models import RecordAudio, BaseWhispers, BaseVAD
from base.dataclass import DataRecord, DataWhisper, DataVoiceActivityDetection
import pyaudio
import torch
import numpy as np
from models.whisper import load_model
from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
import asyncio
import threading
import speech_recognition as sr
from models.processing import remove_special_characters


class SpeechRecognition(RecordAudio):
    def __init__(self, sample_rate = 16000, channels = 1):
        super(SpeechRecognition, self).__init__(DataRecord(0, sample_rate, channels))
        self.recorder = sr.Recognizer()
        self.recorder.dynamic_energy_threshold = False
        self.recorder.energy_threshold = 1000
        self.mic = sr.Microphone(sample_rate = self.record_data.sample_rate)

    async def start_record(self):
        self.data_process.queue.clear()
        self.data.queue.clear()
        with self.mic:
            self.recorder.adjust_for_ambient_noise(self.mic)
        self.stream = self.recorder.listen_in_background(self.mic, self.callback)

    async def stop_record(self):
        if self.stream:
            self.stream(wait_for_stop=True)
            self.stream = None
    
    def callback(self, recognizer, audio):
        super(SpeechRecognition, self).callback(audio.get_raw_data())


class PyAudioRecord(RecordAudio):
    def __init__(self, sample_rate = 16000, channels = 1):
        super(PyAudioRecord, self).__init__(DataRecord(0, sample_rate, channels))
        self.stream : pyaudio.Stream = None



    async def start_record(self):
        self.data.queue.clear()
        self.data_process.queue.clear()
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


    def pipeline(self, data: np.ndarray):
        # print("START_PIPELINE")
        try:
            result = self.model.transcribe(audio = data, 
                        language = self.data_whisper.language, beam_size = 4)
            print(result)
        except Exception as e:
            print(e)
            result = ""
        return self.post_process(result = result)
    

    def post_process(self, **kwargs):
        # print("END_PIPELINE")
        try:
            result = remove_special_characters(kwargs.get("result").get('text')).replace('.', '')
        except:
            result = ""
        return result
    

class VADs(BaseVAD):
    def __init__(self, data_vad : DataVoiceActivityDetection):
        super(VADs, self).__init__(data_vad)

    async def load_model(self):
        self.model = Model.from_pretrained(checkpoint = self.data_vad.path,
                    map_location = torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = VoiceActivityDetection(segmentation=self.model)
        HYPER_PARAMETERS = {
            # remove speech regions shorter than that many seconds.
            "min_duration_on": 0.3,
            # fill non-speech regions shorter than that many seconds.
            "min_duration_off": 0.0
        }
        self.model.instantiate(HYPER_PARAMETERS)

    def pipeline(self, data: torch.tensor, sample_rate: int):
        segments = self.model({'waveform': data, 'sample_rate': sample_rate})
        return self.post_process(segments = segments, sample_rate = sample_rate)

    def post_process(self, **kwargs):
        segments = kwargs.get("segments")
        sample_rate = kwargs.get("sample_rate")
        chunks = []
        for (segment, _, _) in segments.itertracks(yield_label=True):
            chunks.append([int(segment.start * sample_rate), int(segment.end * sample_rate)])
        return chunks


def run_async(coroutime, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coroutime(*args))
    loop.close()