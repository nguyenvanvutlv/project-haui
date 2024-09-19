import flet as ft
import assets
from models.system import App
from flet_route import Routing, path


from templates.controls.home import HomeControls
from templates.controls.playlist import PlayListControls


def main(page: ft.Page):
    app = App(page)

    homeControls = HomeControls(app)
    playListControls = PlayListControls(app)

    app_routes = [
        path(url = assets.HOME_ROUTE, clear = True, 
             view = homeControls.view),
        path(url = assets.PLAYLIST_ROUTE, clear = True,
            view = playListControls.view)   
    ]
    Routing(
        app_routes = app_routes,
        page = page
    )
    page.go(assets.HOME_ROUTE)
    page.update()

ft.app(main)