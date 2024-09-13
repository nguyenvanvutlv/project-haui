import flet as ft
import flet_route
import assets
from assets import HOME_ROUTE
from base.mainapp import MainApp
from controls.file_controls import FileControls
from controls.home_controls import HomeControls
from controls.settings_controls import SettingsControls
from models.record.record_audio import RecordPyaudio, RecordSpeechRecognition
import pyaudio


def main(page: ft.Page):

    # bộ ghi âm từ pyaudio
    record_pyaudio = RecordPyaudio(format = pyaudio.paInt16, 
                            input = True, frames_per_buffer = 1024)
    record_speech = RecordSpeechRecognition()


    app = MainApp(page, record_pyaudio = record_pyaudio, 
                            record_speech = record_speech)
    
    home_controls = HomeControls(app)
    settings_controls = SettingsControls(app)
    files_controls = FileControls(app)
    app_routes = [
        flet_route.path(url = assets.HOME_ROUTE, clear = True, view = home_controls.view),
        flet_route.path(url = assets.SETTINGS_ROUTE, clear = True, view = settings_controls.view),
        flet_route.path(url = assets.FILES_ROUTE, clear = True, view = files_controls.view)
    ]
    flet_route.Routing(
        app_routes = app_routes,
        page = page
    )
    page.go(HOME_ROUTE)
    page.update()

ft.app(main)
