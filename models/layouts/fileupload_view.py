import flet as ft
from flet_route import Params, Basket

import assets
from base_model.base import BaseLayout


class FileLoadView(BaseLayout):

    def create_object(self, **kwargs):
        super().create_object(title = "Tải tệp", icons = [ft.icons.ARROW_RIGHT],
                              tooltips = ["Thoát"],
                              func = [
                                  lambda event : self.main_app.page.go(
                                      assets.HOME_ROUTE)
                              ],
                              **kwargs)
        return self

    def view(self, page: ft.Page, params: Params, basket: Basket):
        base_view = super().view(page, params, basket)
        return base_view