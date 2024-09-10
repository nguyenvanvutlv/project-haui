from abc import abstractmethod

import flet as ft
from flet_route import Params, Basket

from assets import SETTINGS_ROUTE, FILES_ROUTE
from base.mainapp import MainApp
from view import BaseView
from view.home.home_component import HomeComponent


class HomeView(BaseView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)
        self.app_bar = self.app_bars(title = "Trang chủ",
                        function_callbacks = [
                            lambda event : self.main_app.page.go(FILES_ROUTE),
                            lambda event : self.main_app.page.go(SETTINGS_ROUTE)
                        ],
                        icons = [ft.icons.FILE_PRESENT, ft.icons.SETTINGS], tooltips = ['Danh sách tệp', 'Cài đặt'])
        self.content.controls = [
            HomeComponent(title = "Thu âm", callback = self.open_form_record, tooltip = "Ghi âm trực tiếp",
                          icons = ft.icons.MIC),
            HomeComponent(title = "Tải tệp", callback = self.file_upload, tooltip = "Thực hiện trên tệp",
                          icons = ft.icons.FILE_UPLOAD)
        ]

        self.pick_files = ft.FilePicker(on_result = self.pick_files_result)

        self.line = []
        self.message = ft.Text("", size = 25)
        self.is_record: bool = False

        self.action_record = ft.CupertinoActionSheetAction(
                    content = ft.IconButton(icon = ft.icons.CIRCLE, icon_size = 50, splash_radius = 5,
                                on_click = self.record),
                    is_default_action=True,
        )

        self.action_sheet = ft.CupertinoActionSheet(
            title=ft.Row([ft.Text("Ghi âm", size = 25)], alignment=ft.MainAxisAlignment.CENTER),
            message=ft.Row([self.message], alignment=ft.MainAxisAlignment.CENTER),
            cancel=ft.CupertinoActionSheetAction(
                content=ft.Text("Thoát"),
                on_click = self.close_form_record
            ),
            actions=[
                self.action_record
            ],
        )
        self.bottom_sheet = ft.CupertinoBottomSheet(self.action_sheet,
                                on_dismiss=lambda event : print(event))
        self.current_method: str = "mic"

    @abstractmethod
    def pick_files_result(self, event: ft.FilePickerResultEvent):
        if event.files is None:
            return
        return event.files[0]

    def open_form_record(self, event: ft.ControlEvent):
        event.page.open(self.bottom_sheet)
        event.page.update()

    def close_form_record(self, event: ft.ControlEvent):
        event.page.close(self.bottom_sheet)
        event.page.update()

    @abstractmethod
    async def record(self, event: ft.ControlEvent) -> bool:
        pass

    def file_upload(self, event: ft.ControlEvent):
        # kiểm tra xem mô hình đã được load hay chưa
        if not self.main_app.is_loaded:
            snack_bar = ft.SnackBar(content = ft.Text("Vui lòng tải mô hình trước"))
            if len(event.page.overlay):
                event.page.overlay.clear()
            event.page.overlay.append(snack_bar)
            snack_bar.open = True
            event.page.update()
            return
        self.pick_files.pick_files(allow_multiple=False, file_type = ft.FilePickerFileType.AUDIO,
                        allowed_extensions = ["mp3", "wav", "mp4", "m4a", "mkv"])

    def view(self, page: ft.Page, params: Params, basket: Basket) -> ft.View:
        base_view = super().view(page, params, basket)
        base_view.controls.append(self.bottom_sheet)
        base_view.controls.append(self.pick_files)
        base_view.scroll = ft.ScrollMode.AUTO
        return base_view