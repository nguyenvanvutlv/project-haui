import flet as ft
from typing import List, Callable


class RecordComponent(ft.CupertinoBottomSheet):
    def __init__(
            self,
            title: str,
            actions: List[Callable] = [],
            name_actions: List[str] = [],
            cancel: str = "Thoát",
            callable_cancel: Callable = None
    ):
        super().__init__()
        self.message = ft.Text("1")
        self.lines = [""]
        self.callable_cancel = callable_cancel

        self.preaction = [ft.CupertinoActionSheetAction(
            content=ft.ElevatedButton(name_actions[index], on_click=action),
            is_default_action=True,
            on_click=action
        ) for index, action in enumerate(actions)]


        self.action_sheet = ft.CupertinoActionSheet(
            title=ft.Text(title),
            message = self.message,
            cancel=ft.CupertinoActionSheetAction(
                content=ft.Text(cancel),
                on_click = self.close_form,
            ),
            actions=[
                ft.CupertinoActionSheetAction(
                    content = ft.Column(
                            [ft.ProgressRing(), ft.Text("Đang tải mô hình...")],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    is_default_action = True
                )
            ],
        )
        self.content = self.action_sheet  # Directly assign the action sheet to content

    async def close_form(self, event: ft.ControlEvent) -> None:
        event.page.close(self)
        if self.callable_cancel:
            await self.callable_cancel(event)
        event.page.update()

    def open_form(self, event: ft.ControlEvent) -> None:
        event.page.open(self)
        event.page.update()

    def update_content(self, event: ft.ControlEvent):
        self.content.actions = self.preaction
        event.page.update()

    def disable_record(self, event: ft.ControlEvent) -> None:
        self.preaction[0].content.disabled = True
        event.page.update()

    def enable_record(self, event: ft.ControlEvent) -> None:
        self.preaction[0].content.disabled = False
        event.page.update()

    def update_context(self, context):
        self.lines[-1] = context
        self.message.value = "\n".join(self.lines)
        self.message.update()

    def update_new_context(self):
        self.lines.append("")