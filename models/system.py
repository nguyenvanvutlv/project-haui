import flet as ft
import assets
import json
from base.system import MainApp
from base.dataclass import DataWhisper, DataVoiceActivityDetection
from models.models import PyAudioRecord, Whispers, VADs, SpeechRecognition
import torch


class App(MainApp):
    def __init__(self, page: ft.Page):
        settings = json.load(open(assets.SETTINGS_JSON, "r", 
                                encoding = 'utf-8'))
        page.window.height = settings.get('window', {}).get('height', 600)
        page.window.width = settings.get('window', {}).get('width', 800)
        super(App, self).__init__(page, 
            playlist = settings['audios'])
        # self.record_audio = PyAudioRecord(settings.get('record', {}).get('sample_rate', 16000),
        #                                   settings.get('record', {}).get('channels', 1))
        self.record_audio = SpeechRecognition(settings.get('record', {}).get('sample_rate', 16000),
                                          settings.get('record', {}).get('channels', 1))
        
        self.record_source = PyAudioRecord(settings.get('record', {}).get('sample_rate', 16000),
                                          settings.get('record', {}).get('channels', 1))

        self.whispers = Whispers(DataWhisper(id = 0, path = settings.get('model', {}).get('whisper', ""),
                                             fp16 = True if torch.cuda.is_available() else False,
                                             language = "vi", gpu = True if torch.cuda.is_available() else False))
        self.vads = VADs(DataVoiceActivityDetection(id = 1, path = settings.get('model', {}).get('vad', "")))
        

