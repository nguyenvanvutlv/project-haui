import flet as ft
from flet_route import Params, Basket


class BaseView(object):
    def __init__(self, main_app):
        self.main_app = main_app
        self.app_bar: ft.AppBar = None
        self.context: ft.Column = None

    def create_appbar(self, title: str, icons: list = [], function_callback: list = [],
                      tooltips : list = []):
        self.app_bar = ft.AppBar(
            title = ft.Text(title),
            actions = [
                ft.IconButton(icon = icon, on_click = function_callback[index], tooltip = tooltips[index])\
                                    for index, icon in enumerate(icons)
            ]
        )


    def view(self, page: ft.Page, params: Params, basket: Basket) -> ft.View:
        base_view = ft.View(
            route = page.route
        )
        return base_view
