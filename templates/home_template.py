import flet as ft
from flet_route import Params, Basket

from assets import SETTINGS_ROUTE, MIC_ROUTE, FILEUPLOAD_ROUTE
from templates.base_template import BaseView
from templates.component.conponent_home_template import HomeComponent


class HomeView(BaseView):
    def __init__(self, main_app):
        super().__init__(main_app)

    def view(self, page: ft.Page, params: Params, basket: Basket) -> ft.View:
        base_view = super().view(page, params, basket)
        self.context = ft.Column(
            controls = [
                HomeComponent(title = "Ghi Âm", icons = [ft.icons.MIC],
                              functions = [lambda event : page.go(MIC_ROUTE)],
                              tooltips = ["Xem ghi âm"]),
                HomeComponent(title = "Tải tệp", icons = [ft.icons.FILE_UPLOAD],
                              functions = [lambda event : page.go(FILEUPLOAD_ROUTE)],
                              tooltips = ["Thực hiện trên file"])
            ]
        )
        self.create_appbar(title = "Trang chủ",
                        icons = [],
                        function_callback = [],
                        tooltips = [])
        base_view.controls.append(self.app_bar)
        base_view.controls.append(self.context)
        return base_view