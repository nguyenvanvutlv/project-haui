import flet as ft
from base.view import BaseView
from base.system import MainApp
from flet_route import Params, Basket
from templates.component.function import HomeComponent

class HomeView(BaseView):
    def __init__(self, main_app : MainApp):
        super(HomeView, self).__init__(main_app)
        self.app_bar = self.app_bars(title = "Trang chủ",
                                     function_callbacks = [
                                         None
                                     ],
                                     icons = [
                                         ft.icons.SETTINGS
                                     ],
                                     tooltips = [
                                         "Cài đặt"
                                     ])
        self.content.controls = [
            HomeComponent(title = "Ghi âm", callback = None, tooltip = "Ghi âm", 
                          icons=ft.icons.MIC),
            HomeComponent(title = "Tải tệp", callback = None, tooltip = "Tải tệp"
                          , icons=ft.icons.FILE_COPY),
        ]

    def view(self, page: ft.Page, params: Params, basket: Basket) -> ft.View:
        baseview = super().view(page, params, basket)

        return baseview