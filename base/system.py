import flet as ft
from base.design_pattern import Singleton
from base.design_pattern import Manage
from base.models import Audio, RecordAudio, BaseWhispers, BaseVAD
from base.dataclass import DataAudio, DataWhisper, DataVoiceActivityDetection
import torch
import assets
import json

class ManageAudio(Manage):
    def __init__(self):
        super().__init__()


class MainApp(metaclass = Singleton):
    page: ft.Page = None

    audios: ManageAudio = ManageAudio()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    data_whisper: DataWhisper = DataWhisper(
        id = 0,
        fp16 = True if torch.cuda.is_available() else False,
        gpu = device
    )
    data_vad: DataVoiceActivityDetection = DataVoiceActivityDetection(id = 1)


    record_audio: RecordAudio = None
    record_source: RecordAudio = None

    whispers: BaseWhispers = None
    vads: BaseVAD = None

    def __init__(self, page: ft.Page, **kwargs):
        self.page = page

        for index, value in enumerate(kwargs.get('playlist', [])):
            self.audios.add(Audio(DataAudio(**value)))

        print(len(self.audios))

        self.data_whisper.path = kwargs.get('model', {}).get('whisper', "")
        self.data_vad.path = kwargs.get('model', {}).get('vad', "")

    def on_route_change(self, event: ft.ControlEvent, route):
        self.page.go(route)

    def save(self):
        data = {
            "audios" : self.audios.save(),
            "model": {
                "whisper": "assets/models/pho.bin",
                "vad": "assets/models/pytorch_model.bin"
            },
            "windows": {
                "height": 600,
                "width": 800
            },
            "record": {
                "sample_rate": 16000,
                "channels": 1
            }
        }
        with open(assets.SETTINGS_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            