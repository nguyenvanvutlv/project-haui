from abc import abstractmethod

import flet as ft
import pygame
from flet_route import Params, Basket

from assets import HOME_ROUTE, SETTINGS_ROUTE, CURRENT_AUDIO
from base_model.base import MainApp
from templates.base_template import BaseView
from templates.component.audio_component_template import AudioComponent
from templates.component.new_record_template import RecordComponent


class MicView(BaseView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)
        self.record_component: RecordComponent = RecordComponent(title = "Ghi Âm",
                                                                 function_callback = [self.start_record, self.end_record],
                                                                 tooltips = ["Bắt đầu", "Dừng"])

        self.new_record: ft.IconButton = ft.IconButton(icon = ft.icons.ADD, tooltip = "Tạo bản ghi âm mới",
                                                       on_click = self.new_record_function)
        self.list_audio: ft.Column = None

    @abstractmethod
    async def new_record_function(self, event: ft.ControlEvent):
        self.record_component.open_form(event)
        event.page.update()
        self.main_app.load_mic()
        self.main_app.models.load_model()

    @abstractmethod
    def start_record(self, event: ft.ControlEvent):
        self.record_component.update_button_record(event, True)
        self.main_app.record.start_record()


    @abstractmethod
    async def end_record(self, event: ft.ControlEvent):
        self.record_component.update_button_record(event, False)
        await self.main_app.record.end_record()

    def view_current_audio(self, event: ft.ControlEvent, config: dict, basket: Basket):
        basket.current_audio_config = config
        event.page.go(CURRENT_AUDIO)



    def view(self, page: ft.Page, params: Params, basket: Basket) -> ft.View:
        base_view = super().view(page, params, basket)
        if self.list_audio is None:
            self.list_audio = ft.Column()
            for index, value in enumerate(self.main_app.config["data_base_audio"]):
                audio_component = AudioComponent(config = value, basket = basket, callback_listen = self.view_current_audio)
                self.list_audio.controls.append(audio_component)


        self.create_appbar(title = "Ghi âm trực tiếp",
                           icons = [ft.icons.ARROW_LEFT],
                           function_callback = [lambda event : page.go(HOME_ROUTE)],
                           tooltips = ["Quay lại"])
        base_view.controls.append(self.app_bar)
        base_view.controls.append(self.new_record)
        base_view.controls.append(self.record_component)
        base_view.controls.append(self.list_audio)
        return base_view