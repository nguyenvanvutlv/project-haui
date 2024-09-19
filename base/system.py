import flet as ft
from base.design_pattern import Singleton
from base.design_pattern import Manage
from base.models import Audio
from base.dataclass import DataAudio


class ManageAudio(Manage):
    def __init__(self):
        super().__init__()


class MainApp(metaclass = Singleton):
    page: ft.Page = None

    audios: ManageAudio = ManageAudio()

    def __init__(self, page: ft.Page, **kwargs):
        self.page = page

        for index, value in enumerate(kwargs.get('playlist', [])):
            self.audios.add(Audio(DataAudio(**value)))

    def on_route_change(self, event: ft.ControlEvent, route):
        self.page.go(route)
    