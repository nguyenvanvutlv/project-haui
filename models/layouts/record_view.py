import flet as ft
from flet_route import Params, Basket

import assets
from base_model.base import BaseLayout
from models.main_model.data_record.base import ListRecordData, RecordData
from models.layouts.components.record_component import FormRecord


class RecordView(BaseLayout):
    list_record: ft.Column = None
    action_sheet: ft.CupertinoActionSheet = None
    form_record: ft.CupertinoBottomSheet = None


    def create_object(self, **kwargs):
        super().create_object(title = "Ghi âm",
                              icons = [ft.icons.PLAY_CIRCLE_FILL, ft.icons.ARROW_RIGHT],
                              tooltips = ["Tạo mới", "Thoát"],
                              func = [
                                  self.new_record,
                                  lambda event : self.main_app.page.go(
                                      assets.HOME_ROUTE)
                              ],
                              **kwargs)
        self.list_record = ft.Column()
        self.action_sheet = ft.CupertinoActionSheet(
            title=ft.Text("Chuyển giọng nói thành văn bản"),
            # message=ft.Text("Message"),
            cancel=ft.CupertinoActionSheetAction(
                content=ft.Text("Thoát"),
                on_click=self.close_form_record,
            ),
            actions=[
                ft.CupertinoActionSheetAction(
                    content=ft.ElevatedButton("Ghi âm"),
                    is_default_action=True,
                    on_click=lambda e: print("Ghi âm"),
                ),
            ],
        )
        self.form_record = ft.CupertinoBottomSheet(self.action_sheet)

        if self.main_app.list_record is None:
            self.main_app.list_record = ListRecordData()

        for index_record in range(len(self.main_app.list_record)):
            self.list_record.controls.append(
                self.create_component(context = "test", icons = ft.icons.DATA_OBJECT,
                                      actions = None, icons_callable = ft.icons.DELETE)
            )
        return self

    def new_record(self, event: ft.ControlEvent):
        self.open_form_record(event)
        event.page.update()


    def delete_record(self, event: ft.ControlEvent, id: int) -> None:
        for index, value in enumerate(self.list_record.controls):
            if self.main_app.list_record[index].id == id:
                self.main_app.list_record.detach(index)
                self.list_record.controls.pop(index)
                break
        event.page.update()

    def create_component(self, context: str, icons: str,
                         actions: callable, icons_callable: str) -> ft.Stack:
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
                    icon=icons_callable,
                    right=5,
                    top=0,
                    on_click = actions
                ),
            ]
        )

    def open_form_record(self, event: ft.ControlEvent) -> None:
        event.control.page.open(self.form_record)

    def close_form_record(self, event: ft.ControlEvent) -> None:
        event.control.page.close(self.form_record)
        record_data = RecordData().create_object(id = len(self.main_app.list_record), sample_rate = 16000,
                                 data = None)
        self.main_app.list_record.attach(record_data)
        self.list_record.controls.append(
            self.create_component(context=f"Bản ghi âm {len(self.main_app.list_record)}",
                                  icons=ft.icons.DATA_OBJECT,
                                  actions= lambda event, id = record_data.id : self.delete_record(event, id),
                                  icons_callable = ft.icons.DELETE)
        )
        event.page.update()

    def view(self, page: ft.Page, params: Params, basket: Basket):
        base_view = super().view(page, params, basket)
        base_view.controls.append(
            ft.Column(
                controls = [
                    self.list_record
                ]
            )
        )
        base_view.controls.append(self.form_record)
        base_view.scroll = ft.ScrollMode.AUTO
        return base_view