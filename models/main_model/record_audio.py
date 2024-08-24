import asyncio

from base_model.base import Model
import speech_recognition as sr
import sys
import numpy as np

from models.main_model.model_speechRecognition.AutoSpeechRecognition import AudioModel
from models.main_model.time_counter.update import UpdateAction
from models.process.remove_silent import process_remove


class Record(Model):
    sample_rate: int = 0
    audio_data: np.ndarray = None
    recorder: sr.Recognizer = None
    micro: sr.Microphone = None
    record_timeout: float = 3
    record_phrase_timeout: float = 5
    update_timer: UpdateAction = None
    audio_model: AudioModel = None
    silent_waveform: np.ndarray = None

    # context

    current_context: str = ""
    update_context: callable = None
    update_new_context: callable = None

    def create_object(self, sample_rate: int, energy_threshold: int,
                      record_timeout: int, update_context: callable, update_new_context: callable,
                      phrase_timeout: int = 5, **kwargs):
        super().create_object(**kwargs)
        self.sample_rate = sample_rate
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = energy_threshold
        self.recorder.dynamic_energy_threshold = False
        self.record_phrase_timeout = phrase_timeout
        if 'linux' in sys.platform:
            index = [mic_name for mic_name in \
                     sr.Microphone.list_microphone_names() if mic_name == "pulse"][0]
            self.micro = sr.Microphone(sample_rate = self.sample_rate,
                                       device_index = index)
        else:
            self.micro = sr.Microphone(sample_rate = self.sample_rate)
        self.silent_waveform = np.zeros(int(self.sample_rate * 1.0))
        self.update_timer = UpdateAction(interval = 1.02, callback = self.get_context_from_wav)
        self.update_context = update_context
        self.update_new_context = update_new_context

        return self

    async def start_record(self):
        with self.micro:
            self.recorder.adjust_for_ambient_noise(self.micro, duration = 1)

        self.stop_record_object = self.recorder.listen_in_background(self.micro, self.record_callback,
                                           phrase_time_limit = self.record_timeout)
        self.update_timer.start()

    async def stop_record(self):
        # thực hiện việc dừng ghi âm
        try:
            if self.stop_record_object is not None:
                self.update_timer.stop()
                self.stop_record_object(wait_for_stop = True)
                self.audio_data = None
                await asyncio.sleep(5)
        except:
            return

    def record_callback(self, _, audio: sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        audio_np = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if self.audio_data is None:
            self.audio_data = audio_np
        else:
            self.audio_data = np.concatenate((self.audio_data, audio_np), axis = 0)

    def update_model(self, model: AudioModel):
        self.audio_model = model

    async def get_context_from_wav(self):
        if self.update_timer.is_running:
            return
        self.update_timer.is_running = True
        print("HIHI")

        if self.audio_data is None or self.audio_model is None:
            self.update_timer.is_running = False
            return

        result, segment = process_remove(waveform = self.audio_data, sample_rate = self.sample_rate,
                                         silent_waveform = self.silent_waveform)
        result = np.concatenate(result, axis = 0).astype(np.float32)
        context = await self.audio_model.trans(result)
        self.current_context = context['text']
        self.update_context(self.current_context)

        current_second = len(self.audio_data) / self.sample_rate
        if current_second >= 5:
            print("BIG")
            self.audio_data = None
            self.update_new_context()

        self.update_timer.is_running = False

    # def get_audio_data(self):
    #     audio_data = b''.join(self.data_queue.queue)
    #     audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
    #     if self.audio_data is None:
    #         self.audio_data = audio_np
    #     else:
    #         self.audio_data = np.concatenate((self.audio_data, audio_np), axis = 0)
    #     self.data_queue.clear()