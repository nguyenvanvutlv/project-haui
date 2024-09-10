import json
from abc import abstractmethod

import flet as ft
from flet_route import Params, Basket

from assets import HOME_ROUTE, SETTINGS_JSON
from base.mainapp import MainApp
from view import BaseView
from view.settings.settings_component import SettingsComponent
import torch


class SettingsView(BaseView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)
        self.app_bar = self.app_bars(title = "Cài đặt",
                        function_callbacks = [lambda event : self.main_app.page.go(HOME_ROUTE)],
                        icons = [ft.icons.ARROW_LEFT],
                        tooltips = ["Quay lại"])

        self.settings_models = SettingsComponent(title = "Tải mô hình", objects = ft.Switch,
                            value = self.main_app.is_loaded, on_change = self.load_model)
        self.settings_gpu = SettingsComponent(title = "GPU", objects = ft.Switch,
                            value = self.main_app.global_settings.gpu, on_change = self.turn_on_gpu)
        self.content.controls = [
            self.settings_models,
            self.settings_gpu
        ]

    def turn_on_gpu(self, event: ft.ControlEvent):
        if event.control.value and not torch.cuda.is_available():
            snack_bar = ft.SnackBar(content = ft.Text("Không tìm thấy GPU"))
            if len(event.page.overlay):
                event.page.overlay.clear()
            event.page.overlay.append(snack_bar)
            snack_bar.open = True
        self.settings_gpu.button.value = event.control.value and torch.cuda.is_available()
        self.main_app.global_settings.gpu = self.settings_gpu.button.value
        self.main_app.global_settings.fp16 = self.settings_gpu.button.value
        self.main_app.global_settings.device = "cuda" if self.main_app.global_settings.gpu else "cpu"

        dict_ = self.main_app.global_settings.dict()
        with open(SETTINGS_JSON, "w", encoding = 'utf-8') as file:
            json.dump(dict_, file, ensure_ascii=False)
        event.page.update()

    @abstractmethod
    async def load_model(self, event: ft.ControlEvent):
        pass

    def view(self, page: ft.Page, params: Params, basket: Basket) -> ft.View:
        self.settings_models.button.value = self.main_app.is_loaded
        self.settings_gpu.button.value = self.main_app.global_settings.gpu
        base_view = super().view(page, params, basket)
        return base_view