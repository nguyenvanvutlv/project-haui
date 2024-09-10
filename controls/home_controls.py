import soundfile

import assets
from assets import FILES_ROUTE
from base.data import Audio
from base.mainapp import MainApp
from models import UpdateAction
from models.record.read_file import read_audio
from view.home.home_view import HomeView
import flet as ft

class HomeControls(HomeView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)
        self.update_action = UpdateAction(interval=1.02, callback = self.update_action_callback)
        self.is_running : bool = False


    async def record(self, event : ft.ControlEvent):
        if self.is_running:
            return

        self.is_running = True

        self.is_record = not self.is_record
        self.action_record.content.icon = ft.icons.PAUSE_CIRCLE if self.is_record\
            else ft.icons.CIRCLE
        event.page.update()

        if self.is_record:
            await self.main_app.record.start_record(self.main_app.global_settings.sample_rate,
                                              self.main_app.global_settings.channels)
            self.update_action.start()
        else:
            await self.main_app.record.end_record()
            self.update_action.stop()

            path = f"assets/audios/{len(self.main_app.audios) + 1}.wav"
            audio_data =  Audio(id = len(self.main_app.audios), path = path,
                                sample_rate=self.main_app.global_settings.sample_rate,
                                channels = self.main_app.global_settings.channels)
            self.main_app.audios.attach(audio_data)
            self.main_app.audios.save(assets.DATABASE_JSON)
            self.main_app.record.save_record(path, self.main_app.global_settings.sample_rate)

        self.is_running = False

    def update_action_callback(self):
        print(self.main_app.record.get_numpy())

    def pick_files_result(self, event: ft.FilePickerResultEvent):
        files = super().pick_files_result(event)
        if files is None:
            return

        path = files.path
        size = files.size

        audio_np = read_audio(path, sample_rate=self.main_app.global_settings.sample_rate,
                                channel = self.main_app.global_settings.channels)
        soundfile.write(f"assets/audios/{len(self.main_app.audios) + 1}.wav", audio_np,
                        samplerate=self.main_app.global_settings.sample_rate)
        audio_data = Audio(id = len(self.main_app.audios), path = f"assets/audios/{len(self.main_app.audios) + 1}.wav",
                            sample_rate=self.main_app.global_settings.sample_rate,
                            channels = self.main_app.global_settings.channels)
        self.main_app.audios.attach(audio_data)
        self.main_app.audios.save(assets.DATABASE_JSON)


        event.page.go(FILES_ROUTE)
















