from abc import abstractmethod
import flet as ft
from flet_route import Params, Basket
from assets import HOME_ROUTE
from base_model.base import MainApp
from templates.base_template import BaseView



class FileUploadView(BaseView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)
        self.extenstion_file = ["wav", "mp3", "mp4", "m4a", "mkv"]

        self.new_record: ft.IconButton = ft.IconButton(icon = ft.icons.UPLOAD_FILE, tooltip = "Tạo bản ghi âm mới",
                                                       on_click = self.new_record_function)
        self.file_picker: ft.FilePicker = ft.FilePicker(on_result = self.file_picker_result)

    @abstractmethod
    def file_picker_result(self, event: ft.FilePickerResultEvent) -> tuple[str, str] | None:
        if len(event.files) == 0:
            return None

        path_file = event.files[0].path
        size = event.files[0].path

        if path_file.split(".")[-1] not in self.extenstion_file:

            snack_bar = ft.SnackBar(content = ft.Text(
                value = "Tệp không đúng định dạng, vui lòng tải các file có đuôi là {}".format(self.extenstion_file)))
            if len(event.page.overlay) > 0:
                event.page.overlay.clear()
            event.page.overlay.append(snack_bar)
            snack_bar.open = True
            event.page.update()
            return None
        return path_file, size



    @abstractmethod
    def new_record_function(self, event: ft.ControlEvent) -> None:
        self.file_picker.pick_files(allow_multiple = False,
                                    allowed_extensions = self.extenstion_file)

    def view(self, page: ft.Page, params: Params, basket: Basket) -> ft.View:
        base_view = super().view(page, params, basket)
        self.create_appbar(title = "Chuyển giọng nói theo tệp", function_callback = [lambda event : page.go(HOME_ROUTE)],
                           tooltips = ["Quay lại"])
        base_view.controls.append(self.app_bar)
        base_view.controls.append(self.new_record)
        base_view.controls.append(self.file_picker)
        return base_view