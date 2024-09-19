import flet as ft
from flet_route import Params, Basket
from base.view import BaseView
from base.system import MainApp
import assets
from abc import abstractmethod

class PlayList(BaseView):
    def __init__(self, main_app: MainApp):
        super(PlayList, self).__init__(main_app)
        self.app_bar = self.app_bars(
            title = "Danh sách âm thanh",
            function_callbacks = [
                lambda event : self.main_app.on_route_change(event, assets.HOME_ROUTE)
            ],
            icons = [
                ft.icons.ARROW_LEFT
            ],
            tooltips = [
                "Quay lại"
            ]
        )

    @abstractmethod
    def listen_audio(self, event: ft.ControlEvent):
        pass

    def view(self, page : ft.Page, params: Params, basket: Basket) -> ft.View:
        base_view = super().view(page, params, basket)


        self.content.controls.clear()

        for index in range(len(self.main_app.audios)):

            self.content.controls.append(
                ft.ExpansionTile(
                            title=ft.Text(self.main_app.audios[index].audio_data.name),
                            affinity=ft.TileAffinity.PLATFORM,
                            maintain_state=True,
                            collapsed_text_color=ft.colors.RED,
                            text_color=ft.colors.RED,
                            controls=[
                                ft.ListTile(title=ft.Text(self.main_app.audios[index].audio_data.text)),
                                ft.ElevatedButton(text = "Nghe", on_click = self.listen_audio, data = index, key = index)
                            ],
                )
            )


        return base_view