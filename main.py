import flet as ft
import assets
from models.system import App
from flet_route import Routing, path
from templates.controls.home import HomeControls
from templates.controls.playlist import PlayListControls
from templates.controls.record import RecordControls
from templates.view.settings import SettingView
import pygame


def main(page: ft.Page):
    pygame.mixer.init()
    app = App(page)

    homeControls = HomeControls(app)
    playListControls = PlayListControls(app)
    recordControls = RecordControls(app)
    settingsView = SettingView(app)

    app_routes = [
        path(url = assets.HOME_ROUTE, clear = True, 
             view = homeControls.view),
        path(url = assets.PLAYLIST_ROUTE, clear = True,
            view = playListControls.view),
        path(url = assets.RECORD_ROUTE, clear = True,
            view = recordControls.view),
        path(url = assets.SETTING_ROUTE, clear = True,
            view = settingsView.view)
    ]
    Routing(
        app_routes = app_routes,
        page = page
    )
    page.go(assets.HOME_ROUTE)
    page.update()

ft.app(main)