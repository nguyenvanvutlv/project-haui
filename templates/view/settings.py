import flet as ft
from flet_route import Basket, Params
from flet_runtime import Page, View
from base.system import MainApp
from base.view import BaseView
from templates.component.function import SettingsComponent
import assets

class SettingView(BaseView):
    def __init__(self, main_app: MainApp):
        super(SettingView, self).__init__(main_app)

        self.app_bar = self.app_bars(
            title = "Cài đặt",
            function_callbacks = [
                lambda event : self.main_app.on_route_change(event, assets.HOME_ROUTE)
            ],
            icons = [
                ft.icons.ARROW_LEFT
            ],
            tooltips = [
                "Quay lại"
            ]
        )
        self.load_model = SettingsComponent("Tải mô hình", self.on_change_load_model)

    async def on_change_load_model(self, status):
        if status and not self.main_app.whispers.is_loaded:
            snackbar = ft.SnackBar(
                content = ft.Text("Đang tải mô hình")
            )
            if len(self.main_app.page.overlay) != 0:
                self.main_app.page.overlay.clear()
            self.main_app.page.overlay.append(snackbar)
            snackbar.open = True
            self.main_app.page.update()
            await self.main_app.whispers.load_model()
            await self.main_app.vads.load_model()
            snackbar = ft.SnackBar(
                content =  ft.Text("Tải mô hình thành công")
            )
            if len(self.main_app.page.overlay) != 0:
                self.main_app.page.overlay.clear()
            self.main_app.page.overlay.append(snackbar)
            snackbar.open = True
            self.main_app.page.update()


    def view(self, page: Page, params: Params, basket: Basket) -> View:
        base_view = super().view(page, params, basket)
        base_view.controls.append(self.load_model)
        base_view.scroll = ft.ScrollMode.AUTO
        return base_view