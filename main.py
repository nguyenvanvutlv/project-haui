import flet as ft
from flet_route import path, Routing
from assets import HOME_ROUTE, WIDTH, HEIGHT, SETTINGS_ROUTE, FILEUPLOAD_ROUTE, MIC_ROUTE, CURRENT_AUDIO
from base_model.base import MainApp
from views.controller import HomeViewController, FileUploadController, MicController, CurrentAudioController


def main(page: ft.Page):
    app = MainApp(page)
    app.settings_windows()
    homeview = HomeViewController(app)
    fileuploadview = FileUploadController(app)
    micview = MicController(app)
    current_audio = CurrentAudioController(app)
    app_routes = [
        path(url = HOME_ROUTE, clear = True, view = homeview.view),
        path(url = FILEUPLOAD_ROUTE, clear = True, view = fileuploadview.view),
        path(url = MIC_ROUTE, clear = True, view = micview.view),
        path(url = CURRENT_AUDIO, clear = True, view = current_audio.view)
    ]
    Routing(
        page = page,
        app_routes = app_routes
    )
    page.go(HOME_ROUTE)
    page.update()
ft.app(main)