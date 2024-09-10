import asyncio
from abc import abstractmethod
import flet as ft
import pygame
from flet_route import Params, Basket

from assets import HOME_ROUTE
from base.data import Audio
from base.mainapp import MainApp
from models import UpdateAction
from models.record.read_file import read_audio
from models.threads import run_async
from view import BaseView
from view.file_view.file_component import FileComponent

import threading


class FileView(BaseView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)

        self.status_init: bool = False

        self.app_bar = self.app_bars(title = "Tổng hợp các file",
                function_callbacks = [lambda event : self.main_app.page.go(HOME_ROUTE)],
                icons = [ft.icons.ARROW_LEFT], tooltips=['Quay lại'])
        self.update_list()

        self.icon_play = ft.IconButton(icon = ft.icons.PLAY_CIRCLE, icon_size = 50, splash_radius = 5,
                                on_click = self.play_audio, tooltip = "Thực hiện")
        self.display_result_audio = ft.CupertinoActionSheetAction(
                    content = self.icon_play,
                    is_default_action=True,
        )
        self.start_time  = ft.Text(value = "0", size = 10)
        self.end_time = ft.Text(value = "--", size = 10)
        self.slice = ft.Slider(value = 0, min = 0, max = 100)

        self.display_slicer = ft.CupertinoActionSheetAction(
            content = ft.Row(
                controls = [
                    self.start_time,
                    self.slice,
                    self.end_time
                ],
                alignment = ft.MainAxisAlignment.CENTER
            ),is_default_action=False
        )

        self.line = ""
        self.message = ft.Text("", size = 25, weight = ft.FontWeight.W_100)
        self.update_line = UpdateAction(interval = 1.02, callback = self.update_line_callback)
        self.action_sheet = ft.CupertinoActionSheet(
            title=ft.Row([ft.Text("Kết quả", size = 25)]),
            message = self.message,
            cancel=ft.CupertinoActionSheetAction(
                content=ft.Text("Thoát"),
                on_click = self.stop_audio
            ),
            actions=[
                self.display_slicer,
                self.display_result_audio
            ],
        )
        self.bottom_sheet = ft.CupertinoBottomSheet(self.action_sheet,
                                on_dismiss=self.stop_audio)
        self.current_audio: Audio = None
        self.is_running: bool = False

        self.update_second_slicer = UpdateAction(interval=0.5, callback = self.update_second_slicer_callback)

    def update_line_callback(self):
        self.message.value = self.line
        try:
            self.main_app.page.update()
        except:
            pass

    def update_second_slicer_callback(self):
        if not pygame.mixer.music.get_busy():
            self.is_running = False
            self.icon_play.icon = ft.icons.PAUSE_CIRCLE
            self.update_second_slicer.stop()
            pygame.mixer.music.stop()
            self.slice.value = 0
        else:
            current_second = pygame.mixer.music.get_pos() / 1000
            self.slice.value = current_second / int(self.end_time.value[:-1]) * 100
        try:
            self.slice.update()
        except:
            pass

    @abstractmethod
    async def enhance_audio(self, path: str):
        pass

    async def play_audio(self, event: ft.ControlEvent):
        self.is_running = not self.is_running
        if self.is_running:
            self.message.value = ""
            self.line = ""
            pygame.mixer.music.load(self.current_audio.path)  # Change this to your audio file
            pygame.mixer.music.play()
            self.update_second_slicer.start()
            self.icon_play.icon = ft.icons.PAUSE_CIRCLE
            event.page.update()
            self.update_line.start()
            await asyncio.sleep(3)

            if self.status_init:
                thread = threading.Thread(target = run_async,
                                args = (self.enhance_audio, self.current_audio.path))
                thread.start()
                self.status_init = False
        else:
            self.icon_play.icon = ft.icons.PLAY_CIRCLE
            pygame.mixer.music.pause()
            event.page.update()

    def stop_audio(self, event: ft.ControlEvent):
        self.is_running = False
        self.icon_play.icon = ft.icons.PLAY_CIRCLE
        event.page.update()
        pygame.mixer.music.stop()
        self.close_form(event)

    def open_form(self, event: ft.ControlEvent, audio_data: Audio):
        self.status_init = True
        event.page.open(self.bottom_sheet)
        self.current_audio = audio_data

        audio_np = read_audio(self.current_audio.path, self.main_app.global_settings.sample_rate,
                                self.main_app.global_settings.channels)
        self.end_time.value = str(int(len(audio_np) / self.main_app.global_settings.sample_rate)) + "s"
        event.page.update()


    def close_form(self, event: ft.ControlEvent):
        self.is_running = False
        self.icon_play.icon = ft.icons.PLAY_CIRCLE
        event.page.close(self.bottom_sheet)
        event.page.update()


    def update_list(self):
        self.content.controls.clear()
        for index_audio in range(len(self.main_app.audios)):
            self.content.controls.append(FileComponent(
                            audio_data = self.main_app.audios[index_audio],
                            title = "Audio " + str(index_audio + 1),
                            callback = self.open_form,
                            tooltip="Nghe", icons=ft.icons.PLAY_CIRCLE, text = self.main_app.audios[index_audio].text))

    def view(self, page: ft.Page, params: Params, basket: Basket) -> ft.View:
        base_view = super().view(page, params, basket)
        base_view.controls.append(self.bottom_sheet)
        if len(self.content.controls) != len(self.main_app.audios):
            self.update_list()
            self.status_init = True

            self.current_audio = self.main_app.audios[len(self.main_app.audios) - 1]
            audio_np = read_audio(self.current_audio.path, self.main_app.global_settings.sample_rate,
                                  self.main_app.global_settings.channels)
            self.end_time.value = str(int(len(audio_np) / self.main_app.global_settings.sample_rate)) + "s"
            page.open(self.bottom_sheet)
            page.update()


        return base_view