import flet as ft
from flet_route import Params, Basket

from base_model.base import MainApp
from models.update_action import UpdateAction
from templates.current_audio import CurrentAudio
from templates.fileupload_template import FileUploadView
from templates.home_template import HomeView
from templates.mic_template import MicView
from pydub import AudioSegment


class HomeViewController(HomeView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)


class FileUploadController(FileUploadView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)


    def file_picker_result(self, event: ft.FilePickerResultEvent) -> tuple[str, str] | None:
        result = super().file_picker_result(event)
        if result is None:
            return

        path_file, size = result
        audio = AudioSegment.from_file(path_file)
        audio = audio.set_frame_rate(self.main_app.config["sample_rate"]).set_channels(1)


class MicController(MicView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)

        self.update_model: UpdateAction = UpdateAction(interval = 1.02, callback = self.callback_check)
        self.update_model.start()

    def callback_check(self):
        self.record_component.update_action(self.main_app.record is not None and \
                                            self.main_app.models.models is not None)
        if self.main_app.models.models is not None:
            self.main_app.record.models = self.main_app.models
        self.main_app.page.update()

    async def new_record_function(self, event: ft.ControlEvent):
        await super().new_record_function(event)


class CurrentAudioController(CurrentAudio):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)