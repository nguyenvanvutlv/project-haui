from base_model.base import Model
from queue import Queue
import speech_recognition as sr
import sys
import assets




class Record(Model):
    sample_rate: int = 0
    data_queue: Queue = Queue()
    recorder: sr.Recognizer = None
    micro: sr.Microphone = None

    def create_object(self, sample_rate: int, energy_threshold: int, **kwargs):
        super().create_object(**kwargs)
        self.sample_rate = sample_rate
        self.data_queue.queue.clear()
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = energy_threshold
        self.recorder.dynamic_energy_threshold = False
        if 'linux' in sys.platform:
            index = [mic_name for mic_name in \
                     sr.Microphone.list_microphone_names() if mic_name == "pulse"][0]
            self.micro = sr.Microphone(sample_rate = self.sample_rate,
                                       device_index = index)
        else:
            self.micro = sr.Microphone(sample_rate = self.sample_rate)


        return self