import flet as ft
from abc import abstractmethod
from flet_route import Params, Basket
from base.system import MainApp

class BaseView(object):
    def __init__(self, main_app: MainApp):
        self.list_routes : list[str] = []
        self.main_app = main_app
        self.content : ft.Column = ft.Column()
        self.app_bar = self.app_bars("Trang chủ", function_callbacks = [None],
                                     icons = [ft.icons.SETTINGS], tooltips = ["Cài đặt"])


    @abstractmethod
    def view(self, page: ft.Page, params: Params, basket: Basket) -> ft.View:
        base_view = ft.View(route = page.route,
                            controls = [
                                self.app_bar,
                                self.content
                            ])
        return base_view

    def app_bars(self, title : str, function_callbacks: list[callable],
                 icons : list[str], tooltips: list[str]):
        app_bar = ft.AppBar(
            title = ft.Text(value = title),
            actions = [
                ft.IconButton(icon = icon,
                              tooltip = tooltips[index],
                              on_click = function_callbacks[index])

                for index, icon in enumerate(icons)
            ]
        )
        return app_bar