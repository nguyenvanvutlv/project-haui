import flet as ft
from flet_route import Basket, Params
from flet_runtime import Page, View
from base.system import MainApp
from base.view import BaseView
from assets import HOME_ROUTE
from abc import abstractmethod

class FileView(BaseView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)

        self.textField = ft.TextField(multiline = True,
                                      autofocus=True,
                                      border = ft.InputBorder.NONE,
                                      min_lines=40,
                                      content_padding=30,
                                      text_size = 20,
                                      cursor_color='black')
        self.final_text = []
        self.current_file = None
        self.current_audio = None

        self.app_bar = self.app_bars(
            title = "Tải tệp",
            function_callbacks = [
                lambda event : self.save_file(event),
                lambda event : self.open_file(event),
                lambda event : self.main_app.on_route_change(event, HOME_ROUTE)
            ],
            icons = [
                ft.icons.UPLOAD_FILE,
                ft.icons.FILE_UPLOAD,
                ft.icons.ARROW_LEFT
            ],
            tooltips = [
                "Lưu tệp",
                "Tải Tệp",
                "Quay lại"
            ]
        )

        self.file_dialog = ft.FilePicker(on_result=self.on_file_result)

    @abstractmethod
    async def on_file_result(self, event : ft.FilePickerResultEvent):      
        pass


    def open_file(self, event : ft.ControlEvent):
        self.file_dialog.pick_files(
            allow_multiple = False,
            allowed_extensions = ['mp4', 'mkv', 'mp3', 'wav', 'flac', 'ogg']
        )

    @abstractmethod
    def save_file(self, event : ft.ControlEvent):
        pass

    @abstractmethod
    async def run_file(self, event : ft.ControlEvent):
        pass


    def view(self, page: Page, params: Params, basket: Basket) -> View:
        base_view = super().view(page, params, basket)
        base_view.controls.append(self.textField)
        base_view.controls.append(self.file_dialog)
        return base_view