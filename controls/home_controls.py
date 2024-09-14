import soundfile

import assets
from assets import FILES_ROUTE
from base.data import Audio
from base.mainapp import MainApp
from models import UpdateAction
from models.record.read_file import read_audio
from models.noisereduce import reduce_noise
from view.home.home_view import HomeView
import flet as ft
from datetime import datetime, timedelta
import numpy as np
from models.threads import run_async
import threading
import torch

class HomeControls(HomeView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)
        self.update_action = UpdateAction(interval=0.15, 
                        callback = self.update_action_callback)
        self.is_running : bool = False
        self.phrase_complete : bool = False
        self.is_run_enhance : bool = False
        self.current_text = ''

        self.is_running_global : bool = False
        self.is_speech: bool = False

    async def global_enhance(self, audio: np.ndarray):
        if self.is_running_global:
            return
        
        self.is_running_global = True

        audio = reduce_noise(audio, sr = self.main_app.global_settings.sample_rate,
                                use_torch=True)
        audio_torch = torch.as_tensor(audio).reshape(1, -1)
        # voice activity detection - phát hiện giọng nói
        segments = self.main_app.vad.get_speech(audio_torch,
                            sample_rate = self.main_app.global_settings.sample_rate)
        results = []
        for segment  in segments:
            start = segment['start']
            end = segment['end']
            chunk = audio[start:end]
            result = self.main_app.models_whisper[0].objects.transcribe(audio = chunk, language = "vi",
                                beam_size = self.main_app.global_settings.beam_size,
                                no_speech_threshold = 0.6,
                                compression_ratio_threshold=2.0,
                                fp16 = self.main_app.global_settings.fp16)
            results.append(result['text'][:-1])
        self.is_running_global = False
        self.message.value = ' '.join(results)
        self.main_app.page.update()

    async def enhnace_audio(self, audio: np.ndarray):
        # giảm nhiễu
        audio = reduce_noise(audio, sr = self.main_app.global_settings.sample_rate,
                             use_torch=True)
        audio_torch = torch.as_tensor(audio).reshape(1, -1)
        # voice activity detection - phát hiện giọng nói
        segments = self.main_app.vad.get_speech(audio_torch, 
                            sample_rate = self.main_app.global_settings.sample_rate)
        results = []
        for segment  in segments:
            start = segment['start']
            end = segment['end']
            chunk = audio[start:end]
            result = self.main_app.models_whisper[0].objects.transcribe(audio = chunk, language = "vi",
                                beam_size = self.main_app.global_settings.beam_size,
                                fp16 = self.main_app.global_settings.fp16)
            results.append(result['text'][:-1])
        self.is_run_enhance = False
        self.current_text = ' '.join(results) 
        self.line[-1] = self.current_text
        self.message.value = ' '.join(self.line)
        self.main_app.page.update()



    async def record(self, event : ft.ControlEvent):
        if self.is_running:

            # kiểm tra xem người dùng có ấn 2 lần liên tiếp hay không
            return
        
        self.is_running = True


        self.is_record = not self.is_record
        self.action_record.content.icon = ft.icons.PAUSE_CIRCLE if self.is_record\
            else ft.icons.CIRCLE
        event.page.update()

        if self.is_record:
            """
                Bắt đầu ghi âm
            """
            await self.main_app.record_pyaudio.start_record()
            await self.main_app.record_speech.start_record()
            self.update_action.start()  
            self.line.clear()
            self.line.append('')
            self.is_speech = False
            self.phrase_complete = False
            self.main_app.record_speech.last_get = None
        else:
            """
                Kết thúc ghi âm
            """
            await self.main_app.record_pyaudio.end_record()
            await self.main_app.record_speech.end_record()
            self.update_action.stop()


            # thực hiện lưu thành file âm thanh
            # thực hiện tạo tên tệp
            path = f"assets/audios/output_{len(self.main_app.audios) + 1}.wav"
            # thực hiện lấy dữ liệu từ pyaudio [nguồn chính]
            # audip_np = self.main_app.record_pyaudio.get_data(norm=True)
            self.main_app.record_pyaudio.save_file(path, norm=True)
            self.main_app.record_speech.clear_data()
            self.main_app.record_pyaudio.clear_data()
            audio_data = Audio(id = len(self.main_app.audios), path = path,
                                sample_rate=self.main_app.global_settings.sample_rate,
                                channels = self.main_app.global_settings.channels)
            self.main_app.audios.attach(audio_data)
            self.main_app.audios.save(assets.DATABASE_JSON)
        self.is_running = False


    async def update_action_callback(self):

        data_pyaudio = self.main_app.record_pyaudio.get_data(norm = True)
        data_speech = self.main_app.record_speech.get_data(norm = True)

        length = data_speech.shape[0]
        
        
        now = datetime.now()

        if self.main_app.record_speech.last_get and now - self.main_app.record_speech.last_get\
              > timedelta(seconds=self.main_app.record_speech.kwargs.get("phrase_timeout", 3)):
            self.phrase_complete = True

        if length > 0 and not self.is_run_enhance:
            self.is_speech = True
            self.is_run_enhance = True
            thread = threading.Thread(target = run_async,
                                args = (self.enhnace_audio, data_speech))
            thread.start()
        if self.phrase_complete and not self.is_running:
            self.main_app.record_speech.clear_data()
            self.main_app.record_speech.last_get = None
            self.phrase_complete = False
            if len(self.current_text) > 0:
                self.line.append(self.current_text)
                self.line.append('')

        if data_pyaudio.shape[0] > 0 and self.is_speech:
            thread = threading.Thread(target = run_async,
                                      args = (self.global_enhance, data_pyaudio))
            thread.start()

        

        
                
        



    def pick_files_result(self, event: ft.FilePickerResultEvent):
        files = super().pick_files_result(event)
        if files is None:
            return

        path = files.path
        size = files.size

        audio_np = read_audio(path, sample_rate=self.main_app.global_settings.sample_rate,
                                channel = self.main_app.global_settings.channels)
        soundfile.write(f"assets/audios/{len(self.main_app.audios) + 1}.wav", audio_np,
                        samplerate=self.main_app.global_settings.sample_rate)
        audio_data = Audio(id = len(self.main_app.audios), path = f"assets/audios/{len(self.main_app.audios) + 1}.wav",
                            sample_rate=self.main_app.global_settings.sample_rate,
                            channels = self.main_app.global_settings.channels)
        self.main_app.audios.attach(audio_data)
        self.main_app.audios.save(assets.DATABASE_JSON)


        event.page.go(FILES_ROUTE)
















