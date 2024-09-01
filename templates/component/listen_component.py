import flet as ft
import pygame

class ListenComponent(ft.CupertinoBottomSheet):
    def __init__(self, title: str, function_callback : list[callable], tooltips: list[str]):
        self.config : dict = None
        self.main_function = [
            ft.CupertinoActionSheetAction(
                content = ft.ElevatedButton(tooltip, on_click = function_callback[index]),
                is_default_action = True
            ) for index, tooltip in enumerate(tooltips)
        ]


        super().__init__(content = ft.CupertinoActionSheet(
            title = ft.Text(title),
            message = ft.Text("", size = 32),
            cancel = ft.CupertinoActionSheetAction(
                content = ft.Text("Thoát"),
                on_click = lambda event : self.close_form(event)
            ),
            actions = self.main_function
        ))

    def close_form(self, event: ft.ControlEvent):
        event.page.close(self)
        event.page.update()

    def open_form(self, event: ft.ControlEvent, config):
        self.config = config
        self.content.title.value = self.config["file_name"]
        self.content.message.value = self.config["text"]
        event.page.open(self)
        event.page.update()