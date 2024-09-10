import asyncio

from base.data import WhisperData
from base.mainapp import MainApp
from view.settings.settings_view import SettingsView
from models.whisper import load_model
import flet as ft
import torch

class SettingsControls(SettingsView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)
        self.is_running: bool = False

    async def load_model(self, event: ft.ControlEvent):
        await asyncio.sleep(1)
        if self.is_running:
            self.settings_models.button.value = not event.control.value
            event.page.update()
            return

        self.is_running = True

        if event.control.value:
            snack_bar = ft.SnackBar(content = ft.Text("Đang tải mô hình"))
            if len(event.page.overlay):
                event.page.overlay.clear()
            event.page.overlay.append(snack_bar)
            snack_bar.open = True
            event.page.update()
            await asyncio.sleep(1)
            for index_model, value in enumerate(self.main_app.global_settings.models):
                dict_ = value.copy()
                whisper_data = WhisperData(**dict_)
                dict_.pop('id')
                dict_['device'] = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                whisper_data.objects = load_model(**dict_)
                self.main_app.models_whisper.attach(whisper_data)
            snack_bar = ft.SnackBar(content = ft.Text("Đã tải xong mô hình"))
            if len(event.page.overlay):
                event.page.overlay.clear()
            event.page.overlay.append(snack_bar)
            snack_bar.open = True
            event.page.update()
        else:
            self.main_app.models_whisper.clear_all()
            snack_bar = ft.SnackBar(content = ft.Text("Dừng mô hình"))
            if len(event.page.overlay):
                event.page.overlay.clear()
            event.page.overlay.append(snack_bar)
            snack_bar.open = True
            event.page.update()
        self.main_app.is_loaded = event.control.value
        self.is_running = False