import flet as ft
import assets
from base_model.base import MainApp
from flet_route import path, Routing

from models.layouts.fileupload_view import FileLoadView
from models.layouts.home_view import HomeView
from models.layouts.record_view import RecordView


def main(page: ft.Page):
    main_app: MainApp = MainApp().create_object(page = page)
    main_app.settings_windows(assets.WIDTH, assets.HEIGHT)
    home_view = HomeView().create_object(main_app = main_app)
    record_view = RecordView().create_object(main_app = main_app)
    fileupdate_view = FileLoadView().create_object(main_app = main_app)
    app_routes = [
        path(url = assets.HOME_ROUTE, clear = True, view = home_view.view),
        path(url = assets.RECORD_ROUTE, clear = True, view = record_view.view),
        path(url = assets.FILE_UPLOAD, clear = True, view = fileupdate_view.view)
    ]
    Routing(
        page = page,
        app_routes = app_routes
    )
    page.go(page.route)

ft.app(main)
