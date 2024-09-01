import sys

import flet as ft
import json

import assets, pygame
from models.log.base_log import BaseLoguru
from models.speech_recognition.main import Record, ModelWav2vec


class MainApp(object):
    def __init__(self, page: ft.Page):
        pygame.mixer.init()
        self.log : BaseLoguru = BaseLoguru(sinks = [(sys.stdout, False)], name_logs = "main_app")
        self.config = json.load(open(assets.settings_path, mode = "r", encoding = "utf-8"))
        self.page: ft.Page = page
        self.record: Record = None
        self.models = ModelWav2vec(self.config["path_model"])




    def load_mic(self):
        if self.record is not None:
            return
        self.record: Record = Record(sample_rate = self.config["sample_rate"],
                                     mic_name = self.config["mic_name"],
                                     record_timeout = self.config["record_timeout"],
                                     save_file = self.config["save_file"])

    def settings_windows(self):
        self.page.window.width = self.config["width"]
        self.page.window.height = self.config["height"]
        self.page.update()

    def save_config(self):
        with open(assets.settings_path, "w", encoding = 'utf-8') as file:
            json.dump(self.config, file, ensure_ascii=False)