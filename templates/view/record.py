from base.view import BaseView
from base.system import MainApp
from base import UpdateAction
import flet as ft
from flet_route import Params, Basket
from assets import HOME_ROUTE
from abc import abstractmethod


class RecordView(BaseView):
    def __init__(self, main_app : MainApp):
        super(RecordView, self).__init__(main_app)

        self.is_recording = False

        self.textField = ft.TextField(multiline = True,
                                      autofocus=True,
                                      border = ft.InputBorder.NONE,
                                      min_lines=40,
                                      content_padding=30,
                                      text_size = 20,
                                      cursor_color='black')
        
    
        self.button_start = ft.CupertinoActionSheetAction(
            content = ft.Text("Bắt đầu ghi âm"),
            on_click = self.start_record,
        )
        self.button_stop = ft.CupertinoActionSheetAction(
            content = ft.Text("Dừng ghi âm"),
            on_click = self.stop_record,
            disabled=True,
        )

        self.action_sheet = ft.CupertinoActionSheet(
            title=ft.Row([ft.Text("Chức năng")], alignment=ft.MainAxisAlignment.CENTER),
            cancel=ft.CupertinoActionSheetAction(
                content=ft.Text("Thoát"),
                on_click=self.close,
            ),
            actions=[
                self.button_start,
                self.button_stop
            ],
        )

        self.bottom_sheet = ft.CupertinoBottomSheet(
            self.action_sheet,
            on_dismiss=self.close)
        
        self.app_bar = self.app_bars(title = "Ghi âm trực tiếp", 
                                     function_callbacks = [
                                         lambda event : self.save_audio(event),
                                         lambda event : self.main_app.page.open(self.bottom_sheet),
                                         lambda event : self.main_app.on_route_change(event, HOME_ROUTE)
                                     ],
                                     icons = [
                                         ft.icons.SAVE,
                                         ft.icons.MIC,
                                         ft.icons.ARROW_LEFT
                                     ],
                                     tooltips = [
                                         "Lưu đoạn âm thanh",
                                         "Thực hiện ghi âm",
                                         "Quay lại"
                                     ])
        self.dislay_seconds = ft.ElevatedButton(text = "Thời gian: 0s")
        self.app_bar.actions.insert(0, self.dislay_seconds)
        self.update_second = UpdateAction(interval = 1, callback = self.update_seconds)

    def update_seconds(self, **kwargs):
        audio_np = self.main_app.record_audio.get_data
        seconds = len(audio_np) / self.main_app.record_audio.record_data.sample_rate
        self.dislay_seconds.text = f"Thời gian: {int(seconds)}s"
        self.main_app.page.update()
        
    @abstractmethod
    async def start_record(self, event: ft.ControlEvent):
        self.is_recording = True
        self.dislay_seconds.text = "Thời gian: 0s"
        self.update_second.start()
        self.button_start.disabled = True
        self.button_stop.disabled = False
        event.page.update()
        self.close(event)

    @abstractmethod
    async def stop_record(self, event: ft.ControlEvent):
        self.is_recording = False
        self.update_second.stop()
        self.button_start.disabled = False
        self.button_stop.disabled = True
        event.page.update()
        self.close(event)

    def close(self, event: ft.ControlEvent):
        self.main_app.page.close(self.bottom_sheet)


    @abstractmethod
    def save_audio(self, event : ft.ControlEvent):
        if len(self.main_app.page.overlay) > 0:
            self.main_app.page.overlay.clear()
        if self.is_recording:

            snack_bar = ft.SnackBar(
                content = ft.Text("Đang ghi âm, vui lòng dừng ghi âm trước khi lưu")
            )
            self.main_app.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.main_app.page.update()
            return
        
        snack_bar = ft.SnackBar(
            content = ft.Text("Lưu thành công")
        )
        return snack_bar



    def view(self, page : ft.Page, params : Params, basket: Basket) -> ft.View:
        base_view = super(RecordView, self).view(page, params, basket)
        base_view.controls.append(self.textField)
        base_view.scroll = ft.ScrollMode.AUTO
        return base_view