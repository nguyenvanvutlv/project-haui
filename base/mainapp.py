from assets import SETTINGS_JSON, DATABASE_JSON
from base import Singleton, Manage
import flet as ft
import json
from base.data import Settings, Audio
from base.models import Record, ModelVads, BaseRecord
import pygame

class ManageAudio(Manage):
    def __init__(self):
        super().__init__()


class ManageWhispers(Manage):
    def __init__(self):
        super().__init__()



class MainApp(metaclass = Singleton):
    page: ft.Page = None
    # phần cài đặt chính
    global_settings: Settings = None
    # danh sách audio đã được thêm vào
    audios: ManageAudio = ManageAudio()
    # danh sách mô hình
    is_loaded: bool = False
    models_whisper: ManageWhispers = ManageWhispers()


    record_pyaudio : BaseRecord = None
    record_speech : BaseRecord = None
    vad: ModelVads = None

    def __init__(self, page: ft.Page, **kwargs):
        self.page = page

        self.record_pyaudio = kwargs.get("record_pyaudio", None)
        self.record_speech = kwargs.get("record_speech", None)
        self.vad = kwargs.get('vad', None)

        self.global_settings = Settings(
            **json.load(open(SETTINGS_JSON, "r", encoding = 'utf-8'))
        )
        pygame.mixer.init(frequency=self.global_settings.sample_rate,
                          channels=self.global_settings.channels)

        data_audio = json.load(open(DATABASE_JSON, "r", encoding = 'utf-8'))
        for index_audio, value_audio in enumerate(data_audio):
            self.audios.attach(
                Audio(**value_audio)
            )
        self.page.window.width = self.global_settings.width
        self.page.window.height = self.global_settings.height
        self.page.update()

