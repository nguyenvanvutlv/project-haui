import asyncio
from dataclasses import dataclass, asdict
from datetime import datetime

import numpy as np
import soundfile
import torch.cuda
import speech_recognition as sr
from queue import Queue
from models.update_action import UpdateAction
from models.renoise_audio import reduce_noise
from models.whisper import Whisper, load_model

@dataclass
class ConfigModel:
    model_size_or_path: str = ""
    compute_type: str = "float16"
    device: str = "auto"
    download_root: str = ""

    def dict(self):
        return asdict(self)

class ModelWav2vec:
    def __init__(self, path):
        self.path = path
        self.models: Whisper = None

    def load_model(self):
        if self.models is not None:
            return
        if not torch.cuda.is_available():
            raise Exception("GPU NOT RUNNING")
        self.models = load_model(name = self.path, device = "cuda", in_memory=True)

    def trans(self, audio):
        result = self.models.transcribe(audio, condition_on_previous_text=False, language="vi")
        print(result)
        # return result["text"], result[""]


class Record(object):
    def __init__(self, mic_name: str = "pulse", sample_rate: int = 16000,
                 record_timeout: int = 2, save_file: str = "assets/record.wav"):

        if mic_name not in sr.Microphone.list_microphone_names():
            raise Exception("MIC NOT FOUND")

        self.mic_name = mic_name
        self.sample_rate = sample_rate
        self.record_timeout = record_timeout
        self.save_file = save_file


        self.data_queue = Queue()    # queue này dùng để thực hiện chuyển giọng nói thành văn bản
        self.process_queue = Queue() # queue này dùng để nhận dữ liệu đầu vào

        self.mic = sr.Microphone(sample_rate = self.sample_rate,
             device_index = [index for index, value in enumerate(sr.Microphone.list_microphone_names()) \
                             if value == self.mic_name][0])

        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = 2500
        self.recorder.dynamic_energy_threshold = False
        self.stopper = None

        self.current_audio = None
        self.final_audio = []

        self.update_data: UpdateAction = UpdateAction(interval = 1.02,
                                                      callback = self.speech2text)

        self.models : ModelWav2vec = None

    def record_callback(self, _, audio: sr.AudioData) -> None:
        print("recording...")
        self.process_queue.put(audio.get_raw_data())
        self.data_queue.put(audio.get_raw_data())

    def speech2text(self):
        if self.update_data.is_running:
            return

        self.update_data.is_running = True
        if not self.process_queue.empty():
            self.current_audio = np.frombuffer(b''.join(self.data_queue.queue),
                            dtype = np.int16).astype(np.float32) / 32768.0
            self.current_audio = reduce_noise(y = self.current_audio, sr = self.sample_rate)
            self.process_queue.queue.clear()

            self.models.trans(audio = self.current_audio)

        else:
            # nếu không nhận được dữ liệu mới thì sẽ thực hiện làm mới phần data_queue
            if self.current_audio is not None:
                self.final_audio.append(self.current_audio)
                self.current_audio = None
            self.data_queue.queue.clear()
            pass
        self.update_data.is_running = False

    def start_record(self):
        with self.mic:
            self.recorder.adjust_for_ambient_noise(self.mic)
        self.stopper = self.recorder.listen_in_background(self.mic, self.record_callback,
                                           phrase_time_limit=self.record_timeout)
        self.update_data.start()

    async def end_record(self):
        print("end record")
        self.update_data.stop()
        if self.stopper is not None:
            self.stopper(wait_for_stop = True)

        if self.current_audio is not None:
            self.final_audio.append(self.current_audio)
            self.current_audio = None


        self.process_queue.queue.clear()
        self.data_queue.queue.clear()
        if len(self.final_audio) == 0:
            return
        # print(len(self.final_audio))

        audio_np = np.concatenate(self.final_audio, axis = 0)
        soundfile.write(self.save_file, audio_np, self.sample_rate)


# if __name__ == "__main__":
#     async def run():
#         record = Record()
#
#         record.start_record()
#
#         while True:
#             try:
#                 pass
#             except:
#                 await record.end_record()
#     asyncio.run(run())