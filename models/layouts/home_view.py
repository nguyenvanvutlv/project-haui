from abc import abstractmethod

import flet as ft
from flet_route import Params, Basket

import assets
from base_model.base import Model, BaseLayout


class HomeView(BaseLayout):

    record_view: ft.Stack = None
    file_upload: ft.Stack = None

    def create_object(self, **kwargs):
        super().create_object(title = "Trang chủ", icons = [], tooltips = [],
                              func = [],
                              **kwargs)
        self.record_view = self.create_component(
            context = "Ghi âm", icons = ft.icons.MIC,
            actions = lambda event : self.main_app.page.go(assets.RECORD_ROUTE)
        )
        self.file_upload = self.create_component(
            context = "Tải tệp", icons = ft.icons.FILE_UPLOAD,
            actions = lambda event : self.main_app.page.go(assets.FILE_UPLOAD)
        )
        return self

    def create_component(self, context: str, icons: str,
                         actions: callable) -> ft.Stack:
        return ft.Stack(
            controls = [
                ft.Container(
                    height = 40,
                    border_radius = 10,
                    border = ft.Border(
                        top = ft.BorderSide(width=1),
                        bottom = ft.BorderSide(width=1),
                        left = ft.BorderSide(width=1),
                        right = ft.BorderSide(width=1)
                    )
                ),
                ft.Container(
                    content=ft.Icon(icons, size=20),
                    top=10,
                    left=15
                ),
                ft.Text(
                    max_lines = 1,
                    overflow = ft.TextOverflow.CLIP,
                    top = 5,
                    left = 60,
                    value = context,
                    size = 20
                ),
                ft.Container(
                    height = 40,
                    border_radius = 10
                ),
                ft.IconButton(
                    icon=ft.icons.VIEW_IN_AR,
                    right=5,
                    top=0,
                    on_click = actions
                ),
            ]
        )

    @abstractmethod
    def view(self, page: ft.Page, params: Params, basket: Basket) -> ft.View:
        base_view = super().view(page, params, basket)
        base_view.controls.append(
            ft.Column(
                controls=[
                    self.record_view,
                    self.file_upload
                ]
            )
        )
        return base_view