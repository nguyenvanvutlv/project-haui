import flet as ft
from flet_route import Params, Basket   
from base.system import MainApp
from templates.view.playlist import PlayList


class PlayListControls(PlayList):
    def __init__(self, main_app: MainApp):
        super(PlayListControls, self).__init__(main_app)