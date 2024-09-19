import flet as ft
import assets
import json
from base.system import MainApp


class App(MainApp):
    def __init__(self, page: ft.Page):
        settings = json.load(open(assets.SETTINGS_JSON, "r", 
                                encoding = 'utf-8'))
        super(App, self).__init__(page, 
            playlist = settings['audios'])


