import flet as ft
import flet_route
import assets
from assets import HOME_ROUTE
from base.mainapp import MainApp
from controls.file_controls import FileControls
from controls.home_controls import HomeControls
from controls.settings_controls import SettingsControls
from models.record.record_audio import RecordAudio, ModelVad


def main(page: ft.Page):

    record : RecordAudio = RecordAudio()
    model_vad : ModelVad = ModelVad()
    app = MainApp(page, record, model_vad)
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
