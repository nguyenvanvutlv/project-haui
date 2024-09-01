import flet as ft

class RecordComponent(ft.CupertinoBottomSheet):
    def __init__(self, title: str, function_callback : list[callable], tooltips: list[str]):
        self.message = ft.Text(value = "", weight = ft.FontWeight.BOLD)
        self.line = [""]
        self.loading = ft.CupertinoActionSheetAction(
            content=ft.Column(
                [ft.ProgressRing(), ft.Text("Đang tải mô hình...")],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            is_default_action=True
        )


        self.main_function = [
            ft.CupertinoActionSheetAction(
                content = ft.ElevatedButton(tooltip, on_click = function_callback[index]),
                is_default_action = True
            ) for index, tooltip in enumerate(tooltips)
        ]


        super().__init__(content = ft.CupertinoActionSheet(
            title = ft.Text(title),
            message = self.message,
            cancel = ft.CupertinoActionSheetAction(
                content = ft.Text("Thoát"),
                on_click = lambda event : self.close_form(event)
            ),
            actions = [
                self.loading
            ]
        ))
    def update_action(self, status: bool = False):
        if status:
            self.content.actions = self.main_function
        else:
            self.content.actions = [self.loading]

    def close_form(self, event: ft.ControlEvent):
        event.page.close(self)
        event.page.update()

    def open_form(self, event: ft.ControlEvent):
        event.page.open(self)
        event.page.update()

    def update_button_record(self, event: ft.ControlEvent, status):
        self.content.actions[0].content.disabled = status
        self.content.actions[1].content.disabled = not status
        event.page.update()