import flet as ft
from base.view import BaseView
from base.system import MainApp
from flet_route import Params, Basket
from templates.component.function import HomeComponent
from assets import HOME_ROUTE, RECORD_ROUTE, SETTING_ROUTE,FILE_ROUTE, PLAYLIST_ROUTE

class HomeView(BaseView):
    def __init__(self, main_app : MainApp):
        super(HomeView, self).__init__(main_app)
        self.app_bar = self.app_bars(title = "Trang chủ",
                                     function_callbacks = [
                                         lambda event : self.main_app.on_route_change(event, PLAYLIST_ROUTE),
                                         lambda event : self.main_app.on_route_change(event, SETTING_ROUTE)
                                     ],
                                     icons = [
                                         ft.icons.LIST,
                                         ft.icons.SETTINGS
                                     ],
                                     tooltips = [
                                         "Danh sách âm thanh",
                                         "Cài đặt"
                                     ])
        self.content.controls = [
            HomeComponent(title = "Ghi âm", 
                          callback = lambda event : self.main_app.on_route_change(event, RECORD_ROUTE),
                          tooltip = "Ghi âm", 
                          icons=ft.icons.MIC),
            HomeComponent(title = "Tải tệp", 
                          callback = lambda event : self.main_app.on_route_change(event, FILE_ROUTE), tooltip = "Tải tệp"
                          , icons=ft.icons.FILE_COPY),
        ]

    def view(self, page: ft.Page, params: Params, basket: Basket) -> ft.View:
        baseview = super().view(page, params, basket)

        return baseview