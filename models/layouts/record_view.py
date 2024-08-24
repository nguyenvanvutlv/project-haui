import asyncio

import flet as ft
from flet_route import Params, Basket

import assets
from base_model.base import BaseLayout
from models.main_model.data_record.base import ListRecordData, RecordData
from models.layouts.components.record_component import RecordComponent
from models.main_model.model_speechRecognition.AutoSpeechRecognition import AudioModel
from models.main_model.record_audio import Record


class RecordView(BaseLayout):
    list_record: ft.Column = None
    record_component: RecordComponent = None
    # đối tượng ghi âm
    record_object: Record = None


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
        if self.main_app.list_record is None:
            self.main_app.list_record = ListRecordData()

        for index_record in range(len(self.main_app.list_record)):
            self.list_record.controls.append(
                self.create_component(context = "test", icons = ft.icons.DATA_OBJECT,
                                      actions = None, icons_callable = ft.icons.DELETE)
            )
        self.record_component = RecordComponent(title = "Chuyển giọng nói thành văn bản",
                                                actions = [self.start_record],
                                                name_actions = ["Ghi âm"],
                                                callable_cancel = self.end_record
                                                )
        self.record_object = Record().create_object(sample_rate = assets.SAMPLE_RATE,
                                                    energy_threshold = assets.ENERGY_THRESHOLD,
                                                    update_context = self.update_context,
                                                    update_new_context = self.update_new_context,
                                                    record_timeout = assets.RECORD_TIMEOUT)
        return self

    async def new_record(self, event: ft.ControlEvent):
        # thực hiện tải model ngay khi lần đầu chọn
        self.record_component.open_form(event)
        event.page.update()

        await asyncio.sleep(3)
        if self.main_app.audio_model is None:
            self.main_app.audio_model = AudioModel().create_object()
            await self.main_app.audio_model.load_model()
            self.record_object.update_model(self.main_app.audio_model)
            self.record_component.update_content(event)


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

    async def start_record(self, event: ft.ControlEvent) -> None:
        self.record_component.disable_record(event)
        await self.record_object.start_record()

    async def end_record(self, event: ft.ControlEvent) -> None:
        self.record_component.enable_record(event)
        await self.record_object.stop_record()

    def update_context(self, context: str):
        # cập nhật về text hiện tại
        self.record_component.update_context(context)

    def update_new_context(self):
        self.record_component.update_new_context()

    # def close_form_record(self, event: ft.ControlEvent) -> None:
    #     event.control.page.close(self.form_record)
    #     record_data = RecordData().create_object(id = len(self.main_app.list_record), sample_rate = 16000,
    #                              data = None)
    #     self.main_app.list_record.attach(record_data)
    #     self.list_record.controls.append(
    #         self.create_component(context=f"Bản ghi âm {len(self.main_app.list_record)}",
    #                               icons=ft.icons.DATA_OBJECT,
    #                               actions= lambda event, id = record_data.id : self.delete_record(event, id),
    #                               icons_callable = ft.icons.DELETE)
    #     )
    #     event.page.update()

    def view(self, page: ft.Page, params: Params, basket: Basket):
        base_view = super().view(page, params, basket)
        base_view.controls.append(
            ft.Column(
                controls = [
                    self.list_record
                ]
            )
        )
        base_view.controls.append(self.record_component)
        base_view.scroll = ft.ScrollMode.AUTO
        return base_view