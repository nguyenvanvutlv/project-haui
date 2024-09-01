import flet as ft
import pygame
from flet_route import Params, Basket

from assets import MIC_ROUTE
from models.update_action import UpdateAction
from templates.base_template import BaseView


class CurrentAudio(BaseView):
    def __init__(self, main_app):
        super().__init__(main_app)

        self.duration: int = 0
        self.start_: int = 0
        self.end_: int = 0
        self.current_position: int = 0
        self.config: dict = None
        self.is_playing: bool = False
        self.audio = None

        self.slider: ft.Slider = ft.Slider(
            min = 0,
            thumb_color = "tranparent"
        )

        self.play_button: ft.IconButton = ft.IconButton(icon = ft.icons.PLAY_ARROW_ROUNDED, on_click = self.__play)

        self.update_position: UpdateAction = UpdateAction(interval = 0.1, callback = self.__update_position)

    def __update_position(self):
        if self.update_position.is_running:
            return

        self.update_position.is_running = True
        self.current_position = pygame.mixer.music.get_pos()
        self.update_position.is_running = False
        if self.current_position == -1:
            self.update_position.stop()
            self.play_button.icon = ft.icons.PLAY_ARROW_ROUNDED
            return
        self.start_ = self.current_position / 1000.
        self.slider.value = self.current_position / 1000.


    def __play(self, event: ft.ControlEvent):
        if self.current_position == -1:
            pygame.mixer.music.play(loops=0, start = 0)
            self.is_playing = True
            self.play_button.icon = ft.icons.STOP
            self.update_position.start()
        elif self.is_playing == False:
            if self.start_ == 0:
                pygame.mixer.music.play(loops = 0)
            else:
                pygame.mixer.music.unpause()
            self.play_button.icon = ft.icons.STOP
            self.update_position.start()
            self.is_playing = True
        else:
            pygame.mixer.music.pause()
            self.play_button.icon = ft.icons.PLAY_ARROW_ROUNDED
            self.update_position.stop()
            self.is_playing = False
        event.page.update()


    def go_back(self, event: ft.ControlEvent):
        self.update_position.stop()
        pygame.mixer.music.stop()
        event.page.update()
        event.page.go(MIC_ROUTE)

    def view(self, page: ft.Page, params: Params, basket: Basket) -> ft.View:
        base_view = super().view(page, params, basket)

        self.config = basket.get('current_audio_config')
        pygame.mixer.music.load(self.config["path"])
        self.slider.max = self.config["seconds"]
        self.slider.value = 0
        self.start_ = 0
        self.create_appbar("Nghe audio", icons = [ft.icons.ARROW_LEFT],
                           function_callback = [self.go_back],
                           tooltips = ["Quay trở lại"])
        base_view.controls.append(self.app_bar)
        base_view.controls.append(
            ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.slider,
                    ft.Row(
                        spacing=0,

                        controls=[
                            self.play_button
                        ]
                    )
                ]
            )
        )
        return base_view