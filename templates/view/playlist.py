import flet as ft
from flet_route import Params, Basket
from base.view import BaseView
from base.system import MainApp


class PlayList(BaseView):
    def __init__(self, main_app: MainApp):
        super(PlayList, self).__init__(main_app)
        

    def view(self, page : ft.Page, params: Params, basket: Basket) -> ft.View:
        return super().view(page, params, basket)